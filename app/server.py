from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
from langserve import add_routes
from app.api.answer import router as answer_router
from app.api.upload import router as upload_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

#设置允许访问的域名
origins = ["*"]  #也可以设置为"*"，即为所有。

#设置跨域传参
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,  #设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  #允许跨域的headers，可以用来鉴别来源等作用。


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
app.include_router(answer_router, prefix="/v1/answer", tags=["answer"])
app.include_router(upload_router, prefix="/v1", tags=["upload"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
