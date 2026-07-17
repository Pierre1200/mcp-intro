from fastmcp import FastMCP
import json
from pathlib import Path


mcp = FastMCP("Programming Learning Server")
DATA_PATH = Path(__file__).parent.parent / "data" / "topics.json"


@mcp.tool
def search_topics(query: str) -> list[dict]:
    """Search programming topics by title or keyword."""
    with open(DATA_PATH, "r") as f:
        topics = json.load(f)
    results = []
    for topic in topics:
        if query.lower() in topic["title"].lower() or any(query.lower() in keyword.lower() for keyword in topic.get("key_concepts", [])):
            results.append(topic)
    return results

@mcp.tool
def get_topic_details(topic_id: str) -> dict:
    """Get detailed information about a specific programming topic."""
    with open(DATA_PATH, "r") as f:
        topics = json.load(f)
    for topic in topics:
        if topic["id"] == topic_id:
            return topic
    return {"error": "Topic not found"} 

@mcp.resource("topics://catalog")
def get_topic_catalog() -> str:
    """Return the list of available topic ids and titles."""
    # Load topics.
    with open(DATA_PATH, "r") as f:
        topics = json.load(f)
    # Create a catalog of topic ids and titles.
    catalog = [{"id": topic["id"], "title": topic["title"]} for topic in topics]
    return json.dumps(catalog, indent=2)

if __name__ == "__main__":
    mcp.run()