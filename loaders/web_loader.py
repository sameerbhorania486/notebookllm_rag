from langchain_community.document_loaders import WebBaseLoader


def load_web(url: str):
    """
    Load content from a web page.
    """
    loader = WebBaseLoader(url)

    documents = loader.load()

    return documents


if __name__ == "__main__":
    documents = load_web("https://www.python.org/")

    print(f"Total documents loaded: {len(documents)}")

    for doc in documents:
        print(doc.page_content[:2000])
        print("-" * 50)