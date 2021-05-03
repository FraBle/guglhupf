import fnmatch

from fastapi import Query
from fastapi.responses import StreamingResponse

from guglhupf.core.settings import settings
from guglhupf.core.util.router import APIRouter

router = APIRouter(
    prefix='/recordings',
    tags=['recordings'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/')
async def list_recordings(
    front: bool = True,
    back: bool = True,
    local: bool = True,
    cloud: bool = True,
):
    with open(settings.uploaded_files_txt) as uploaded_files_txt:
        all_uploaded_videos = {
            line.strip().split('/')[-1]
            for line in uploaded_files_txt
        }

    all_videos = [
        (
            video.strip().split('/')[-1],
            video.strip().split('/')[-1] in all_uploaded_videos,
        )
        for video in fnmatch.filter(
            [str(vid_file) for vid_file in settings.recordings_dir.iterdir()],
            '*.mp4',
        )
    ]

    return filter(
        lambda vid: all([
            front or not vid[0].startswith('video_front_'),
            back or not vid[0].startswith('video_back_'),
            cloud or not vid[1],
            local or vid[1],
        ]),
        all_videos,
    )


@router.get('/{video}')
def list_recordings(video: str = Query(..., regex='^[a-z0-9_-]+\.mp4$')):
    video_file = open(settings.recordings_dir / video, mode='rb')
    return StreamingResponse(video_file, media_type='video/mp4')
