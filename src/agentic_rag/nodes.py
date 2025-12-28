from pydantic import BaseModel, Field
from typing import Literal
from src.common.prompts import INTENT_PROMPT, GRADE_PROMPT, REWRITE_PROMPT,GENERATE_PROMPT
from langchain.messages import HumanMessage, AIMessage
from src.agentic_rag.tools import retriever_tool, web_search
from src.common.llm import llm_2
from src.agentic_rag.state import AgentState


class QueryIntent(BaseModel):
    intent: Literal["greeting", "lds_religion", "web_search"]

def route_initial_intent(state: AgentState):
    question = state["messages"][0].content

    response = llm_2.with_structured_output(QueryIntent).invoke(
        [{"role": "user", "content": INTENT_PROMPT.format(question=question)}]
    )

    return {"intent": response.intent}

def greeting_response(state: AgentState):
    response = llm_2.invoke(state["messages"])
    return {"messages": [response]}


def web_entry(state: AgentState):
    query = state["messages"][0].content
    result = tavily_client.search(query)

    content = "\n\n".join(r["content"] for r in result["results"])

    return {"messages": [HumanMessage(content=content)]}




class GradeDocuments(BaseModel):  
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


def grade_documents(
    state: AgentState,
) -> Literal["generate_answer", "rewrite_question", "web_fallback"]:

    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = llm_2.with_structured_output(GradeDocuments).invoke(
        [{"role": "user", "content": prompt}]
    )

    if response.binary_score == "yes":
        return "generate_answer"

    if state["retry_count"] >= 1:
        return "web_fallback"

    return "rewrite_question"



def rewrite_question(state: AgentState):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = llm_2.invoke([{"role": "user", "content": prompt}])
    return {
        "messages": [HumanMessage(content=response.content)],
        "retry_count": state["retry_count"] + 1
            }

def generate_answer(state: AgentState):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = llm_2.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}


def web_fallback(state: AgentState):
    query = state["messages"][0].content
    result = web_search.invoke(query)

    return {
        "messages": [
            HumanMessage(content=result)
        ]
    }

def decide_web_or_respond(state: AgentState):
    last_user_msg = next(
        m for m in reversed(state["messages"])
        if m.type == "human"
    )

    response = (
        llm_2.bind_tools([web_search]).invoke([last_user_msg])
    )

    return {"messages": [response]}

def lds_retriever_node(state: AgentState):
    last_user_msg = next(
        m for m in reversed(state["messages"]) if m.type == "human"
    )
    docs_text = retriever_tool.invoke(last_user_msg.content)
    return {"messages": [AIMessage(content=docs_text)]}