from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
import json
import asyncio
import os
import inspect

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


async def status_broadcast_loop():
    while True:
        try:
            if manager.active_connections:
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
        except Exception as e:
            print(f"Error in status broadcast loop: {e}")
        await asyncio.sleep(1.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Starting RPi Car Infotainment Backend (HAL: {settings.hal_mode})")
    
    results = HALFactory.initialize_all()
    print(f"Module initialization results: {results}")
    
    broadcast_task = asyncio.create_task(status_broadcast_loop())
    
    yield
    
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass
        
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
        if inspect.isawaitable(success):
            success = await success
        return {"success": success, "volume": audio.get_volume()}
    return {"error": "Audio module not available"}


@app.post("/api/audio/mute")
async def set_mute(muted: bool):
    audio = HALFactory.get_module("audio")
    if audio:
        success = audio.set_muted(muted)
        if inspect.isawaitable(success):
            success = await success
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
        devices = bt.scan_devices()
        if inspect.isawaitable(devices):
            devices = await devices
        return devices
    return []


@app.post("/api/bluetooth/connect")
async def bt_connect(address: str):
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.connect(address)
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/disconnect")
async def bt_disconnect():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.disconnect()
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/unpair")
async def bt_unpair(address: str):
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.unpair(address)
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/discoverable")
async def bt_discoverable(enabled: bool):
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.set_discoverable(enabled)
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/player/play")
async def bt_player_play():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.player_play()
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/player/pause")
async def bt_player_pause():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.player_pause()
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/player/next")
async def bt_player_next():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.player_next()
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/player/previous")
async def bt_player_previous():
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.player_previous()
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/player/shuffle")
async def bt_player_shuffle(mode: str):
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.player_shuffle(mode)
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "Bluetooth module not available"}


@app.post("/api/bluetooth/player/repeat")
async def bt_player_repeat(mode: str):
    bt = HALFactory.get_module("bluetooth")
    if bt:
        success = bt.player_repeat(mode)
        if inspect.isawaitable(success):
            success = await success
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
        networks = wifi.scan_networks()
        if inspect.isawaitable(networks):
            networks = await networks
        # Rinominiamo is_secure in isSecure per il frontend
        return [{**n, "isSecure": n.get("is_secure", False)} for n in networks]
    return []


@app.post("/api/wifi/connect")
async def wifi_connect(ssid: str, password: str = ""):
    wifi = HALFactory.get_module("wifi")
    if wifi:
        success = wifi.connect(ssid, password)
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "WiFi module not available"}


@app.post("/api/wifi/disconnect")
async def wifi_disconnect():
    wifi = HALFactory.get_module("wifi")
    if wifi:
        success = wifi.disconnect()
        if inspect.isawaitable(success):
            success = await success
        return {"success": success}
    return {"error": "WiFi module not available"}


@app.get("/api/obd/status")
async def obd_status():
    obd = HALFactory.get_module("obd")
    if obd:
        return obd.get_status()
    return {"error": "OBD module not available"}


# ── System endpoints ──────────────────────────────────────────────────────────

@app.get("/api/system/version")
async def system_version():
    system = HALFactory.get_module("system")
    if system:
        git_info = await system.get_git_info()
        return {
            "version": system.get_version(),
            **git_info
        }
    return {"version": "unknown"}


@app.post("/api/system/update/pull")
async def system_update_pull():
    system = HALFactory.get_module("system")
    if system:
        return await system.pull_code()
    return {"error": "System module not available"}


@app.post("/api/system/update/install")
async def system_update_install():
    system = HALFactory.get_module("system")
    if system:
        return await system.run_install()
    return {"error": "System module not available"}


@app.post("/api/system/reboot-app")
async def system_reboot_app():
    system = HALFactory.get_module("system")
    if system:
        return await system.reboot_app()
    return {"error": "System module not available"}


@app.post("/api/system/reboot")
async def system_reboot():
    system = HALFactory.get_module("system")
    if system:
        return await system.reboot_system()
    return {"error": "System module not available"}


@app.post("/api/system/shutdown")
async def system_shutdown():
    system = HALFactory.get_module("system")
    if system:
        return await system.shutdown_system()
    return {"error": "System module not available"}




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


@app.get("/api/media/songs")
async def get_songs():
    media = HALFactory.get_module("media")
    if media:
        return await media.get_all_songs()
    return {"error": "Media module not available"}


class RenameRequest(BaseModel):
    new_name: str

class TrimRequest(BaseModel):
    start_time: int
    end_time: int

@app.delete("/api/media/songs/{song_id}")
async def delete_song(song_id: str):
    media = HALFactory.get_module("media")
    if media:
        success = await media.delete_song(song_id)
        return {"success": success}
    return {"error": "Media module not available"}

@app.put("/api/media/songs/{song_id}/rename")
async def rename_song(song_id: str, req: RenameRequest):
    media = HALFactory.get_module("media")
    if media:
        success = await media.rename_song(song_id, req.new_name)
        return {"success": success}
    return {"error": "Media module not available"}

@app.post("/api/media/songs/{song_id}/trim")
async def trim_song(song_id: str, req: TrimRequest):
    media = HALFactory.get_module("media")
    if media:
        success = await media.trim_song(song_id, req.start_time, req.end_time)
        return {"success": success}
    return {"error": "Media module not available"}



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

# ── Static Files & Frontend ───────────────────────────────────────────────────

# /library must be mounted BEFORE the "/" catch-all
library_path = os.path.join(os.path.dirname(__file__), "library")
if not os.path.exists(library_path):
    os.makedirs(library_path)
app.mount("/library", StaticFiles(directory=library_path), name="library")

# Mount built frontend — must be LAST (catch-all for html=True)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {"status": "ok", "message": "RPi Car Infotainment Backend — frontend non compilato"}



if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)