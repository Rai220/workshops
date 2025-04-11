from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent

from langchain_gigachat.chat_models.gigachat import GigaChat

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.runnables import RunnableConfig



# LLM GigaChat
giga = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    profanity_check=False,
    base_url="https://gigachat.sberdevices.ru/v1",
    # top_p=0,
    streaming=False,
    max_tokens=8000,
    temperature=1,
    timeout=600,
)


from contextlib import asynccontextmanager

DEFAULT_MCP_CONFIG = {
    "apple-shortcuts": {
        "args": ["-y", "mcp-server-apple-shortcuts"],
        "command": "npx",
        "transport": "stdio",
    }
}


class Configuration(BaseModel):
    system_prompt: str = Field(
        default="Ты полезный ассистент",
        description="Основной системный промпт",
        json_schema_extra={
            "langgraph_nodes": ["agent"],
            "langgraph_type": "prompt",
        },
    )
    mcp_config: dict = Field(
        default=DEFAULT_MCP_CONFIG,
        description="Конфигурация MCP",
    )


@asynccontextmanager
async def make_graph(config: RunnableConfig):
    async with MultiServerMCPClient(
        config.get("configurable", {}).get("mcp_config", DEFAULT_MCP_CONFIG)
    ) as client:
        agent = create_react_agent(
            giga,
            client.get_tools(),
            prompt=config.get("configurable", {}).get("system_prompt", ""),
            config_schema=Configuration,
        )
        yield agent
