from fastmcp import FastMCP

mcp = FastMCP("Programming Learning Server")

@mcp.tool
def search_topics(query: str) -> list[dict]:
    """Search programming topics by title or keyword."""
    
if __name__ == "__main__":
    mcp.run()