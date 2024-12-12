from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI,HarmBlockThreshold,HarmCategory

import streamlit as st
import os

st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="🐕")
st.title("🐕 Chat with dog")

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

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    msgs.add_ai_message("How can I help you?")

view_messages = st.expander("View the message contents in session state")

# Get an OpenAI API Key before continuing
# if "openai_api_key" in st.secrets:
#     openai_api_key = st.secrets.openai_api_key
# else:
#     openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
# if not openai_api_key:
#     st.info("Enter an OpenAI API Key to continue")
#     st.stop()


# Set up the LangChain, passing in Message History

if 'gemini-1.5' in option:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an AI chatbot having a conversation with a human."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )
else:
        prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "You are an AI chatbot having a conversation with a human."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

llm = ChatGoogleGenerativeAI(model=option, google_api_key=google_api_key,    safety_settings={
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_TOXICITY: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY: HarmBlockThreshold.BLOCK_NONE,

    },)
chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    
    # msgs.add_user_message(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)#response.content
    # msgs.add_ai_message(response)


# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:

    view_messages.json(st.session_state.langchain_messages)
