from operator import itemgetter
from guglhupf.core.util.router import APIRouter
from guglhupf.core.stats.system import system, video, software, all_stats

# Cannot be used for Websockets because of `prefix` until this is merged:
# https://github.com/tiangolo/fastapi/pull/2640
router = APIRouter(
    prefix='/stats',
    tags=['stats'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/system')
async def system_stats():
    return {
        'attributes': sorted([
            {
                'attribute': system_attribute,
                'value': current_value,
            }
            for system_attribute, current_value in system().items()
        ], key=itemgetter('attribute'),
        ),
    }


@router.get('/video')
async def video_stats():
    return {
        'attributes': sorted([
            {
                'attribute': video_attribute,
                'value': current_value,
            }
            for video_attribute, current_value in video().items()
        ], key=itemgetter('attribute'),
        ),
    }


@router.get('/software')
async def software_stats():
    return {
        'attributes': sorted([
            {
                'attribute': software_attribute,
                'value': current_value,
            }
            for software_attribute, current_value in software().items()
        ], key=itemgetter('attribute'),
        ),
    }
