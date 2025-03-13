from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import interrupt
from typing import Literal, List, TypedDict, Annotated
from langgraph.types import Command
from langchain_core.output_parsers import JsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel, Field
from rich import print as rprint
from dotenv import load_dotenv, find_dotenv

import time

# pip install "langgraph-cli[inmem]"
# Also you need to install rust

# Задайте авторизационные данные для подключения к GigaChat.
# Вы также можете использовать другие способы авторизации.
# Подробнее о способах авторизации см. в документации к пакет gigachat:
# https://github.com/ai-forever/gigachat
import os

load_dotenv(find_dotenv())

from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_gigachat.embeddings import GigaChatEmbeddings
from langchain_openai.chat_models import ChatOpenAI

# LLM GigaChat
giga = GigaChat(model="GigaChat-2-Max",
                verify_ssl_certs=False,
                profanity_check=False,
                # base_url="https://gigachat.sberdevices.ru/v1",
                base_url="https://gigachat.ift.sberdevices.ru/v1",
                # top_p=0,
                streaming=False,
                max_tokens=8000,
                temperature=1,
                timeout=600)

from langchain.agents import tool
from typing import Dict, Literal
from langgraph.checkpoint.memory import MemorySaver

cards_db = {
    "2202208XXXX11824": {"type": "МИР", "blocked": False},
    "4508103XXXX14732": {"type": "VISA", "blocked": False},
}

@tool
def get_cards() -> dict:
    """Возвращает состояние банковских карт пользователя в виде dict, где ключем является id карты"""
    print(">>> called get_cards")
    return cards_db

@tool
def block_card(card_id: str, reason: Literal["lost", "not_used", "stolen"]) -> str:
    """Блокирует карту пользователя по номеру карты (card_id).
Обязательно уточни у пользователи причину блокировки карты.
reason - причина блокировки."""
    print(f">>> called block_card({card_id}, {reason})")
    if card_id in cards_db:
      cards_db[card_id]["block"] = True
      return f"Карта {card_id} успешно заблокирована"
    else:
      return f"Неизвестная карта {card_id}"
  
from langgraph.prebuilt import create_react_agent

system = """Ты полезный банковский ассистент, который помогает пользователю работать с картами банка.
Если пользователь просит заблокировать карту, обязательно уточни у него причину блокировки.
"""

agent = create_react_agent(giga, tools=[get_cards, block_card], checkpointer=MemorySaver(), prompt=system)