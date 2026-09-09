from langchain_community.document_loaders import PyPDFLoader
def load_pdf(file_path:str):
    """
    Load content from a PDF file.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents