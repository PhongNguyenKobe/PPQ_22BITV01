from datetime import datetime, timezone, timedelta
import json
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.catalog import Movie, Branch, Showtime, Auditorium
from app.services.gemini import query_gemini_assistant, query_gemini_mood_matcher
from app.schemas.movie import MovieRead, ShowtimeRead
from app.schemas.admin import BranchRead

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    parts: List[Dict[str, str]]  # list of {"text": "message content"}

class AiDiscoveryRequest(BaseModel):
    prompt: str
    history: List[ChatMessage] = Field(default_factory=list)

class AiDiscoveryResponse(BaseModel):
    reply: str
    movies: List[MovieRead]
    branches: List[BranchRead]
    showtimes: List[ShowtimeRead]

class AiMoodRequest(BaseModel):
    prompt: str

class MoodMatchItem(BaseModel):
    movie: MovieRead
    reason: str

class MoodMatchResponse(BaseModel):
    recommendations: List[MoodMatchItem]

def _movie_to_read(movie: Movie) -> MovieRead:
    return MovieRead.model_validate(movie)

def _branch_to_read(branch: Branch) -> BranchRead:
    return BranchRead.model_validate(branch)

def _showtime_to_read(showtime: Showtime) -> ShowtimeRead:
    branch_name = showtime.auditorium.branch.name if showtime.auditorium and showtime.auditorium.branch else ""
    screen_name = showtime.auditorium.name if showtime.auditorium else ""
    return ShowtimeRead(
        id=showtime.id,
        movie_id=showtime.movie_id,
        auditorium_id=showtime.auditorium_id,
        starts_at=showtime.starts_at,
        ends_at=showtime.ends_at,
        status=showtime.status,
        booking_closes_at=showtime.booking_closes_at,
        base_price=showtime.base_price,
        branch_name=branch_name,
        screen_name=screen_name,
    )

@router.post("/query", response_model=AiDiscoveryResponse)
async def query_ai_discovery(
    payload: AiDiscoveryRequest,
    db: AsyncSession = Depends(get_db)
) -> AiDiscoveryResponse:
    # 1. Fetch active movies
    movies_stmt = select(Movie).options(selectinload(Movie.genres)).where(
        or_(
            Movie.status == "NOW_SHOWING",
            Movie.status == "UPCOMING"
        )
    )
    movies_res = await db.execute(movies_stmt)
    movies = list(movies_res.scalars().all())

    # 2. Fetch active branches
    branches_stmt = select(Branch).where(Branch.is_active == True)
    branches_res = await db.execute(branches_stmt)
    branches = list(branches_res.scalars().all())

    # 3. Fetch future open showtimes (limit to next 2 days to optimize performance and prompt size)
    end_time = datetime.now(timezone.utc) + timedelta(days=2)
    showtimes_stmt = select(Showtime).options(
        selectinload(Showtime.movie),
        selectinload(Showtime.auditorium).selectinload(Auditorium.branch)
    ).where(
        Showtime.status == "OPEN",
        Showtime.starts_at > datetime.now(timezone.utc),
        Showtime.starts_at < end_time,
        Showtime.booking_closes_at > datetime.now(timezone.utc)
    ).order_by(Showtime.starts_at.asc())
    showtimes_res = await db.execute(showtimes_stmt)
    showtimes = list(showtimes_res.scalars().all())

    # 4. Format context details for Gemini
    current_time_str = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S (UTC%z)")

    branches_list_str = ""
    for b in branches:
        branches_list_str += f"- ID: {b.id}\n  Tên rạp: {b.name}\n  Thành phố: {b.city}\n  Quận/Huyện: {b.district or 'Không xác định'}\n  Địa chỉ: {b.address_line}\n\n"

    movies_list_str = ""
    for m in movies:
        genres_str = ", ".join([g.name for g in m.genres])
        movies_list_str += f"- ID: {m.id}\n  Tên phim: {m.title}\n  Thể loại: {genres_str}\n  Thời lượng: {m.duration_min} phút\n  Mô tả: {m.description or 'Không có mô tả'}\n  Trạng thái: {m.status}\n\n"

    showtimes_list_str = ""
    for s in showtimes:
        movie_title = s.movie.title if s.movie else "Không rõ"
        branch_name = s.auditorium.branch.name if s.auditorium and s.auditorium.branch else "Không rõ"
        starts_local = s.starts_at.astimezone()
        starts_str = starts_local.strftime("%Y-%m-%d %H:%M")
        showtimes_list_str += f"- ID: {s.id}\n  Phim: {movie_title}\n  Rạp: {branch_name}\n  Phòng chiếu: {s.auditorium.name if s.auditorium else 'Không rõ'}\n  Thời gian chiếu: {starts_str}\n  Giá vé: {int(s.base_price)}đ\n\n"

    # 5. Formulate system instruction
    system_instruction = f"""Bạn là CineAI Assistant - trợ lý ảo đặt vé xem phim thông minh của cụm rạp CineAI.
Nhiệm vụ của bạn là lắng nghe các yêu cầu bằng ngôn ngữ tự nhiên của khách hàng (ví dụ: "tôi muốn xem phim ABC ở quận 1 khoảng 1-4h chiều" hoặc "tối nay có phim hoạt hình gì ở rạp Sala không?"), sau đó tư vấn thân thiện và trả về thông tin rạp, phim, suất chiếu phù hợp.

Thời gian hiện tại của hệ thống (giờ Việt Nam): {current_time_str}.
Hãy luôn so sánh thời gian hiện tại này với thời gian chiếu của các suất chiếu để tránh giới thiệu các suất chiếu đã hoặc sắp diễn ra (trong vòng 5 phút nữa).

Dưới đây là danh sách dữ liệu thực tế đang có trong hệ thống của chúng tôi:

=== DANH SÁCH RẠP CHIẾU (BRANCHES) ===
{branches_list_str}

=== DANH SÁCH PHIM ĐANG CHIẾU & SẮP CHIẾU (MOVIES) ===
{movies_list_str}

=== DANH SÁCH SUẤT CHIẾU HỢP LỆ (SHOWTIMES) ===
{showtimes_list_str}

Hãy tuân thủ các quy tắc sau:
1. Trả lời người dùng bằng tiếng Việt tự nhiên, lịch sự, thân thiện trong trường 'reply'. Tóm tắt ngắn gọn các lựa chọn phù hợp nhất mà bạn tìm thấy.
2. Trích xuất chính xác danh sách UUID:
   - 'movies': Danh sách UUID phim khớp hoặc người dùng đang hỏi đến.
   - 'branches': Danh sách UUID rạp chiếu khớp với địa điểm (Quận, tên rạp...) người dùng chọn. Nếu người dùng nói "Quận 1" hay "Q1", hãy khớp với trường 'Quận/Huyện' hoặc 'Địa chỉ' của các rạp (ví dụ rạp nào ở quận 1 thì đưa ID vào).
   - 'showtimes': Danh sách UUID suất chiếu khớp với phim, rạp và khoảng thời gian người dùng yêu cầu.
3. Sắp xếp danh sách suất chiếu 'showtimes' theo thứ tự thời gian tăng dần (suất chiếu sớm nhất lên trước).
4. Chỉ sử dụng UUID thực tế có trong danh sách dữ liệu được cung cấp ở trên. TUYỆT ĐỐI KHÔNG tự bịa ra UUID không tồn tại.
5. Nếu không tìm thấy suất chiếu nào khớp chính xác với khung giờ hoặc rạp yêu cầu, hãy tìm kiếm các lựa chọn gần nhất (ví dụ: phim đó ở rạp khác gần đó hoặc khung giờ khác) để đề xuất trong 'reply' và đưa các ID đó vào danh sách tương ứng để khách hàng dễ chọn.
6. Nếu người dùng chỉ chào hỏi hoặc nói chuyện ngoài lề không liên quan đến phim ảnh hay đặt vé, hãy trả lời vui vẻ và gợi ý họ đặt câu hỏi về lịch chiếu phim. Để các danh sách 'movies', 'branches', và 'showtimes' là mảng rỗng [].
"""

    # 6. Format chat history and prompt for Gemini
    contents = []
    for msg in payload.history:
        contents.append({
            "role": msg.role,
            "parts": [{"text": p.get("text", "")} for p in msg.parts]
        })
    
    # Append current prompt
    contents.append({
        "role": "user",
        "parts": [{"text": payload.prompt}]
    })

    # 7. Call Gemini service
    gemini_result = await query_gemini_assistant(system_instruction, contents)

    # 8. Retrieve actual objects from database using returned IDs to populate full metadata
    matched_movie_ids = {UUID(mid) for mid in gemini_result.get("movies", []) if mid}
    matched_branch_ids = {UUID(bid) for bid in gemini_result.get("branches", []) if bid}
    matched_showtime_ids = {UUID(sid) for sid in gemini_result.get("showtimes", []) if sid}

    response_movies = [m for m in movies if m.id in matched_movie_ids]
    response_branches = [b for b in branches if b.id in matched_branch_ids]
    
    # Preserve order of showtimes as returned by Gemini (if possible) or starts_at order
    response_showtimes = []
    for sid in gemini_result.get("showtimes", []):
        try:
            suuid = UUID(sid)
            s_obj = next((s for s in showtimes if s.id == suuid), None)
            if s_obj:
                response_showtimes.append(s_obj)
        except ValueError:
            continue

    return AiDiscoveryResponse(
        reply=gemini_result.get("reply", "Tôi có thể giúp gì cho bạn?"),
        movies=[_movie_to_read(m) for m in response_movies],
        branches=[_branch_to_read(b) for b in response_branches],
        showtimes=[_showtime_to_read(s) for s in response_showtimes]
    )

@router.post("/mood-matcher", response_model=MoodMatchResponse)
async def ai_mood_matcher(
    payload: AiMoodRequest,
    db: AsyncSession = Depends(get_db)
) -> MoodMatchResponse:
    # 1. Fetch active movies
    movies_stmt = select(Movie).options(selectinload(Movie.genres)).where(
        or_(
            Movie.status == "NOW_SHOWING",
            Movie.status == "UPCOMING"
        )
    )
    movies_res = await db.execute(movies_stmt)
    movies = list(movies_res.scalars().all())

    # 2. Format context for Gemini
    movies_context = ""
    for m in movies:
        genres_str = ", ".join([g.name for g in m.genres])
        movies_context += f"- ID: {m.id}\n  Tên phim: {m.title}\n  Thể loại: {genres_str}\n  Thời lượng: {m.duration_min} phút\n  Mô tả: {m.description or 'Không có mô tả'}\n\n"

    # 3. Formulate system instruction
    system_instruction = f"""Bạn là CineAI Mood Matcher - chuyên gia tư vấn tâm lý phim ảnh của cụm rạp CineAI.
Nhiệm vụ của bạn là lắng nghe phân tích tâm trạng, hoàn cảnh hoặc mong muốn của người dùng (ví dụ: "buồn chán sau khi thi trượt", "đi chơi với người yêu", "muốn xem phim cười bể bụng").
Đối chiếu với danh sách các bộ phim đang chiếu/sắp chiếu dưới đây và đề xuất chính xác Top 3 bộ phim phù hợp nhất với tâm trạng/hoàn cảnh đó.
Với mỗi phim được gợi ý, hãy viết một đoạn giải thích ngắn gọn, thuyết phục và đầy thấu hiểu bằng tiếng Việt (khoảng 2-3 câu) vì sao phim này là lựa chọn tuyệt vời dành cho họ.

=== DANH SÁCH PHIM ĐANG & SẮP CHIẾU ===
{movies_context}
"""

    # 4. Call Gemini mood matcher service
    gemini_result = await query_gemini_mood_matcher(system_instruction, payload.prompt)

    # 5. Populate response with actual movie models
    recommendations = []
    for rec in gemini_result.get("recommendations", []):
        try:
            muuid = UUID(rec.get("movie_id", ""))
            movie_obj = next((m for m in movies if m.id == muuid), None)
            if movie_obj:
                recommendations.append(MoodMatchItem(
                    movie=_movie_to_read(movie_obj),
                    reason=rec.get("reason", "Phim phù hợp với tâm trạng của bạn.")
                ))
        except ValueError:
            continue

    # Fallback if Gemini failed or didn't return matches
    if not recommendations and movies:
        # Fallback to first 3 movies
        for m in movies[:3]:
            recommendations.append(MoodMatchItem(
                movie=_movie_to_read(m),
                reason="Dựa trên gợi ý của chúng tôi, đây là bộ phim hấp dẫn bạn có thể yêu thích hôm nay."
            ))

    return MoodMatchResponse(recommendations=recommendations)
