import os
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain import hub
from finbot_api.src.chains.financial_review_chain import (
    vectorstore_query,
    direct_trade_query
)

FINANCIAL_AGENT_MODEL = "openai"

financial_agent_prompt = "..."

tools = [
    Tool(
        name="Education",
        func=vectorstore_query.invoke,
        description="""Useful when you need to answer questions
        about general idea of the markets and trading.
        """,
    ),
    Tool(
        name="TradeQuery",
        func=direct_trade_query.invoke,
        description="""Useful for suggestions about the direct
        trading queries.
        """,
    ),
]

chat_model = ChatOpenAI(
    model=FINANCIAL_AGENT_MODEL,
    temperature=0,
)

financial_rag_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=financial_agent_prompt,
    tools=tools,
)

financial_rag_agent_executor = AgentExecutor(
    agent=financial_rag_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)