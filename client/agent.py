import asyncio
import sys
from pathlib import Path
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

APP_NAME = "programming_learning_agent"
USER_ID = "local_user"

# Connexion au serveur MCP en stdio (le sous-processus est lancé automatiquement)
mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["server/learning_server.py"],
        ),
    ),
    tool_filter=["search_topics", "get_topic_details"],
)

study_agent = Agent(
    name="study_assistant_agent",
    model=LiteLlm(model="ollama_chat/qwen3:8b"),
    instruction=(
        "You are a programming study assistant. "
        "When the user asks about a topic, first use the MCP tools to search for "
        "a matching topic and retrieve its details. "
        "Use the returned MCP data to answer. Include prerequisites, key concepts, "
        "common mistakes, and one practice idea when available. "
        "Do not invent topic details that were not provided by the MCP server. "
        "If no topic matches, explain that clearly."
        "Respond in a concise and clear manner, suitable for a beginner programmer and in french."
    ),
    tools=[mcp_tools],
)


async def run_agent(agent, message_text):
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    user_message = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_text = ""
    async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=user_message):
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            is_thought = getattr(part, "thought", None)
            if not is_thought and part.text:
                final_text = part.text

    return final_text


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "I want to study Python decorators. What should I review first?"
    response = asyncio.run(run_agent(study_agent, question))
    print(response)
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)  # crée output/ si besoin
    (output_path / "sample_agent_response.md").write_text(response)


if __name__ == "__main__":
    main()