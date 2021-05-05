import fnmatch
from pathlib import Path

from fastapi import Query, Request
from fastapi.responses import StreamingResponse

from guglhupf.core.settings import settings
from guglhupf.core.util.router import APIRouter

router = APIRouter(
    prefix='/recordings',
    tags=['recordings'],
    responses={404: {'description': 'Not found'}},
)

BYTES_PER_RESPONSE = 100000


def get_video_and_total_size(video):
    file_path = Path(settings.recordings_dir / video)
    video_file = open(file_path, mode='rb')
    video_size = (file_path).stat().st_size
    return video_file, video_size


def chunk_generator_from_stream(stream, chunk_size, start, size):
    bytes_read = 0

    stream.seek(start)

    while bytes_read < size:
        bytes_to_read = min(chunk_size,
                            size - bytes_read)
        yield stream.read(bytes_to_read)
        bytes_read = bytes_read + bytes_to_read

    stream.close()


@router.get('/')
async def list_recordings(
    front: bool = False,
    back: bool = False,
    local: bool = False,
    cloud: bool = False,
):
    with open(settings.uploaded_files_txt) as uploaded_files_txt:
        all_uploaded_videos = {
            line.strip().split('/')[-1]
            for line in uploaded_files_txt
        }

    all_videos = [
        {
            'fileName': video.strip().split('/')[-1],
            'uploaded':video.strip().split('/')[-1] in all_uploaded_videos,
        }
        for video in fnmatch.filter(
            [str(vid_file) for vid_file in settings.recordings_dir.iterdir()],
            '*.mp4',
        )
    ]

    return {
        'recordings': list(filter(
            lambda vid: all([
                front or not vid['fileName'].startswith('video_front_'),
                back or not vid['fileName'].startswith('video_back_'),
                cloud or not vid['uploaded'],
                local or vid['uploaded'],
            ]),
            all_videos,
        )),
    }


@router.get('/{video}')
def list_recordings(
    req: Request,
    video: str = Query(..., regex='^[a-z0-9_-]+\.mp4$'),
):
    # https://github.com/tiangolo/fastapi/issues/1240#issuecomment-797618168
    asked = req.headers.get("Range")
    stream, total_size = get_video_and_total_size(video)
    start_byte_requested = int(asked.split("=")[-1][:-1])
    end_byte_planned = min(start_byte_requested +
                           BYTES_PER_RESPONSE, total_size) - 1
    chunk_generator = chunk_generator_from_stream(
        stream,
        chunk_size=10000,
        start=start_byte_requested,
        size=BYTES_PER_RESPONSE
    )
    return StreamingResponse(
        chunk_generator,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte_requested}-{end_byte_planned}/{total_size}",
            "Content-Type": "..."
        },
        status_code=206,
        media_type='video/mp4',
    )
