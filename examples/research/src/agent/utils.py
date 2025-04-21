import httpx
from markdownify import markdownify

httpx_client = httpx.Client(follow_redirects=False, timeout=10)


def print_stream(stream):
    for ns, update in stream:
        print(f"Namespace '{ns}'")
        for node, node_updates in update.items():
            if node_updates is None:
                continue

            if isinstance(node_updates, (dict, tuple)):
                node_updates_list = [node_updates]
            elif isinstance(node_updates, list):
                node_updates_list = node_updates
            else:
                raise ValueError(node_updates)

            for node_updates in node_updates_list:
                print(f"Update from node '{node}'")
                if isinstance(node_updates, tuple):
                    print(node_updates)
                    continue
                messages_key = next(
                    (k for k in node_updates.keys() if "messages" in k), None
                )
                if messages_key is not None:
                    node_updates[messages_key][-1].pretty_print()
                else:
                    print(node_updates)

        print("\n\n")

    print("\n===\n")


def fetch_doc(url: str) -> str:
    """Fetch a document from a URL and return the markdownified text.

    Args:
        url (str): The URL of the document to fetch.

    Returns:
        str: The markdownified text of the document.
    """
    try:
        response = httpx_client.get(url, timeout=10)
        response.raise_for_status()
        return markdownify(response.text)
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        return f"Encountered an HTTP error: {str(e)}"

def search_web(query: str) -> str:
    """Perform a web search using DuckDuckGo Instant Answer API and return the top results.

    Args:
        query (str): The search query.

    Returns:
        str: A summary of the top results.
    """
    try:
        params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1, "skip_disambig": 1}
        response = httpx_client.get("https://api.duckduckgo.com/", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = []
        if "AbstractText" in data and data["AbstractText"]:
            results.append(f"Abstract: {data['AbstractText']}")
        if "RelatedTopics" in data and data["RelatedTopics"]:
            for topic in data["RelatedTopics"][:3]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(f"- {topic['Text']}")
        if not results:
            return "No relevant results found."
        return "\n".join(results)
    except Exception as e:
        return f"Web search failed: {str(e)}"
