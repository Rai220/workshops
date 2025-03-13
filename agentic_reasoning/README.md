# Пример агента для LangGraph в виде микросервиса
Для запуска:
1. Изучите документацию Doc: https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/
2. Установите langgraph-cli: ```pip install --upgrade "langgraph-cli[inmem]"``` (на маке нужет rust!)
3. Создайте venv
4. Установите зависимости (см. agentic_reasoning.ipynb)
5. Переименуйте .env.example в .env и настройте креды
6. Запустите через langgraph dev ```langgraph dev```
7. Можно обратиться через curl:
```bash
curl -s --request POST \
    --url "http://localhost:2024/runs/stream" \
    --header 'Content-Type: application/json' \
    --data "{
        \"assistant_id\": \"agent\",
        \"input\": {
            \"messages\": [
                {
                    \"role\": \"human\",
                    \"content\": \"Какие у меня есть банковские карты?\"
                }
            ]
        },
        \"stream_mode\": \"updates\"
    }" 
```