import json
from typing import Dict, Any, List
from google.genai import types

from app.services.llm_service import llm_service
from app.agent.prompts import SYSTEM_INSTRUCTION, ALL_TOOL_SCHEMAS
from app.agent.state import AgentState

# Import tool functions
from app.tools.weather_tool import get_weather
from app.tools.time_tool import get_current_time
from app.tools.calculator_tool import calculate
from app.tools.location_tool import get_location_information

# The Tool Registry maps string identifiers to Python functions
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "calculate": calculate,
    "get_location_information": get_location_information
}

MAX_AGENT_STEPS = 5

# Global session memory registry to maintain short-term memory across API requests.
# Maps session_id (str) -> List of types.Content objects.
SESSION_MEMORY: Dict[str, List[types.Content]] = {}

def run_agent(user_query: str, session_id: str = "default_session") -> Dict[str, Any]:
    """
    Stateful agent loop utilizing a global session memory store to preserve
    conversational history and track execution metadata using AgentState.
    """
    # 1. Retrieve or initialize conversation history for the session ID
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = []
        
    history = SESSION_MEMORY[session_id]
    
    # 2. Structure new user message and append to persistent history
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_query)]
    )
    history.append(user_content)
    
    # 3. Initialize AgentState to track this execution turn
    state = AgentState(
        current_query=user_query,
        messages=history,
        iteration_count=0
    )
    
    # 4. Execute the Agent Loop
    while state.iteration_count < MAX_AGENT_STEPS:
        state.iteration_count += 1
        
        # Query Gemini passing full history including previous turns
        response = llm_service.generate_response(
            contents=history,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=ALL_TOOL_SCHEMAS
        )
        
        if response.function_calls:
            model_content = response.candidates[0].content
            history.append(model_content)
            
            for call in response.function_calls:
                tool_name = call.name
                if tool_name not in state.tools_used:
                    state.tools_used.append(tool_name)
                    
                tool_args = dict(call.args) if call.args else {}
                
                # Execute tool
                if tool_name in TOOL_REGISTRY:
                    func = TOOL_REGISTRY[tool_name]
                    try:
                        tool_result = func(**tool_args)
                        state.tool_results.append({tool_name: tool_result})
                    except Exception as e:
                        tool_result = {"error": f"Execution failed: {str(e)}"}
                        state.errors.append(f"Tool {tool_name} failed: {str(e)}")
                else:
                    tool_result = {"error": f"Tool '{tool_name}' not found."}
                    state.errors.append(f"Tool {tool_name} not registered.")
                
                # Append result to history
                tool_content = types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=tool_name,
                            response=tool_result
                        )
                    ]
                )
                history.append(tool_content)
                
            continue
            
        else:
            # Complete conversational response generated
            state.final_answer = response.text if hasattr(response, 'text') else str(response)
            
            # Print current state log to console for debugging and transparency
            print(f"\n--- STATE LOG FOR SESSION {session_id} ---")
            print(f"Query: {state.current_query}")
            print(f"Tools Used: {state.tools_used}")
            print(f"Iterations: {state.iteration_count}")
            print(f"Final Response: {state.final_answer}")
            print(f"History Size: {len(history)} messages")
            print("-----------------------------------------\n")
            
            return {
                "response": state.final_answer,
                "tools_used": state.tools_used,
                "agent_iterations": state.iteration_count,
                "session_id": session_id
            }
            
    # Safeguard limit exceeded
    error_msg = f"[Safeguard Exceeded] Agent reached maximum iteration limit of {MAX_AGENT_STEPS} steps."
    state.errors.append(error_msg)
    
    return {
        "response": error_msg,
        "tools_used": state.tools_used,
        "agent_iterations": state.iteration_count,
        "session_id": session_id
    }
