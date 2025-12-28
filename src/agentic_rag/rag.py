from langchain.messages import HumanMessage, AIMessage
from src.agentic_rag.graph import graph

def get_msg_content(msg):
    return msg.content

def rag_service(user_query: str, chat_history: list, session_id: str, username: str, db):
    """
    RAG service using LangGraph workflow with chat history integration.
    
    Parameters:
    - user_query: current user question
    - chat_history: list of previous messages (dicts with 'role' and 'content')
    - session_id, username, db: for logging and retrieving chat history
    """

    # Load previous chat history from DB if not provided
    if chat_history is None:
        chat_history = get_chat_history(session_id, db)

    # Convert chat history into LangChain Messages
    messages = []
    for entry in chat_history:
        if entry['role'] == 'user':
            messages.append(HumanMessage(content=entry['content']))
        elif entry['role'] == 'assistant':
            messages.append(AIMessage(content=entry['content']))

    # Append the current user query
    messages.append(HumanMessage(content=user_query))

    # Initial LangGraph state
    state = {
        "messages": messages,
        "retry_count": 0,
        "intent": "",
    }

    # Stream the workflow
    for chunk in graph.stream(state):
        for node_name, update in chunk.items():
            if "messages" in update:
                state["messages"] = update["messages"]
            if "retry_count" in update:
                state["retry_count"] = update["retry_count"]
            if "intent" in update:
                state["intent"] = update["intent"]

    # Final response from the assistant
    final_msg = state["messages"][-1]
    answer = get_msg_content(final_msg)

    # Log the user query and assistant response in DB
    insert_log(session_id, username, user_query, answer, db)

    # Update chat history with new interaction
    chat_history.append({"role": "user", "content": user_query})
    chat_history.append({"role": "assistant", "content": answer})

    return answer.strip(), session_id, chat_history
