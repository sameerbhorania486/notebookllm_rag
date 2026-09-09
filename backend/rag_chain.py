import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def create_llm():
    """
    Create the Groq LLM.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env")

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key
    )

    return llm

###
from langchain_core.prompts import ChatPromptTemplate


def create_rag_chain(retriever, llm):
    """
    Create a RAG chain using retriever and LLM.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful AI assistant.

        Answer the user's question using only the context provided below.
        If the answer is not available in the context, say:
        "I don't have enough information in the provided sources."

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
    )

    def format_documents(documents):
        return "\n\n".join(
            document.page_content
            for document in documents
        )

    def ask(question):
        documents = retriever.invoke(question)

        context = format_documents(documents)

        response = llm.invoke(
            prompt.format_messages(
                context=context,
                question=question
            )
        )

        return response.content

    return ask