from email import message
from threading import Thread
from typing import Generator, List
import uuid

from constants.config import (
    LLM_MODEL_NAME,
    TORCH_DEVICE,
    USE_QUANT,
    MODEL_OPTIMIZATION,
)

from utils.timing import measure_time
from utils.tools import tools_define

from utils.stream_helper import process_stream_content

from utils.tools.tools_helper import extract_tool_calls_and_reupdate_output


def load_model():
    try:
        from transformers.models.auto.modeling_auto import AutoModelForCausalLM
        from transformers.models.auto.tokenization_auto import AutoTokenizer
        from transformers.generation.streamers import TextIteratorStreamer
        from transformers.utils.quantization_config import BitsAndBytesConfig
    except ImportError:
        raise ImportError("transformers is not installed. Please install it using 'pip install transformers'.")
    global _model, _tokenizer

    # Configure model loading based on device
    try:
        with measure_time("Load model"):
            if USE_QUANT:
                print("Using quantization")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=MODEL_OPTIMIZATION["torch_dtype"],
                    bnb_4bit_use_double_quant=True,
                    use_flash_attention_2=True,
                )
                _model = AutoModelForCausalLM.from_pretrained(
                    LLM_MODEL_NAME,
                    torch_dtype=MODEL_OPTIMIZATION["torch_dtype"],
                    device_map="auto",
                    quantization_config=quantization_config,
                    low_cpu_mem_usage=MODEL_OPTIMIZATION["low_cpu_mem_usage"],
                    use_cache=MODEL_OPTIMIZATION["use_cache"],
                    # max_memory={0: "4GiB"},  # Limit GPU memory usage
                )
            else:
                print("Not using quantization")
                _model = AutoModelForCausalLM.from_pretrained(
                    LLM_MODEL_NAME,
                    torch_dtype=MODEL_OPTIMIZATION["torch_dtype"],
                    device_map="auto",
                    low_cpu_mem_usage=MODEL_OPTIMIZATION["low_cpu_mem_usage"],
                    use_cache=MODEL_OPTIMIZATION["use_cache"],
                    # max_memory={0: "8GiB"},  # Limit GPU memory usage
                )

            # Configure tokenizer with appropriate settings
            _tokenizer = AutoTokenizer.from_pretrained(
                LLM_MODEL_NAME,
                use_fast=True,  # Use fast tokenizer for better performance
            )

            _model.eval()
    except Exception as e:
        print(f"Failed to load model or tokenizer: {str(e)}")
        _model = None
        _tokenizer = None
        raise


def clear_resources():
    global _model, _tokenizer
    _model = None
    _tokenizer = None


def generate(messages: List[dict], has_tool_call: bool = True) -> dict:

    if _model is None or _tokenizer is None:
        raise RuntimeError(
            "Model or tokenizer not initialized. Ensure load_model was called successfully."
        )

    # Prepare tools if enabled
    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    # Apply chat template
    formatted_prompt = _tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tool_choice=tool_choice,
        tokenize=False,
        add_generation_prompt=True,
    )

    try:
        # Tokenize input with optimized settings
        inputs = _tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,  # Adjust based on your needs
        ).to(TORCH_DEVICE)

        # Generate response with optimized settings
        output_ids = _model.generate(
            **inputs,
            max_new_tokens=4096,
            do_sample=False,
            # temperature=0.7,
            pad_token_id=_tokenizer.pad_token_id,
            eos_token_id=_tokenizer.eos_token_id,
            # use_cache=True,  # Enable KV cache for faster generation
            # num_beams=1,  # Use greedy decoding for faster inference
        )

        # Decode response
        output_text = _tokenizer.decode(
            output_ids[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )

        cleaned_output, tool_calls = extract_tool_calls_and_reupdate_output(output_text)

        # Create ChatResponse using from_llm_output
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

    except Exception as e:
        print(f"Error in create chat completion: {str(e)}")
        raise


def generate_stream(
    messages: List[dict], has_tool_call: bool = True
) -> Generator[dict, None, None]:
    if _model is None or _tokenizer is None:
        raise RuntimeError(
            "Model or tokenizer not initialized. Ensure load_model was called successfully."
        )

    # Prepare tools if enabled
    tools = tools_define.tools if has_tool_call else None
    tool_choice = "auto" if has_tool_call else "none"

    # Apply chat template
    formatted_prompt = _tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tool_choice=tool_choice,
        tokenize=False,
        add_generation_prompt=True,
    )

    try:
        # Tokenize input with optimized settings
        inputs = _tokenizer(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=4096,  # Adjust based on your needs
        ).to(TORCH_DEVICE)

        # Generate streaming output
        streamer = TextIteratorStreamer(
            _tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            do_sample=True,
            max_new_tokens=4096,
            pad_token_id=_tokenizer.pad_token_id,
            eos_token_id=_tokenizer.eos_token_id,
        )

        # Generate in background thread
        thread = Thread(target=_model.generate, kwargs=generation_kwargs)
        thread.start()

        # Create a generator that yields content from the streamer
        def content_generator():
            for content in streamer:
                yield content

        # Use the common stream processor
        yield from process_stream_content(content_generator())

    except Exception as e:
        print(f"Error in create stream chat completion: {str(e)}")
        yield {
            "choices": [{"delta": {"role": "assistant", "content": f"Error: {str(e)}"}}]
        }
