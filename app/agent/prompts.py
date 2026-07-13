# Tool Schemas matching the Google GenAI OpenAPI Function Declaration standard.
# The LLM reads these schemas to decide if it needs to select a tool,
# and to determine the exact arguments and types needed to execute it.

WEATHER_TOOL_SCHEMA = {
    "name": "get_weather",
    "description": "Retrieve current weather information (temperature, condition, humidity) for a city or location.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "location": {
                "type": "STRING",
                "description": "The city or location name to query weather for (e.g. 'Bengaluru', 'Tokyo', 'New York')."
            }
        },
        "required": ["location"]
    }
}

TIME_TOOL_SCHEMA = {
    "name": "get_current_time",
    "description": "Return the current local time for a city or location.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "location": {
                "type": "STRING",
                "description": "The city or location name to get the local time for (e.g. 'London', 'Tokyo')."
            }
        },
        "required": ["location"]
    }
}

CALCULATOR_TOOL_SCHEMA = {
    "name": "calculate",
    "description": "Safely evaluate mathematical expressions containing basic arithmetic operators (+, -, *, /, **, %).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "expression": {
                "type": "STRING",
                "description": "The mathematical expression to safely evaluate (e.g., '45000 * 18 / 100'). Commas in numbers are handled."
            }
        },
        "required": ["expression"]
    }
}

LOCATION_TOOL_SCHEMA = {
    "name": "get_location_information",
    "description": "Retrieve basic geographic details (latitude, longitude, city, country) for a place or famous landmark.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "location": {
                "type": "STRING",
                "description": "The landmark or place name to query (e.g. 'Eiffel Tower', 'Taj Mahal')."
            }
        },
        "required": ["location"]
    }
}

# Combined registry schema list to pass directly to Gemini
ALL_TOOL_SCHEMAS = [
    WEATHER_TOOL_SCHEMA,
    TIME_TOOL_SCHEMA,
    CALCULATOR_TOOL_SCHEMA,
    LOCATION_TOOL_SCHEMA
]

SYSTEM_INSTRUCTION = (
    "You are a helpful multi-tool assistant. "
    "You have access to a set of tools to query live weather, local time, locations, and perform math operations. "
    "Use them when required, but answer directly for questions that do not require external tools."
)
