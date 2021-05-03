# from fastapi import APIRouter
from guglhupf.core.util.router import APIRouter

from guglhupf.v1.endpoints import recordings, stats

router = APIRouter(
    prefix='/v1',
    responses={404: {'description': 'Not found'}},
)
router.include_router(recordings.router)
router.include_router(stats.router)
