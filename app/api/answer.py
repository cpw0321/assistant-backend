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
from docx import Document
import re

class Person(BaseModel): 
    name: str

class FileInput(BaseModel):
    filename: list

class ChatInput(BaseModel):
    question: str

class AggregateSummarizeInput(BaseModel):
    fileList: list

class FileDirInput(BaseModel):
    filedir: str

router = APIRouter()

import os
os.environ["DASHSCOPE_API_KEY"] = "sk-"
#llm=Tongyi(model_name="qwen-plus",temperature=0.1)
model = Tongyi(model_name="qwen-max", temperature=0.46)
print("===========================")
# dir(Tongyi)
print(model)



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
    answer_chain = prompt | model | StrOutputParser()
    result = answer_chain.invoke(chat_input.question)
    return {"result": result}
    

@router.post("/item")
async def create_item(p: Person):
    return p.name

template =         '''
    # 角色
    你是一位专长于债务重组领域的律师助理，具备两年以上实战经验。你的核心职责是透彻分析并精准总结法律文档，为律师提供关于企业状况的精炼报告。

    ## 技能
    ### 技能1: 法律与财务双基
    - 掌握基础法律知识，特别是债务重组与争议解决的关键法规与程序。
    - 具备基础财务理解力，熟悉财务报表结构，能解读主要财务科目及其应用。

    ### 技能2: 高效信息提炼
    - 精准阅读文档，快速识别并提取案件核心要素与细节信息。
    
    ### 技能3: 准确文案撰写
    - 运用法律术语与财务语言，将提取的信息整合为精确、简洁的报告，确保内容的客观性与完整性。

    ## 任务流程
    1. 将主体事件一句话总结并作为标题，请参照示例。

    2. 总结事件发生的原因，整理成一段话即可，请参照示例。

    3. 禁止总结其他内容，禁止自行分析，不要超过300字

    4. 格式要求：
    xxxx（标题写在第一行，字体加粗，时间必须写在前面）
    xxxx（原因写在第二段）

    5. 示例
    **2018年5月3日，赫美集团因出具无法表示意见的审计报告被实施退市风险警示**
    2018年5月3日，因普华永道对其2017年度财务报告出具无法表示意见的审计报告，导致深交所对该企业股票实行退市风险警示

    ## 限制
    - 仅限于文档内信息总结，禁止外部资料搜索或假设性内容添加。
    - 确保报告内容简洁明了，避免冗余扩展。
    - 所有产出需严格遵循事实，保持专业客观性。
                       
    {text}
    '''

@router.post("/summarize")
async def summarize(file: FileInput):
    # The prompt here should take as an input variable the
    # `document_variable_name`
    prompt = PromptTemplate.from_template(
        template
    )

    chain = load_summarize_chain(model, chain_type="stuff", prompt=prompt)

    loader = PyPDFLoader(file.filename)
    # loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
    docs = loader.load()
    result = chain.invoke(docs)
    result = chain.invoke(docs)

    return {"result": result["output_text"]}


@router.post("/aggregate_summaries")
async def aggregate_summaries(files: AggregateSummarizeInput):
    aggregated_summary = ""

    for file in files.fileList:
        prompt = PromptTemplate.from_template(
            template
        )

        chain = load_summarize_chain(model, chain_type="stuff", prompt=prompt)

        loader = PyPDFLoader(file)
        docs = loader.load()
        result = chain.invoke(docs)

        # 将每个文件的总结添加到汇总中
        aggregated_summary += result["output_text"] + "\n\n"

    # 将汇总的总结返回
    return {"result": aggregated_summary}

temp = '''
    [
        ("system", "You are a helpful AI bot."),
        ("human", {input}),
    ]
    '''

from langchain.memory import ChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict

history = ChatMessageHistory()


template01 =         '''
你是一个非常厉害的英语老师，擅长回答英语相关的问题，对于其他领域的问题，你就回答不知道。
{input}
    '''

@router.post("/chat/summary")
async def answer(chat_input: ChatInput):
    prompt = ChatPromptTemplate.from_template(template01)
    answer_chain = prompt | model 
    # loader = PyPDFLoader("uploads/alerts/002356 赫美集团 2019-04-30  关于公司股票交易被实施退市风险警示的公告.pdf")
    # docs = loader.load()
    # # print(chat_input.question+"\n\n"+docs[0].page_content)
    return answer_chain.invoke(chat_input.question)
  


    # history.add_user_message(chat_input.question)

    # history.add_ai_message(model.invoke(chat_input.question))
    # return history.messages


@router.post("/summarie/category")
async def aggregate_summaries(fileDir: str):
    
    folder_path = "uploads/" + fileDir
    files = os.listdir(folder_path)
    sorted_files = sorted(files, key=get_sort_key)
    doc = Document()

    for file in sorted_files:
        prompt = PromptTemplate.from_template(
            template
        )

        chain = load_summarize_chain(model, chain_type="stuff", prompt=prompt)

        filename = os.path.join(folder_path, file)
        loader = PyPDFLoader(filename)
        docs = loader.load()
        result = chain.invoke(docs)

        # 将每个文件的总结添加到汇总中
        doc.add_paragraph(result["output_text"] + "\n\n")
        
    
    doc.save(fileDir+".docx")

    # 将汇总的总结返回
    return {"result": "success"}



# 自定义排序函数，从文件名中提取日期作为排序键
def get_sort_key(filename):
    # 使用正则表达式从文件名中提取日期部分
    match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', filename)
    if match:
        date_str = match.group(1)
        return date_str
    else:
        # 如果文件名中没有找到日期信息，返回一个默认值
        return filename