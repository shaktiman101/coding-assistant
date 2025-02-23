from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from react_agent.utils import get_documents


def get_chunk_data(docs):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(docs)
    # doc_splits = text_splitter.split_text(docs)
    return doc_splits

def vectorise(doc_splits):
    # vectorstore = Chroma.from_texts(
    #     texts=doc_splits,
    #     collection_name="code-rag-chroma",
    #     embedding=AzureOpenAIEmbeddings(),
    # )
        
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="code-rag-chroma",
        embedding=AzureOpenAIEmbeddings(),
    )
    return vectorstore

def get_retriever(path="."):
    code_data = get_documents(path)
    print("reading code data")
    chunked_data = get_chunk_data(code_data)
    vectorstore = vectorise(chunked_data)
    print("embedding done")
    retriever = vectorstore.as_retriever()
    return retriever