from fastapi import APIRouter 
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import StuffDocumentsChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Tongyi
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.summarize import load_summarize_chain


class Person(BaseModel):
    name: str

class FileInput(BaseModel):
    filename: str

class ChatInput(BaseModel):
    question: str

router = APIRouter()

import os
os.environ["DASHSCOPE_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
modle = Tongyi()

@router.get("/info")
async def answer():
    return {"message": "Hello World"}

# @router.post("/{question}") 这个路由定义是一个动态路径参数，它会匹配任何形如 /xxx 的路径
# @router.post("/{question}")
@router.post("/chat")
async def answer(chat_input: ChatInput):
    prompt = ChatPromptTemplate.from_template("""
    {input}                                                                                                                       
    """
        )
    answer_chain = prompt | modle | StrOutputParser()
    return answer_chain.invoke(chat_input.question)
    

@router.post("/item")
async def create_item(p: Person):
    return p.name

@router.post("/summarize")
async def summarize(file: FileInput):
    # The prompt here should take as an input variable the
    # `document_variable_name`
    prompt = PromptTemplate.from_template(
        "总结这篇文章的内容: {text}"
    )

    chain = load_summarize_chain(modle, chain_type="stuff", prompt=prompt)

    loader = PyPDFLoader(file.filename)
    # loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
    docs = loader.load()
    result = chain.invoke(docs)

    return result["output_text"]


