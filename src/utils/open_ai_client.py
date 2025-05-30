from typing import Generator, List
import uuid
import openai

from utils.tools import tools_define
from utils.tools.tools_helper import extract_tool_calls_and_reupdate_output

open_ai_client = openai.OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="none",
)

def generate(messages: List[dict], has_tool_call: bool = True) -> dict:
    response = open_ai_client.chat.completions.create(
        messages=messages, # type: ignore
        model="my-model",
        tools=tools_define.tools if has_tool_call else None, # type: ignore
    ).model_dump()
    
    cleaned_output, tool_calls = extract_tool_calls_and_reupdate_output(response.get("choices", [])[0].get("message", {}).get("content", ""))
    
    return {
                "id": f"chatcmpl-{uuid.uuid4().hex}",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": cleaned_output,
                            "tool_calls": tool_calls,
                        },
                    }
                ],
            }

def generate_stream(messages: List[dict], has_tool_call: bool = True) -> Generator[dict, None, None]:
    response = open_ai_client.chat.completions.create(
        messages=messages, # type: ignore
        model="my-model",
        tools=tools_define.tools if has_tool_call else None, # type: ignore
        stream=True,
    )
    
    id = f"chatcmpl-{uuid.uuid4().hex}"
    accumulated_content = ""
    in_tool_call = False
    
    for chunk in response:
        chunk_dict = chunk.model_dump()
        content = chunk_dict.get("choices", [])[0].get("delta", {}).get("content", "")
        
        if content:
            accumulated_content += content
            
            # Check if we're in a tool call
            if "<tool_call>" in content:
                in_tool_call = True
            elif "</tool_call>" in content:
                in_tool_call = False
                # Process the complete tool call
                cleaned_output, tool_calls = extract_tool_calls_and_reupdate_output(accumulated_content)
                accumulated_content = cleaned_output
                
                yield {
                    "id": id,
                    "choices": [
                        {
                            "delta": {
                                "role": "assistant",
                                "content": cleaned_output,
                                "tool_calls": tool_calls,
                            },
                        }
                    ],
                }
                continue
        
        # If we're not in a tool call, yield the content as is
        if not in_tool_call:
            yield {
                "id": id,
                "choices": [
                    {
                        "delta": {
                            "role": "assistant",
                            "content": content,
                            "tool_calls": None,
                        },
                    }
                ],
            }


