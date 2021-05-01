from fastapi import APIRouter

router = APIRouter(
    prefix='/recordings',
    tags=['recordings'],
    responses={404: {'description': 'Not found'}},
)


fake_items_db = {'plumbus': {'name': 'Plumbus'}, 'gun': {'name': 'Portal Gun'}}


@router.get('/')
async def read_items():
    return fake_items_db
