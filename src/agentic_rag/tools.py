from langchain.tools import tool
from tavily import TavilyClient
import os
from langchain.tools import tool
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


INDEX_PATH = "E://Practice//Fastapi//RAG_FastApi//faiss_index"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
retriever = FAISS.load_local(INDEX_PATH, embedding_model,allow_dangerous_deserialization=True).as_retriever()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool(description="Search and return information about LDS and it's teachings")
def retriever_tool(query: str) -> str:
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])


@tool(description="Do a web search based on user queries")
def web_search(query: str) -> str:
    result = tavily_client.search(query)
    return "\n\n".join(
        r["content"] for r in result.get("results", [])
    )