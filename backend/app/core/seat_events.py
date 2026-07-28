from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class SeatEventManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, showtime_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[showtime_id].add(websocket)

    def disconnect(self, showtime_id: UUID, websocket: WebSocket) -> None:
        self._connections[showtime_id].discard(websocket)
        if not self._connections[showtime_id]:
            self._connections.pop(showtime_id, None)

    async def broadcast(self, showtime_id: UUID, event: str) -> None:
        stale: list[WebSocket] = []
        for connection in self._connections.get(showtime_id, set()):
            try:
                await connection.send_json({"event": event, "showtime_id": str(showtime_id)})
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(showtime_id, connection)


seat_events = SeatEventManager()
