from langchain_community.document_loaders import YoutubeLoader


def load_youtube(url):

    try:

        loader = YoutubeLoader.from_youtube_url(
            url,
            add_video_info=False,
            language=["en", "hi"]
        )

        documents = loader.load()

        if not documents:
            raise ValueError(
                "No transcript/content found for this YouTube video."
            )

        print(
            f"YouTube transcript loaded successfully: {len(documents)} document(s)"
        )

        return documents

    except Exception as e:

        print(
            f"YouTube loader error: {e}"
        )

        raise ValueError(
            f"Could not load YouTube transcript: {e}"
        )