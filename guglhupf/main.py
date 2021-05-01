from fastapi import FastAPI

from guglhupf.core.settings import settings
from guglhupf.core.log import setup_logging
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


@app.get('/')
async def root():
    return {'message': 'Hello Bigger Applications!'}
