from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio

from core.config import get_settings
from core.hal import HALFactory


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Starting RPi Car Infotainment Backend (HAL: {settings.hal_mode})")
    
    results = HALFactory.initialize_all()
    print(f"Module initialization results: {results}")
    
    yield
    
    print("Shutting down RPi Car Infotainment Backend...")
    HALFactory.shutdown_all()


app = FastAPI(
    title="RPi Car Infotainment API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "RPi Car Infotainment Backend"}


@app.get("/api/audio/status")
async def audio_status():
    audio = HALFactory.get_module("audio")
    if audio:
        return audio.get_status()
    return {"error": "Audio module not available"}


@app.post("/api/audio/volume")
async def set_volume(level: int):
    audio = HALFactory.get_module("audio")
    if audio:
        success = audio.set_volume(level)
        return {"success": success, "volume": audio.get_volume()}
    return {"error": "Audio module not available"}


@app.post("/api/audio/mute")
async def set_mute(muted: bool):
    audio = HALFactory.get_module("audio")
    if audio:
        success = audio.set_muted(muted)
        return {"success": success, "muted": audio.get_muted()}
    return {"error": "Audio module not available"}


@app.get("/api/bluetooth/status")
async def bluetooth_status():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        return bt.get_status()
    return {"error": "Bluetooth module not available"}


@app.get("/api/bluetooth/devices")
async def bluetooth_devices():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        return bt.scan_devices()
    return []


@app.post("/api/bluetooth/connect")
async def bt_connect(address: str):
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.connect(address)
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/disconnect")
async def bt_disconnect():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.disconnect()
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.get("/api/wifi/status")
async def wifi_status():
    wifi = HALFactory.get_module("wifi")
    if wifi:
        return wifi.get_status()
    return {"error": "WiFi module not available"}


@app.get("/api/wifi/networks")
async def wifi_networks():
    wifi = HALFactory.get_module("wifi")
    if wifi:
        return wifi.scan_networks()
    return []


@app.post("/api/wifi/connect")
async def wifi_connect(ssid: str, password: str = ""):
    wifi = HALFactory.get_module("wifi")
    if wifi:
        success = wifi.connect(ssid, password)
        return {"success": success}
    return {"error": "WiFi module not available"}


@app.post("/api/wifi/disconnect")
async def wifi_disconnect():
    wifi = HALFactory.get_module("wifi")
    if wifi:
        success = wifi.disconnect()
        return {"success": success}
    return {"error": "WiFi module not available"}


@app.get("/api/obd/status")
async def obd_status():
    obd = HALFactory.get_module("obd")
    if obd:
        return obd.get_status()
    return {"error": "OBD module not available"}


@app.get("/api/airplay/status")
async def airplay_status():
    airplay = HALFactory.get_module("airplay")
    if airplay:
        return airplay.get_status()
    return {"error": "AirPlay module not available"}


@app.get("/api/map/status")
async def map_status():
    map_mod = HALFactory.get_module("map")
    if map_mod:
        return map_mod.get_status()
    return {"error": "Map module not available"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(message)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_websocket_message(message: dict):
    msg_type = message.get("type")
    data = message.get("data", {})
    
    if msg_type == "get_status":
        audio = HALFactory.get_module("audio")
        bt = HALFactory.get_module("bluetooth")
        wifi = HALFactory.get_module("wifi")
        
        await manager.broadcast({
            "type": "status_update",
            "data": {
                "audio": audio.get_status() if audio else {},
                "bluetooth": bt.get_status() if bt else {},
                "wifi": wifi.get_status() if wifi else {},
            }
        })


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)