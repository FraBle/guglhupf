from fastapi import APIRouter

from guglhupf.v1.endpoints import recordings

router = APIRouter(
    prefix='/v1',
    responses={404: {'description': 'Not found'}},
)
router.include_router(recordings.router)
