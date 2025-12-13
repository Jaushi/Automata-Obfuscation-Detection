# Utility functions

def search_dictionary(data, query):
    if not query:
        return data
    results = {}
    query_lower = query.lower()
    for key, value in data.items():
        if isinstance(value, dict):
            nested_results = search_dictionary(value, query)
            if nested_results:
                results[key] = nested_results
        elif isinstance(value, list):
            filtered = [item for item in value if query_lower in item.lower()]
            if filtered:
                results[key] = filtered
        elif query_lower in str(value).lower():
            results[key] = value
    return results