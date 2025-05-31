from typing import Generator, List, Dict, Any, Optional
import uuid
from utils.tools.tools_helper import extract_tool_calls_and_reupdate_output

def process_stream_content(
    content_stream: Generator[str, None, None],
    stream_id: Optional[str] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Common function to process streaming content and handle tool calls.
    
    Args:
        content_stream: Generator that yields content chunks
        stream_id: Optional ID for the stream. If not provided, a new UUID will be generated.
    
    Yields:
        Dictionary containing the processed stream response
    """
    if stream_id is None:
        stream_id = f"chatcmpl-{uuid.uuid4().hex}"
    
    accumulated_content = ""
    in_tool_call = False
    
    for content in content_stream:
        if not content or content.strip() == "":
            continue
        
        accumulated_content += content
        
        if "<tool_call>" in content:
            in_tool_call = True
        elif "</tool_call>" in content:
            in_tool_call = False
            # Process the complete tool call
            cleaned_output, tool_calls = extract_tool_calls_and_reupdate_output(accumulated_content)
            accumulated_content = cleaned_output
            
            yield {
                "id": stream_id,
                "choices": [
                    {
                        "delta": {
                            "role": "assistant",
                            "content": cleaned_output,
                            "tool_calls": tool_calls,
                        }
                    }
                ]
            }
            continue
        
        # If we're not in a tool call, yield the content as is
        if not in_tool_call:
            yield {
                "id": stream_id,
                "choices": [
                    {
                        "delta": {
                            "role": "assistant",
                            "content": content,
                            "tool_calls": None,
                        }
                    }
                ]
            } 