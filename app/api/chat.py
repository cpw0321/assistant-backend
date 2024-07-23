from app.api.answer import model
from langchain.chains.router import LLMRouterChain, MultiPromptChain
from langchain.chains.router.llm_router import RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts import PromptTemplate
from fastapi import APIRouter 

router = APIRouter()

# 准备2条目的链：一条物理链，一条数学链
# 1. 物理链
physics_template = """
"system", "你是一位物理学家，擅长回答物理相关的问题，当你不知道问题的答案时，你就回答不知道。"
具体问题如下：
"human","{input}"
"""
physics_prompt = PromptTemplate.from_template(physics_template)
physics_chain = LLMChain(llm=model, prompt=physics_prompt)

# 2. 数学链
math_template = """
你是一个数学家，擅长回答数学相关的问题，当你不知道问题的答案时，你就回答不知道。
具体问题如下：
{input}
"""
math_prompt = PromptTemplate.from_template(math_template)
math_chain = LLMChain(llm=model, prompt=math_prompt)

# 3. 英语链
english_template = """
你是一个非常厉害的英语老师，擅长回答英语相关的问题，当你不知道问题的答案时，你就回答不知道。
具体问题如下：
{input}
"""
english_prompt = PromptTemplate.from_template(english_template)
english_chain = LLMChain(llm=model, prompt=english_prompt)

######### 所有可能的目的链
destination_chains = {}
destination_chains["physics"] = physics_chain
destination_chains["math"] = math_chain
destination_chains["english"] = english_chain

######### 默认链
default_chain = ConversationChain(llm=model, output_key="text")

# 让多路由模板 能找到合适的 提示词模板
destinations_template_str = """
physics:擅长回答物理问题
math:擅长回答数学问题
english:擅长回答英语问题
"""
router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
    destinations=destinations_template_str
)

# 通过路由提示词模板，构建路由提示词
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)

######### 路由链
router_chain = LLMRouterChain.from_llm(llm=model, prompt=router_prompt)

######### 最终的链
multi_prompt_chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=default_chain,
    verbose=True,
)

# multi_prompt_chain.invoke({"input": "重力加速度是多少？"})
# multi_prompt_chain.invoke("y=x^2+2x+1的导数是多少？")
@router.post("/multi/{input}")
async def create_item(input: str):
    return multi_prompt_chain.invoke(input)
# multi_prompt_chain.invoke("将以下英文翻译成中文，只输出中文翻译结果：\n The largest community building the future of LLM apps.")
# multi_prompt_chain.invoke("你是怎么理解java的面向对象的思想的？")

