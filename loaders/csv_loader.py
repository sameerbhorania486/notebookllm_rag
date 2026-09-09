from langchain_community.document_loaders import CSVLoader


def load_csv(file_path):
    loader = CSVLoader(file_path=file_path)
    documents = loader.load()

    return documents


if __name__ == "__main__":
    documents = load_csv("data/employees.csv")

    print(f"Total documents loaded: {len(documents)}")

    for doc in documents:
        print(doc.page_content)
        print("-" * 50)