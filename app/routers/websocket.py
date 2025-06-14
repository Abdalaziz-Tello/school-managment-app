from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..core.websocket import manager
from ..core.auth import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from ..models.models import User, BusRecord
from datetime import datetime

router = APIRouter()

@router.websocket("/ws/bus-mentor/{bus_mentor_id}")
async def bus_mentor_websocket(
    websocket: WebSocket,
    bus_mentor_id: int,
    db: Session = Depends(get_db)
):
    await manager.connect(websocket, "bus_mentors")
    try:
        while True:
            data = await websocket.receive_json()
            # Update bus location in database
            bus_record = BusRecord(
                bus_mentor_id=bus_mentor_id,
                location_lat=data["lat"],
                location_lon=data["lon"],
                timestamp=datetime.utcnow(),
                status="in_transit"
            )
            db.add(bus_record)
            db.commit()
            
            # Broadcast to all parents
            await manager.broadcast_bus_location(
                bus_mentor_id,
                data["lat"],
                data["lon"]
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, "bus_mentors")

@router.websocket("/ws/parent/{parent_id}")
async def parent_websocket(
    websocket: WebSocket,
    parent_id: int,
    db: Session = Depends(get_db)
):
    await manager.connect(websocket, "parents")
    try:
        while True:
            # Keep connection alive and wait for updates
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "parents") 