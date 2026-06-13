"""
THE AI AGENT — This is the heart of ResearchBot.

What makes this an "agent" vs a normal LLM call:

1. TOOLS: Gemini knows about web_search and read_webpage functions
2. DECISION: Gemini itself decides WHEN to call a tool and WITH WHAT arguments
3. LOOP: We keep running until Gemini decides it has enough info to write the report
4. AUTONOMY: We never tell it "search this" — it figures out what to search on its own

This is called "Function Calling" or "Tool Use" — the core concept behind all AI agents.
"""

import google.generativeai as genai
from google.generativeai import protos
from app.config import GEMINI_API_KEY, MAX_AGENT_ITERATIONS
from app.core.tools import execute_tool
from app.schemas import AgentStep

genai.configure(api_key=GEMINI_API_KEY)


# ─── Define the tools Gemini knows about ────────────────────────────────────
# This is a "menu" we give to Gemini. It reads these descriptions and
# decides on its own when to call each one.

TOOL_DECLARATIONS = protos.Tool(
    function_declarations=[
        protos.FunctionDeclaration(
            name="web_search",
            description="Search the web for recent information, news, research papers, or facts about a topic. Use this first to find relevant URLs.",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "query": protos.Schema(
                        type=protos.Type.STRING,
                        description="A specific search query. Be precise."
                    )
                },
                required=["query"]
            )
        ),
        protos.FunctionDeclaration(
            name="read_webpage",
            description="Read the full content of a specific webpage URL. Use this after web_search to get detailed information from a promising page.",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "url": protos.Schema(
                        type=protos.Type.STRING,
                        description="The full URL of the webpage to read."
                    )
                },
                required=["url"]
            )
        )
    ]
)


# ─── System Prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are ResearchBot, an autonomous AI research agent.

Your job: When given a research topic, investigate it thoroughly using your tools, then write a comprehensive, well-structured research report.

Your approach:
1. Start with 1-2 web searches to understand the topic and find good sources
2. Read 2-3 of the most relevant pages in detail
3. If you need more specific information, search again with a more targeted query
4. Once you have enough information, write a detailed report WITHOUT calling any more tools

Your final report must include:
- Executive Summary (2-3 sentences)
- Key Findings (5-7 bullet points)  
- Detailed Analysis (3-4 paragraphs)
- Current Trends & Future Outlook
- Sources Used (list the URLs you read)

Be thorough. Be accurate. Only report what you actually found in your research."""


# ─── The Agent Loop ──────────────────────────────────────────────────────────

def run_research_agent(topic: str) -> dict:
    """
    Run the full autonomous research agent loop.

    Returns a dict with:
    - report: the final research report text
    - steps: list of every action the agent took
    """
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[TOOL_DECLARATIONS],
        system_instruction=SYSTEM_PROMPT
    )

    chat = model.start_chat()
    steps: list[AgentStep] = []
    iterations = 0

    # Kick off the agent
    user_message = f"Research this topic and write a comprehensive report: {topic}"
    response = chat.send_message(user_message)

    # ── AGENT LOOP ──
    # Keep going as long as Gemini wants to call tools
    while iterations < MAX_AGENT_ITERATIONS:
        iterations += 1

        # Check if any part of the response is a tool call
        tool_call_found = False

        for part in response.parts:

            # ── TOOL CALL: Gemini wants to use a tool ──
            if hasattr(part, 'function_call') and part.function_call.name:
                fc = part.function_call
                tool_name = fc.name
                tool_args = dict(fc.args)
                tool_call_found = True

                # Log this step
                steps.append(AgentStep(
                    type="tool_call",
                    content=f"Calling {tool_name} with: {tool_args}",
                    tool_name=tool_name,
                    tool_args=tool_args
                ))

                print(f"[Agent] Calling tool: {tool_name}({tool_args})")

                # Actually execute the tool
                tool_result = execute_tool(tool_name, tool_args)

                # Log tool result
                steps.append(AgentStep(
                    type="tool_result",
                    content=tool_result[:500] + "..." if len(tool_result) > 500 else tool_result,
                    tool_name=tool_name
                ))

                # Send result back to Gemini so it can decide what to do next
                response = chat.send_message(
                    protos.Content(
                        parts=[protos.Part(
                            function_response=protos.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_result}
                            )
                        )]
                    )
                )
                break  # Process one tool call at a time

            # ── FINAL ANSWER: Gemini is done with tools, writing the report ──
            elif hasattr(part, 'text') and part.text and part.text.strip():
                steps.append(AgentStep(
                    type="final",
                    content="Research complete. Writing final report..."
                ))
                return {
                    "report": part.text,
                    "steps": steps
                }

        # If no tool call and no text found, get the text response
        if not tool_call_found:
            final_text = response.text if hasattr(response, 'text') else "Research complete."
            steps.append(AgentStep(type="final", content="Research complete. Writing final report..."))
            return {
                "report": final_text,
                "steps": steps
            }

    # Safety: If we hit max iterations, ask for a summary with what we have
    steps.append(AgentStep(type="final", content="Max iterations reached. Generating report from gathered data..."))
    final_response = chat.send_message(
        "You have reached the maximum number of tool calls. "
        "Write the best research report you can with the information gathered so far."
    )
    return {
        "report": final_response.text,
        "steps": steps
    }
