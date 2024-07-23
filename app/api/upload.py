from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import zipfile

router = APIRouter()

# 上传文件页面
@router.get("/")
def read_root():
    return {"message": "Upload file through /upload endpoint"}


# 上传文件接口，根据文件名分类保存
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):

    # 获取文件名
    filename = file.filename
    
    # 定义分类规则：假设以 "alert_" 开头的文件名为告警类文件
    if "审计" in filename:
        save_directory = "uploads/审计"
    elif "公告" in filename:
        save_directory = "uploads/alerts"
    elif "风险" in filename:
        save_directory = "uploads/风险"
    else :
        save_directory = "uploads/其他"
    # 确保保存目录存在，如果不存在则创建
    os.makedirs(save_directory, exist_ok=True)


    # 拼接保存路径
    save_path = os.path.join(save_directory, filename)

    # 保存文件
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": filename, "save_path": save_path}

# 文件访问接口
@router.get("/files/{file_path:path}")
async def read_file(file_path: str):
    # 构建文件路径
    file_location = os.path.join("./", file_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")

    # 返回文件响应
    return FileResponse(file_location)

# 定义大类关键词
categories = {
    "风险警示": ["风险警示"],
    "交易所关注": ["交易所关注", "关注函", "问询函"],
    "交易所回复": ["交易所回复", "回复", "公告"],
    "证监会立案调查": ["立案调查", "结案", "进展"],
    "证监会行政监管": ["行政监管", "行政处罚", "市场禁入", "警示函"],
    "交易所自律监管": ["自律监管", "纪律处分"],
    "年度审计": ["年度审计", "审计报告"],
    "控股股东和实际控制人": ["控股股东", "实际控制人"],
    "重整情况": ["重整", "债权人会议"],
    "合规问题": ["合规问题", "专项核查意见", "专项审核意见"],
    "投资人引入": ["投资人引入", "战略投资"],
    "重大资产重组": ["重大资产重组", "交易预案", "停牌"]
}

def categorize_file(file_name):
    for category, keywords in categories.items():
        if any(keyword in file_name for keyword in keywords):
            return os.path.join("uploads", category)
    return os.path.join("uploads", "未分类")

@router.post("/upload/files/")
async def upload_file(file: UploadFile = File(...)):
    # 获取文件名并去除后缀
    filename = file.filename
    basefilename, ext = os.path.splitext(filename)

    # 检查文件是否是 .zip 文件
    if ext == ".zip":
        # 创建一个临时文件夹来解压缩文件
        extract_folder = "temp_extracted/"
        os.makedirs(extract_folder, exist_ok=True)

        # 创建一个用于解压缩的 ZipFile 对象
        with zipfile.ZipFile(file.file, 'r') as zip_ref:
            # 获取解压后的文件列表
            extracted_files = zip_ref.namelist()

            # 分类处理每个解压后的文件
            saved_files = []
            for file_name in extracted_files:
                # 忽略 __MACOSX 文件夹及其内容以及任何隐藏文件（以 . 开头的文件）
                if '__MACOSX' in file_name or file_name.startswith('.'):
                    continue

                # 处理文件名乱码问题
                try:
                    file_name = file_name.encode('cp437').decode('gbk')
                except UnicodeDecodeError:
                    file_name = file_name.encode('utf-8').decode('utf-8')


                # 检查是否是文件，而不是目录
                if file_name.endswith('/'):
                    continue
                else:
                    # 获取不包含路径的文件名
                    # 构建源文件路径和目标文件路径
                    base_file_name = os.path.basename(file_name)
                    file_path = os.path.join(extract_folder, file_name)

                    # 解压文件到临时文件夹
                    zip_ref.extract(file_name, extract_folder)

                    # 分类
                    filenameTemp = base_file_name.encode('cp437').decode('utf-8')
                    save_directory = categorize_file(filenameTemp)
                    os.makedirs(save_directory, exist_ok=True)
                    save_path = os.path.join(save_directory, filenameTemp)

                    # 移动文件到目标路径
                    shutil.move(file_path, save_path)
                    
                    saved_files.append({"file_name": filenameTemp, "save_path": save_path})

            # 删除临时解压文件夹
            shutil.rmtree(extract_folder)

        # 返回解压后的文件列表和保存路径
        return JSONResponse(content={"message": "文件已成功上传和解压缩", "saved_files": saved_files})
    
    elif ext == ".pdf":
        # 单个文件上传，直接分类保存
        save_directory = categorize_file(filename)
        os.makedirs(save_directory, exist_ok=True)
        save_path = os.path.join(save_directory, filename)

        # 保存文件
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 删除原始上传文件
        file.file.close()

        # 返回文件名和保存路径
        return JSONResponse(content={"message": "文件已成功上传和分类保存", "filename": filename, "save_path": save_path})

    else:
        # 处理其他类型的文件
        save_directory = categorize_file(filename)
        os.makedirs(save_directory, exist_ok=True)
        save_path = os.path.join(save_directory, filename)

        # 保存文件
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 删除原始上传文件
        file.file.close()

        # 返回文件名和保存路径
        return JSONResponse(content={"message": "其他文件类型已成功上传和分类保存", "filename": filename, "save_path": save_path})