from dotenv import load_dotenv
import streamlit as st

from src.constants import DOTENV_PATH
from src.agent import create_rag_agent
from src.tools import get_retriever_tool, language_checker, query_reformulator

load_dotenv(DOTENV_PATH)

# Set page configuration
st.set_page_config(
    page_title="💬 Multilingual RAG Bot",
    layout="wide"
)

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = create_rag_agent([get_retriever_tool(), language_checker, query_reformulator])
    st.session_state.config = {"configurable": {"thread_id": "1"}}

# Create the three-column layout
left_col, center_col, right_col = st.columns([1, 2, 1])

# Left column content
with left_col:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.agent = create_rag_agent([get_retriever_tool(), language_checker, query_reformulator])
        st.session_state.config = {"configurable": {"thread_id": "1"}}
        st.rerun()

# Center column content with chat interface
with center_col:    # Display chat title
    st.title("💬 Multilingual RAG Bot")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        user_msg = {"role":"user","content":prompt}
        st.session_state.messages.append(user_msg)
        
        response = st.session_state.agent.invoke({"messages": [user_msg]}, st.session_state.config)
        ai_msg = response['messages'][-1].content
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role":"assistant","content":ai_msg})
        
        # Rerun to update the display
        st.rerun()
            

# Right column content is intentionally left blank as per requirements
with right_col:
    pass