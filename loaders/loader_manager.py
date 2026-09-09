from loaders.pdf_loader import load_pdf
from loaders.text_loader import load_text
from loaders.csv_loader import load_csv
from loaders.web_loader import load_web
from loaders.youtube_loader import load_youtube


def load_source(source_type: str, source: str):
    """
    Load documents based on the source type.
    """

    source_type = source_type.lower()

    if source_type == "pdf":
        return load_pdf(source)

    elif source_type == "txt":
        return load_text(source)

    elif source_type == "csv":
        return load_csv(source)

    elif source_type == "web":
        return load_web(source)

    elif source_type == "youtube":
        return load_youtube(source)

    else:
        raise ValueError(
            f"Unsupported source type: {source_type}"
        )