from guglhupf.core.util.router import APIRouter
from guglhupf.core.util.stats import system, video, software

# Cannot be used for Websockets because of `prefix` until this is merged:
# https://github.com/tiangolo/fastapi/pull/2640
router = APIRouter(
    prefix='/stats',
    tags=['stats'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/system')
async def system_stats():
    return system()


@router.get('/video')
async def video_stats():
    return video()


@router.get('/software')
async def software_stats():
    return software()
