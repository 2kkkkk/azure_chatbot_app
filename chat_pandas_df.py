from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.callbacks import StreamlitCallbackHandler
# from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI,HarmBlockThreshold,HarmCategory

import streamlit as st
import pandas as pd
import os

file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}


def clear_submit():
    """
    Clear the Submit Button State
    Returns:

    """
    st.session_state["submit"] = False


@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        return file_formats[ext](uploaded_file)
    else:
        st.error(f"Unsupported file format: {ext}")
        return None


st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="🐕")
st.title("🐕 Chat with dog data frame")
left, middle, right = st.columns(3, vertical_alignment="bottom")
llm_list = ("gemini-pro", "gemini-1.0-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b")
option = left.selectbox(
    "Powered by",
    llm_list,
)


google_api_key_input = st.sidebar.text_input("Google API Key", type="password")
if google_api_key_input:
    google_api_key = google_api_key_input
else:
    google_api_key = os.environ.get("GOOGLE_GEMINI_API_KEY",'no_api_key')

uploaded_file = st.sidebar.file_uploader(
    "Upload a Data file",
    type=list(file_formats.keys()),
    help="Various File formats are Support",
    on_change=clear_submit,
)

if not uploaded_file:
    st.warning(
        "This app uses `PythonAstREPLTool` which is vulnerable to arbitrary code execution. Please use caution in deploying and sharing this app."
    )
    
df = None
if uploaded_file:
    df = load_data(uploaded_file)

if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is this data about?"):
    if df is not None:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        llm = ChatGoogleGenerativeAI(model=option, google_api_key=google_api_key,)

        pandas_df_agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
    else:
        with st.chat_message("assistant"):
            st.write('Please Upload a Data file.')