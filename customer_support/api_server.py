from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langgraph_swarm import create_swarm
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
import asyncio

app = FastAPI()

# Example: create your agents and swarm here
model = ChatOpenAI(model="gpt-4o")
# TODO: Replace with your actual agent creation logic
alice = ...  # create your agent(s)
bob = ...
checkpointer = InMemorySaver()
workflow = create_swarm([alice, bob], default_active_agent="Alice")
swarm_app = workflow.compile(checkpointer=checkpointer)

@app.post("/invoke")
async def invoke(request: Request):
    body = await request.json()
    messages = body.get("input", {}).get("messages", [])
    config = {"configurable": {"thread_id": body.get("thread_id", "1")}}
    # Optionally handle assistant_id, etc.

    def event_stream():
        # This is a simple example; adapt as needed for your streaming logic
        result = swarm_app.invoke({"messages": messages}, config)
        yield str(result)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
