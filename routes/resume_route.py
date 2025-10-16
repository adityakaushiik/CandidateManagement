from fastapi import Depends, File, UploadFile
from fastapi.routing import APIRouter

from services.resume_parser import get_resume_parser

resume_route = APIRouter()


@resume_route.post("/parse")
async def parse_resume(
    file: UploadFile = File(...),
    resume_parser=Depends(get_resume_parser),
):
    data = await resume_parser.parse(file)
    return {"data": data}
