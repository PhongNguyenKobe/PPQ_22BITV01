import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from schemas.movie_schema import Movie

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

# Đường dẫn file JSON
DATA_FILE = Path("data/movies.json")


# ==========================
# Hàm đọc dữ liệu
# ==========================
def load_movies():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================
# Hàm ghi dữ liệu
# ==========================
def save_movies(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ==========================
# GET tất cả phim
# ==========================
@router.get("/")
def get_movies():
    return load_movies()


# ==========================
# GET phim theo ID
# ==========================
@router.get("/{movie_id}")
def get_movie(movie_id: int):
    movies = load_movies()

    for movie in movies:
        if movie["id"] == movie_id:
            return movie

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )


# ==========================
# POST thêm phim
# ==========================
@router.post("/")
def create_movie(movie: Movie):
    movies = load_movies()

    # Kiểm tra ID đã tồn tại
    for m in movies:
        if m["id"] == movie.id:
            raise HTTPException(
                status_code=400,
                detail="Movie ID already exists"
            )

    movies.append(movie.model_dump())
    save_movies(movies)

    return {
        "message": "Movie created successfully",
        "movie": movie
    }


# ==========================
# PUT cập nhật phim
# ==========================
@router.put("/{movie_id}")
def update_movie(movie_id: int, updated_movie: Movie):
    movies = load_movies()

    for index, movie in enumerate(movies):
        if movie["id"] == movie_id:
            movies[index] = updated_movie.model_dump()
            save_movies(movies)

            return {
                "message": "Movie updated successfully",
                "movie": updated_movie
            }

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )


# ==========================
# DELETE phim
# ==========================
@router.delete("/{movie_id}")
def delete_movie(movie_id: int):
    movies = load_movies()

    for index, movie in enumerate(movies):
        if movie["id"] == movie_id:
            deleted_movie = movies.pop(index)
            save_movies(movies)

            return {
                "message": "Movie deleted successfully",
                "movie": deleted_movie
            }

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )