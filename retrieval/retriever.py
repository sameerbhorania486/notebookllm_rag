def create_retriever(
    vector_store,
    source_ids=None,
    k=4
):

    search_kwargs = {
        "k": k
    }

    if source_ids:
        search_kwargs["filter"] = {
            "source_id": {
                "$in": source_ids
            }
        }

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs
    )

    return retriever