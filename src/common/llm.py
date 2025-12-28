from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_deepseek import ChatDeepSeek


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",     # deepseek-r1-distill-qwen-32b  , deepseek-r1-distill-llama-70b
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key = GROQ_API_KEY
)

llm_2 = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.6,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key= DEEPSEEK_API_KEY
)




