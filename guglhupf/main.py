import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from guglhupf.core.settings import settings
from guglhupf.core.log import setup_logging
from guglhupf.core.util.stats import all_stats
from guglhupf.v1 import api

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version=settings.app_version,
)
app.include_router(api.router)

# Init logging last so it can override all loggers
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
)


@app.websocket('/ws/system')
async def system_ws(websocket: WebSocket):
    # Cannot use APIRouter in sub-resource until this is merged:
    # https://github.com/tiangolo/fastapi/pull/2640
    await websocket.accept()
    while True:
        await websocket.send_json(all_stats())
        await asyncio.sleep(0.1)


@app.websocket('/ws/gps')
async def gps_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        with open(settings.gps_txt) as gps_txt:
            gps_coordinates = gps_txt.read()
        await websocket.send_text(gps_coordinates)
        await asyncio.sleep(0.1)
