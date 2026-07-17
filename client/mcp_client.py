import asyncio
from fastmcp import Client

SERVER_PATH = "server/learning_server.py"


async def main():
    client = Client(SERVER_PATH)

    async with client:
        # 1. Liste des tools disponibles
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # 2. Test search_topics avec une requête valide
        search_result = await client.call_tool("search_topics", {"query": "decorators"})
        print("Search result:", search_result)

        # 3. Test get_topic_details avec un id valide
        details_result = await client.call_tool("get_topic_details", {"topic_id": "python-decorators"})
        print("Details result:", details_result)

        # 4. Test avec un id INVALIDE (vérifie que ça ne plante pas)
        invalid_result = await client.call_tool("get_topic_details", {"topic_id": "invalid-id"})
        print("Invalid id result:", invalid_result)

        # 5. Lecture de la resource catalogue
        catalog = await client.read_resource("topics://catalog")
        print("Catalog:", catalog)


if __name__ == "__main__":
    asyncio.run(main())