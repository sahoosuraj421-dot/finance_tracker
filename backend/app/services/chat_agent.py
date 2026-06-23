import uuid
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from sqlalchemy.orm import Session

from app.config import settings
from app.tools.finance_tools import create_finance_tools

SYSTEM_PROMPT = """You are FinTrack AI, a helpful personal finance assistant embedded in a finance tracker app.

You help users understand their spending, income, budgets, and financial patterns. You have access to tools that can:
- Summarize finances and spending by category
- Detect recurring expenses (subscriptions, bills)
- Compare spending between months
- Check and set budget limits
- Add and search transactions
- Show recent activity

Guidelines:
- Be concise, friendly, and actionable
- Use Indian Rupee (₹) amounts formatted with Indian comma grouping (e.g. ₹1,23,456.78)
- When users ask about their data, ALWAYS use the appropriate tool first
- Suggest practical savings tips when spending seems high
- If no data exists, guide users to upload a CSV/XLSX file or add transactions manually
- For date ranges, use YYYY-MM-DD format; for months use YYYY-MM format
"""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_finance_agent(db: Session):
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Set it in your .env file.")

    tools = create_finance_tools(db)
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.3,
    )
    llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    def call_model(state: AgentState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def run_chat(db: Session, message: str, history: list[dict] | None = None) -> tuple[str, list[str]]:
    agent = build_finance_agent(db)
    messages: list[BaseMessage] = []

    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=message))

    result = agent.invoke({"messages": messages})
    final_messages = result["messages"]

    tool_calls_used = []
    for msg in final_messages:
        if isinstance(msg, ToolMessage):
            tool_calls_used.append(msg.name)

    reply = ""
    for msg in reversed(final_messages):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            reply = msg.content if isinstance(msg.content, str) else str(msg.content)
            break

    if not reply:
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                reply = msg.content if isinstance(msg.content, str) else str(msg.content)
                break

    return reply or "I couldn't generate a response. Please try again.", tool_calls_used


def new_session_id() -> str:
    return str(uuid.uuid4())
