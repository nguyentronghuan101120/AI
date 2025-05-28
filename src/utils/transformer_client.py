import os
from threading import Thread
from typing import Generator, List
import torch
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer
from constants.config import GGUF_FILE_NAME, LLM_MODEL_NAME, GGUF_REPO_ID, TORCH_DEVICE, USE_QUANT
from models.others.message import Message, Role
from models.responses.chat_response import ChatResponse
from transformers.generation.streamers import TextIteratorStreamer
from utils.timing import measure_time
from utils.tools import tools_define
from transformers.utils.quantization_config import BitsAndBytesConfig

if(USE_QUANT):
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL_NAME,
        torch_dtype="auto",
        device_map="auto",
        quantization_config=quantization_config,
    )
else:
    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL_NAME,
        torch_dtype="auto",
        device_map="auto",  # hoặc "cpu" nếu bạn muốn ép về CPU
    )

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)


def build_prompt(messages: List[Message]) -> str:
    return "\n".join([f"{m.role.value}: {m.content}" for m in messages])


def generate(messages: List[Message], has_tool_call: bool = True) -> ChatResponse:
    # Convert messages to prompt
    prompt = [message.to_map() for message in messages]

    # prompt = build_prompt(messages)
    # Prepare tools if enabled
    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    # Apply chat template
    formatted_prompt = tokenizer.apply_chat_template(
        prompt,
        tools=tools,
        tool_choice=tool_choice,
        tokenize=False,
        add_generation_prompt=True,
    )

    print("Starting create chat completion")
    try:
        with measure_time("Starting create chat completion"):
            # Tokenize input
            inputs = tokenizer(formatted_prompt, return_tensors="pt").to(TORCH_DEVICE)
            # Generate response
            output_ids = model.generate(
                **inputs,
                max_new_tokens=4096,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            # Decode response
            output_text = tokenizer.decode(
                output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
            )

            # Create ChatResponse using from_llm_output
            return ChatResponse.from_llm_output(
                {
                    "choices": [
                        {
                            "message": {
                                "role": Role.assistant.value,
                                "content": output_text,
                            }
                        }
                    ]
                }
            )
    except Exception as e:
        print(f"Error in create chat completion: {str(e)}")
        raise


def generate_stream(messages: List[Message]) -> Generator[ChatResponse, None, None]:
    # Convert messages to prompt
    prompt = [message.to_map() for message in messages]
    # Prepare tools
    tools = tools_define.tools
    # Apply chat template
    # formatted_prompt = tokenizer.apply_chat_template(
    #     prompt,
    #     tools=tools,
    #     tool_choice="auto",
    #     tokenize=False,
    #     add_generation_prompt=True,
    # )
    try:
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt").to(TORCH_DEVICE)
        # Generate streaming output

        streamer = TextIteratorStreamer(
            tokenizer, skip_prompt=True, skip_special_tokens=True
        )

        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            do_sample=True,
            max_new_tokens=4096,
            temperature=0.7,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

        # Generate in background thread
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        last_role = Role.assistant
        for new_text in streamer:
            # Format the chunk to match the expected structure
            chunk = {
                "choices": [{"delta": {"role": last_role.value, "content": new_text}}]
            }
            response, updated_role = ChatResponse.from_stream_chunk(chunk, last_role)
            if response.choices:  # Only yield if we have valid choices
                yield response
            if updated_role:
                last_role = updated_role
    except Exception as e:
        print(f"Error in create stream chat completion: {str(e)}")
        raise
