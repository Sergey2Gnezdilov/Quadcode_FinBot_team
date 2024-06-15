import streamlit as st
import os
import tempfile
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.environ["GROQ_API_KEY"]


def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "generated" not in st.session_state:
        st.session_state["generated"] = [
            "Hello this is FinBot! Your all in one Customisable Financial Assistant. Feel free to ask me any questions."
        ]

    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey! 👋 FinBot!"]


def conversation_chat(query, chain, history):
    result = chain({
        "question": query,
        "chat_history": history
    })
    history.append((query, result["answer"]))
    return result["answer"]


def display_chat_history(chain):
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_input(
                "Question:",
                placeholder="Ask about your Documents",
                key="input"
            )
            submit_button = st.form_submit_button(label="Send")

        if submit_button and user_input:
            with st.spinner("Generating response ......"):
                output = conversation_chat(
                    query=user_input,
                    chain=chain,
                    history=st.session_state["history"]
                )

            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)

    if st.session_state["generated"]:
        with reply_container:
            for i in range(len(st.session_state["generated"])):
                message(
                    st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs"
                )
                message(
                    st.session_state["generated"][i],
                    key=str(i),
                    avatar_style="fun-emoji"
                )


def create_conversational_chain(vector_store):
    llm = ChatGroq(
        temperature=0.5,
        model_name="mixtral-8x7b-32768",
        groq_api_key=groq_api_key
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
        memory=memory
    )

    return chain


@st.cache_resource
def load_guideline_document():
    pdf_path = "assets/guidelines/C029-IF-on-systems-and-controls-in-an-automated-trading-environment.pdf"
    loader = PyPDFLoader(pdf_path)
    text = loader.load()

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=768,
        chunk_overlap=128,
        length_function=len
    )
    text_chunks = text_splitter.split_documents(text)

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    vector_store = Chroma.from_documents(
        documents=text_chunks,
        embedding=embedding,
        persist_directory="chroma_store_guideline"
    )
    return vector_store


def main():
    initialize_session_state()
    st.title("📈FinBot")
    guideline_vector_store = load_guideline_document()
    chain = create_conversational_chain(vector_store=guideline_vector_store)
    display_chat_history(chain=chain)


if __name__ == "__main__":
    main()
