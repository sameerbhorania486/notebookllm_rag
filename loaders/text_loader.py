from langchain_community.document_loaders import TextLoader


def load_text(file_path: str):
    """
    Load content from a text file.
    """
    loader = TextLoader(
        file_path,
        encoding="utf-8"
    )

    documents = loader.load()

    return documents