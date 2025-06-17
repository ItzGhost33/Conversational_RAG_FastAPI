from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",     # deepseek-r1-distill-qwen-32b  , deepseek-r1-distill-llama-70b
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key = GROQ_API_KEY
)





