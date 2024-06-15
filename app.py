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
import yfinance as yf
import re
import pandas as pd

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


def get_stock_summary(ticker):
    '''
    Get a snapshot of the current stock price along with a brief summary of the company.
    '''
    stock = yf.Ticker(ticker)
    info = stock.info
    current_price = info.get('regularMarketPrice', 'No price available')
    summary = (f"Previous Close: ${info.get('previousClose')}\n"
               f"Market Cap: {info.get('marketCap')} (approx.)\n"
               f"52 Week Range: {info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}")
    return summary


def get_historical_data(ticker, period="1mo"):
    '''
    Provide access to historical data which could be useful for analyzing trends.
    '''
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    # Drop the 'Dividends' and 'Stock Splits' columns
    hist = hist.drop(columns=['Dividends', 'Stock Splits'])
    # Return as Markdown
    return hist.to_markdown()


def get_latest_news(ticker):
    '''
    Retrieve the latest news articles related to the stock, as traders often need to be updated with the latest market news.
    '''
    stock = yf.Ticker(ticker)
    news_items = stock.news
    formatted_news = [f"{item['title']}\nRead more: {item['link']}" for item in news_items]
    return formatted_news


def get_dividends_and_splits(ticker):
    '''
    Information on dividends and stock splits can be crucial for decision-making in trading.
    '''
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    splits = stock.splits
    return dividends, splits


def extract_ticker(query):
    # Simple regex to find uppercase words (assumed ticker symbols)
    match = re.search(r"\b[A-Z]{2,5}\b", query)
    if match:
        return match.group(0)
    return None  # Return None if no ticker found


def conversation_chat(query, chain, history):
    # Initialize the response variable
    response = ""

    # Determine the type of query and process accordingly
    if "price" in query.lower():
        ticker = extract_ticker(query)
        if ticker:
            response = get_stock_summary(ticker)
        else:
            response = "Ticker symbol not found. Please try again."
    elif "news" in query.lower():
        ticker = extract_ticker(query)
        if ticker:
            news = get_latest_news(ticker)
            response = "\n\n".join(news) if news else "No news found."
        else:
            response = "Ticker symbol not found. Please try again."
    elif "history" in query.lower():
        ticker = extract_ticker(query)
        if ticker:
            history_data = get_historical_data(ticker, "1mo")
            response = f"Below is the stock history in the past month for {ticker}:\n\n{history_data}"
        else:
            response = "Ticker symbol not found. Please try again."
    else:
        # Handle non-financial queries using the RAG chain
        result = chain({
            "question": query,
            "chat_history": history
        })
        response = result["answer"]

    history.append((query, response))
    return response


def display_chat_history(chain):
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_input(
                "Question:",
                placeholder="Ask me anything about trading!",
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
            for i, (past, generated) in enumerate(zip(st.session_state["past"], st.session_state["generated"])):
                message(
                    past,
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs"
                )
                # Check if the generated content is Markdown to render it correctly
                if generated.startswith("|"):
                    st.markdown(generated, unsafe_allow_html=True)
                else:
                    message(
                        generated,
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
