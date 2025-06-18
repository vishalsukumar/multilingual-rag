from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools.retriever import create_retriever_tool

from src.constants import MODEL_PROVIDER, OPENAI_LLM_MODEL
from src.prompts import language_checker_prompt, query_reformulator_prompt
from src.vector_store import initialize_vector_store


def get_retriever_tool():
    vectorstore = initialize_vector_store()
    retriever = vectorstore.as_retriever(k=5)
    retriever_tool = create_retriever_tool(
        retriever,
        "retriever",
        "Retrieve relevant documents from the internal knowledge base",
    )
    return retriever_tool

@tool
def language_checker(query: str, context: str) -> str:
    """
    Check if the query is in the same language as the context.
    """
    user_prompt = """
    query: {query}
    context: {context}
    """
    lang_checker_prompt_template = ChatPromptTemplate.from_messages([
        ("system", language_checker_prompt),
        ("user", user_prompt),
    ])
    llm = init_chat_model(OPENAI_LLM_MODEL, model_provider=MODEL_PROVIDER) 
    lang_checker = lang_checker_prompt_template | llm | StrOutputParser()
    return lang_checker.invoke({"query": query, "context": context})

@tool
def query_reformulator(query: str, context: str) -> str:
    """
    Reformat the query to be in the same language as the context.
    """
    user_prompt = """
    query: {query}
    context: {context}
    """
    query_reformulator_prompt_template = ChatPromptTemplate.from_messages([
        ("system", query_reformulator_prompt),
        ("user", user_prompt),
    ])
    llm = init_chat_model(OPENAI_LLM_MODEL, model_provider=MODEL_PROVIDER) 
    query_reformulator = query_reformulator_prompt_template | llm | StrOutputParser()
    return query_reformulator.invoke({"query": query, "context": context})