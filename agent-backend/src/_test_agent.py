"""
Production LangGraph Agent for Playwright POM Generation
"""

from typing import TypedDict, Annotated, Literal
from pydantic import SecretStr
import json

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import Config
from utils._load_prompt import load_prompt
from utils._code_extractor import extract_python_code


# =======================
# Agent State
# =======================
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task_type: Literal["generate_pom", "clarification_needed", "unknown"]
    elements: list[str]
    generated_code: str


# =======================
# Playwright Agent
# =======================
class PlaywrightAgent:
    """
    LangGraph-based agent for generating Playwright Page Object Models
    """

    def __init__(
        self,
        planner_prompt: str = Config.PLANNER_PROMPT,
        codegen_prompt: str = Config.CODEGEN_PROMPT,
    ):
        print("Initializing PlaywrightAgent...")

        self.llm = ChatGroq(
            model=Config.MODEL_NAME,
            api_key=SecretStr(Config.GROQ_API_KEY or ""),
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
        )

        self.planner_prompt = load_prompt("playwright", planner_prompt)
        self.codegen_prompt = load_prompt("playwright", codegen_prompt)

        self.graph = self._build_graph()
        print("PlaywrightAgent initialized")

    # =======================
    # Graph Definition
    # =======================

    def _build_graph(self):
        """Build and compile the LangGraph workflow"""
        graph = StateGraph(AgentState)

        graph.add_node("planner", self._planner_node)
        graph.add_node("code_generator", self._code_generator_node)
        graph.add_node("finalizer", self._finalizer_node)

        graph.add_edge(START, "planner")
        graph.add_conditional_edges(
            "planner",
            self._route_from_planner,
            {
                "generate": "code_generator",
                "clarify": "finalizer",
            },
        )
        graph.add_edge("code_generator", "finalizer")
        graph.add_edge("finalizer", END)

        return graph.compile()

    # =======================
    # Nodes
    # =======================
    def _planner_node(self, state: AgentState) -> AgentState:
        print("📋 Planner: Analyzing request")

        user_message = state["messages"][-1].content

        messages = [
            SystemMessage(content=self.planner_prompt),
            HumanMessage(content=f"User Request:\n{user_message}"),
        ]

        response = self.llm.invoke(messages)

        try:
            
            content = response.content
            if isinstance(content, list):
            
                content = str(content[0]) if content else "{}"
            
            # Extract JSON if wrapped in code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)

            state["task_type"] = plan.get("task_type", "unknown")
            state["elements"] = plan.get("elements_to_find", [])

            state["messages"].append(
                AIMessage(content=f"Planning complete: {plan.get('reasoning', '')}")
            )

        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            print(f"Planner JSON parsing failed: {e}")
            state["task_type"] = "clarification_needed"
            state["elements"] = []
            response_text = str(response.content) if isinstance(response.content, list) else response.content
            state["messages"].append(AIMessage(content=response_text))

        return state

    def _code_generator_node(self, state: AgentState) -> AgentState:
        print("Code Generator: Generating POM code")

        user_request = state["messages"][0].content
        elements = ", ".join(state.get("elements", []))

        messages = [
            SystemMessage(content=self.codegen_prompt),
            HumanMessage(content=f"""
User Request:
{user_request}

Identified UI Elements:
{elements}
"""),
        ]

        response = self.llm.invoke(messages)
        content = response.content
        if isinstance(content, list):
            content = str(content[0]) if content else ""
        
        state["generated_code"] = extract_python_code(content)

        state["messages"].append(
            AIMessage(content="Playwright POM code generated successfully")
        )

        return state

    def _finalizer_node(self, state: AgentState) -> AgentState:
        print("Finalizer: Preparing response")

        if state["task_type"] == "generate_pom" and state.get("generated_code"):
            final_message = f"""Here is your Playwright Page Object Model:
````python
{state['generated_code']}
```"""
        else:
            # ✅ FIX 4: Handle last message content being a list
            last_content = state["messages"][-1].content
            if isinstance(last_content, list):
                final_message = str(last_content[0]) if last_content else "No response"
            else:
                final_message = last_content

        state["messages"].append(AIMessage(content=final_message))
        return state

    # =======================
    # Routing
    # =======================
    def _route_from_planner(self, state: AgentState) -> Literal["generate", "clarify"]:
        return "generate" if state["task_type"] == "generate_pom" else "clarify"

    # =======================
    # Public API
    # =======================
    def process_request(self, user_prompt: str) -> dict:
        try:
            initial_state: AgentState = {
                "messages": [HumanMessage(content=user_prompt)],
                "task_type": "unknown",
                "elements": [],
                "generated_code": "",
            }

            final_state = self.graph.invoke(initial_state)
            final_content = final_state["messages"][-1].content
            if isinstance(final_content, list):
                final_content = str(final_content[0]) if final_content else "No response"

            return {
                "success": True,
                "task_type": final_state["task_type"],
                "generated_code": final_state.get("generated_code"),
                "response": final_content,
            }

        except Exception as e:
            print(f"Error in process_request: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"Error occurred: {e}",
            }


# =======================
# Standalone Test
# =======================

if __name__ == "__main__":
    agent = PlaywrightAgent()

    result = agent.process_request(
        "Generate a Page Object Model for a login page with username, password, and login button"
    )

    if result["success"]:
        print("\nSuccess!")
        print(f"Task Type: {result['task_type']}")
        print(f"\nResponse:\n{result['response']}")
    else:
        print(f"\nError: {result['error']}")