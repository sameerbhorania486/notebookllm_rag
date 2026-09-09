from ingestion.pipeline import run_ingestion
from retrieval.retriever import create_retriever
from backend.rag_chain import create_rag_chain, create_llm


# Create vector store
vector_store = run_ingestion(
    "csv",
    "data/employees.csv"
)
# Create retriever
retriever = create_retriever(vector_store)

# Create LLM
llm = create_llm()

# Create RAG chain
ask = create_rag_chain(retriever, llm)

print("\n🤖 NotebookLLM RAG Assistant")
print("Type 'exit' to stop.\n")

while True:
    question = input("You: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    answer = ask(question)

    print(f"\nAI: {answer}\n")