from typing_extensions import Callable, Sequence, Union

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools.base import BaseTool
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.prompts import chatbot_prompt
from src.tools import get_retriever_tool, language_checker, query_reformulator
from src.utils import get_chat_llm_model


def chatbot_agent(state: MessagesState) -> MessagesState:
    """Generate Tool calls for retrieval, language checking and query formulation or respond"""
    chat_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", chatbot_prompt),
            ("placeholder", "{messages}"),
        ]
    )
    llm_with_tools = get_chat_llm_model(tools=[get_retriever_tool(), language_checker, query_reformulator])
    llm_with_prompt = chat_prompt_template | llm_with_tools
    response = llm_with_prompt.invoke(state)
    return {"messages": [response]}

def create_rag_agent(tools: Sequence[Union[BaseTool, Callable]]) -> CompiledStateGraph:
    """Create a RAG Agent capable of Reasoning, Action and Observation"""
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot_agent)
    graph_builder.add_node("tools", ToolNode(tools))
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition,{"tools": "tools", END: END})
    graph_builder.add_edge("tools", "chatbot")

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    return graph
