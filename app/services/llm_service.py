from google import genai
from typing import Any
from app import config

class LLMService:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please create a '.env' file in the "
                "project root containing GEMINI_API_KEY=your_api_key"
            )
        # Initialize Google GenAI client
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model_name = config.GEMINI_MODEL

    def generate_response(self, contents: Any, system_instruction: str = None, tools: list = None):
        """
        Generate content using Gemini API, with optional system instructions and manual tool schemas.
        Supports both simple string prompts and list of Content objects for multi-turn history.
        """
        from google.genai import types
        
        config_args = {}
        config_params = {}
        
        if system_instruction:
            config_params["system_instruction"] = system_instruction
            
        if tools:
            # Convert manual dictionaries into Google GenAI FunctionDeclarations
            declarations = []
            for tool in tools:
                declarations.append(
                    types.FunctionDeclaration(
                        name=tool["name"],
                        description=tool["description"],
                        parameters=types.Schema(
                            type=tool["parameters"]["type"],
                            properties={
                                k: types.Schema(
                                    type=v["type"],
                                    description=v.get("description", "")
                                )
                                for k, v in tool["parameters"]["properties"].items()
                            },
                            required=tool["parameters"].get("required", [])
                        )
                    )
                )
            
            # Wrap in types.Tool object list
            config_params["tools"] = [types.Tool(function_declarations=declarations)]
            
        if config_params:
            config_args["config"] = types.GenerateContentConfig(**config_params)
            
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                **config_args
            )
            return response
        except Exception as e:
            # We return a mock/dummy response structure containing the error message to avoid crashing
            class ErrorResponse:
                def __init__(self, err):
                    self.text = f"Error contacting Gemini LLM: {err}"
                    self.function_calls = None
            return ErrorResponse(str(e))


# Singleton instance
llm_service = LLMService()
