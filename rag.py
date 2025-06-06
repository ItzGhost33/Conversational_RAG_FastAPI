from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from prompts import system_prompt, contextualize_q_system_prompt, qa_system_prompt
from llm import llm
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from chat_logger import insert_log, get_chat_history



def get_msg_content(msg):
    return msg.content


def rag_service(user_query,chat_history,retriever,session_id,db):

    chat_history = get_chat_history(session_id,db)
    contextualize_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
    

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_prompt,

    )


    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name = 'chat_history'),
        ("human", "{input}")
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    results = rag_chain.invoke({"input": user_query, "chat_history": chat_history})

    insert_log(session_id, user_query, results['answer'].strip(),db)
    chat_history = get_chat_history(session_id,db)

    return results['answer'].strip(),session_id,chat_history

# chat_history = []
# print(chat_history)
# print("-"*50)
# response, chat_history = rag_service( "i need to know about gambling in LDS teachings",chat_history)
# print(response)
# print("-"*50)
# print(chat_history)
# print("-"*50)
# response, chat_history = rag_service( "Is that acceptable in LDS teachings?",chat_history)
# print(response)
# print("-"*50)
# print(chat_history)


 
