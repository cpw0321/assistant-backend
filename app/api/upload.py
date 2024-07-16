from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
import shutil
import os

router = APIRouter()

# 上传文件页面
@router.get("/")
def read_root():
    return {"message": "Upload file through /upload endpoint"}

# 文件上传接口
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # 保存文件到指定目录
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

# 文件访问接口
@router.get("/files/{file_path}")
def read_file(file_path: str):
    # 构建文件路径
    file_location = os.path.join("./", file_path)
    # 返回文件响应
    return FileResponse(file_location)
