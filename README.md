# Utility AI Agent — Learn Agentic AI from First Principles

A lightweight, multi-tool AI Agent built from scratch using **pure Python, FastAPI, and the Gemini API** (without high-level frameworks like LangChain or LangGraph). 

The goal of this repository is to demonstrate and study the core mechanics of **Agentic AI**—such as tool schemas, dynamic function routing, state tracking, and short-term conversational memory—completely from first principles.

---

## 🏗️ Architecture Flow

This project exposes a single chat endpoint `/chat` via FastAPI. Unlike traditional API gateways that hardcode route logic (`if "weather" in query`), this agent uses the **ReAct (Reason + Act) pattern** to decide execution paths dynamically at runtime.

```text
Postman / Client
     │
     ▼ (HTTP POST /chat)
FastAPI Endpoint (api_chat)
     │
     ▼ (passes query & session ID)
Agent Controller (run_agent) ◄──────────────────────────────┐
     │                                                      │
     ▼ (packages query + tool schemas + history)            │ If Gemini
Gemini LLM (Brain)                                          │ requests a
     │                                                      │ Tool Call
     ├─► [NO Tool Calls Needed] ──► Returns Final Answer ───┼─► Exit Loop
     │                                                      │
     └─► [Tool Calls Needed] ──► Returns Tool Call Request  │
                                   │                        │
                                   ▼                        │
                         Registry Match & Exec ─────────────┘
                         (Python Body/Hands runs local API)
```

---

## 🛠️ Built-in Python Tools

The agent is equipped with four core capabilities implemented as standalone Python functions:

1. **Weather Tool** (`get_weather`): Geocodes location names and fetches real-time temperature, condition, and humidity using the free Open-Meteo REST API.
2. **Current-Time Tool** (`get_current_time`): Resolves location timezone dynamically using Open-Meteo Geocoding, and computes local time using Python's standard `zoneinfo` (with Windows `tzdata` fallback).
3. **Calculator Tool** (`calculate`): Safely evaluates mathematical expressions using Python's `ast` (Abstract Syntax Tree) module to restrict operations and prevent unsafe arbitrary code execution (`eval` hacks).
4. **Location Tool** (`get_location_information`): Converts places or tourist landmarks (e.g. "Eiffel Tower") to coordinates using a hybrid local landmark registry with an Open-Meteo API fallback.

---

## 🧠 Core Agentic Concepts Implemented

* **Manual Tool Definitions**: Built explicit JSON-like dictionary schemas for every function (specifying parameter names, descriptions, and required arguments) and passed them directly in the LLM configuration payloads.
* **Tool Registry Mapping**: Established a central lookup registry (`TOOL_REGISTRY`) that maps LLM string identifiers back to local executable Python functions.
* **State Management (`AgentState`)**: Created a Pydantic state container tracking execution metrics, lists of tools utilized, outputs captured, loop step counts, and errors.
* **Short-Term Conversational Memory**: Implemented a global in-memory session store (`SESSION_MEMORY`). Previous turns (user queries, tool call instructions, tool outputs, and conversational replies) are accumulated and sent to Gemini on subsequent turns, enabling the agent to resolve contextual references (such as identifying that *"there"* refers to a previously discussed city).

---

## 🚀 Setup and Run

### 1. Clone the repository & Create a Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=YOUR_REAL_API_KEY_HERE
GEMINI_MODEL=gemini-1.5-flash
```

### 4. Run the API Server
```bash
uvicorn app.main:app --reload
```

---

## 🧪 Demonstration Outputs (Postman Tests)

### Test 1: Vague Question & Automatic Parameter Clarification
**Request**:
```json
POST http://127.0.0.1:8000/chat
{
  "message": "What is the weather?",
  "session_id": "session-demo"
}
```
**Response**:
*The LLM reads the tool schema, notices the `location` parameter is marked as `required`, and automatically asks for clarification:*
```json
{
  "response": "Which city would you like to check the weather for?",
  "tools_used": [],
  "agent_iterations": 1,
  "session_id": "session-demo"
}
```

### Test 2: Memory & Context Resolution
**Request**:
```json
POST http://127.0.0.1:8000/chat
{
  "message": "For Bengaluru",
  "session_id": "session-demo"
}
```
**Response**:
*The LLM reads the conversation history of `session-demo`, resolves the location to Bengaluru, calls the tool, and outputs a conversational answer:*
```json
{
  "response": "The weather in Bengaluru is currently 25.4°C and Mainly clear, with 62% humidity.",
  "tools_used": [
    "get_weather"
  ],
  "agent_iterations": 2,
  "session_id": "session-demo"
}
```

### Test 3: Multi-Tool Query (Parallel Calling)
**Request**:
```json
POST http://127.0.0.1:8000/chat
{
  "message": "What is the weather and local time in Tokyo?",
  "session_id": "session-demo"
}
```
**Response**:
*Gemini requests both tools in parallel. Python loops through both requests, executes them, feeds both results back, and returns the final answer:*
```json
{
  "response": "In Tokyo, it is currently 28°C and rainy. The local time is 10:30 PM.",
  "tools_used": [
    "get_weather",
    "get_current_time"
  ],
  "agent_iterations": 2,
  "session_id": "session-demo"
}
```

### Test 4: Reset Session Memory
**Request**:
```http
DELETE http://127.0.0.1:8000/chat/session-demo
```
**Response**:
```json
{
  "message": "Successfully cleared session memory for session ID: session-demo"
}
```
*Note: Any subsequent request to `session-demo` will now start with a completely empty memory context.*

