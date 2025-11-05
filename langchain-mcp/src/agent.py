from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "stdio",  # Local subprocess communication
            "command": "python",
            "args": ["./src/mcp/weather.py"],
        }
    }
)

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


async def agent():
    tools = await client.get_tools()
    return create_agent(
        llm,
        tools=tools,
    )
