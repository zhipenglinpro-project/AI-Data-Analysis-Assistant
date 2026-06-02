def enrich_query_with_context(
    parsed_query,
    last_parsed_query
):
    if (
        parsed_query.get("intent") == "unknown"
        and last_parsed_query
    ):
        return last_parsed_query

    return parsed_query