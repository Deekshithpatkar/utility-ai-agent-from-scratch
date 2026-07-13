from fastapi import FastAPI, HTTPException
from app.schemas import (
    ChatRequest, ChatResponse,
    WeatherRequest, WeatherResponse,
    TimeRequest, TimeResponse,
    CalculatorRequest, CalculatorResponse,
    LocationRequest, LocationResponse
)
from app.tools.weather_tool import get_weather
from app.tools.time_tool import get_current_time
from app.tools.calculator_tool import calculate
from app.tools.location_tool import get_location_information
from app.agent.manual_agent import run_agent

app = FastAPI(
    title="Utility AI Agent API",
    description="API layer to call specific tools directly and chat with the AI Agent.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Utility AI Agent API. Use Postman to test endpoints."}

@app.post("/weather", response_model=WeatherResponse)
def api_weather(request: WeatherRequest):
    """Call the Stage 1 Weather Tool."""
    result = get_weather(request.location)
    if "error" in result:
        return WeatherResponse(location=request.location, error=result["error"])
    return WeatherResponse(**result)

@app.post("/time", response_model=TimeResponse)
def api_time(request: TimeRequest):
    """Call the Stage 1 Time Tool."""
    result = get_current_time(request.location)
    if "error" in result:
        return TimeResponse(location=request.location, error=result["error"])
    return TimeResponse(**result)

@app.post("/calculate", response_model=CalculatorResponse)
def api_calculate(request: CalculatorRequest):
    """Call the Stage 1 Calculator Tool."""
    result = calculate(request.expression)
    if "error" in result:
        return CalculatorResponse(expression=request.expression, error=result["error"])
    return CalculatorResponse(**result)

@app.post("/location", response_model=LocationResponse)
def api_location(request: LocationRequest):
    """Call the Stage 1 Location Tool."""
    result = get_location_information(request.location)
    if "error" in result:
        return LocationResponse(place=request.location, error=result["error"])
    return LocationResponse(**result)

@app.post("/chat", response_model=ChatResponse)
def api_chat(request: ChatRequest):
    """
    Main agent chat endpoint.
    Routes natural language queries through the agent, preserving session history.
    """
    result = run_agent(request.message, session_id=request.session_id)
    return ChatResponse(**result)
