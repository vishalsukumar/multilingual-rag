from typing_extensions import Callable, Sequence, Union

from langchain_core.tools.base import BaseTool
from langchain.chat_models import init_chat_model

from src.constants import MODEL_PROVIDER, OPENAI_LLM_MODEL

def get_chat_llm_model(
    tools: Sequence[Union[BaseTool, Callable]] | None,
    temperature: float = 0.25,
):
    """A wrapper to initialize and return a Chat model with tools if provided"""
    llm = init_chat_model(OPENAI_LLM_MODEL, model_provider=MODEL_PROVIDER, temperature=temperature)
    if tools:
        llm = llm.bind_tools(tools)
    return llm