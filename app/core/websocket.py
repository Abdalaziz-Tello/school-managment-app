from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "bus_mentors": [],
            "parents": []
        }

    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        self.active_connections[client_type].append(websocket)

    def disconnect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].remove(websocket)

    async def broadcast_bus_location(self, bus_mentor_id: int, lat: float, lon: float):
        message = {
            "type": "bus_location",
            "bus_mentor_id": bus_mentor_id,
            "lat": lat,
            "lon": lon
        }
        for connection in self.active_connections["parents"]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection, "parents")

manager = ConnectionManager() 