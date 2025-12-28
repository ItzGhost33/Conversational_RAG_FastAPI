from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from src.agentic_rag.state import AgentState
from src.agentic_rag.nodes import route_initial_intent, greeting_response, web_entry, lds_retriever_node, rewrite_question, generate_answer, decide_web_or_respond, grade_documents
from src.agentic_rag.tools import web_search

workflow = StateGraph(AgentState)

workflow.add_node("route_intent", route_initial_intent)
workflow.add_node("greeting", greeting_response)
workflow.add_node("web_entry", web_entry)
workflow.add_node("lds_retriever_node",lds_retriever_node)
workflow.add_node("rewrite_question",rewrite_question)
workflow.add_node("generate_answer",generate_answer)
workflow.add_node("decide_web", decide_web_or_respond)
workflow.add_node("web_search", ToolNode([web_search]))


workflow.add_edge(START, "route_intent")

workflow.add_conditional_edges(
    "route_intent",
    lambda state: state["intent"],
    {
        "greeting": "greeting",
        "lds_religion": "lds_retriever_node",
        "web_search": "web_entry",
    }
)


# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "lds_retriever_node",
    grade_documents,
    {
        "generate_answer": "generate_answer",
        "rewrite_question": "rewrite_question",
        "web_fallback": "decide_web",
    }
)

workflow.add_conditional_edges(
    "decide_web",
    tools_condition,
    {
        "tools": "web_search",
        END: END,
    }
)

workflow.add_edge("web_search", "generate_answer")
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "lds_retriever_node")

graph = workflow.compile()


## Test the flow
# for chunk in graph.stream(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Who won icc t20 world cup 2021",
#             }
#         ],
#         "retry_count": 0,
#         "intent": ""
#     }
# ):
#     for node, update in chunk.items():
#         print("Update from node", node)

#         if "messages" in update:
#             update["messages"][-1].pretty_print()
#         else:
#             print(update)

#         print("\n\n")