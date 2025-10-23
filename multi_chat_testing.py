import os
import random
from glob import glob
from dotenv import load_dotenv
load_dotenv()

# Configuration
MODEL = "meta/llama-3.1-8b-instruct"  # Options: gemini-*, gpt-*, claude-*, deepseek-ai/*, mistralai/*, meta/*
TRIAL = 10

# Helper functions
def generate_multi_turn(model, conversation_history, new_prompt):
    if "gemini" in model:
        try:
            # Try new SDK first
            from google import genai
            client = genai.Client()
            conversation_history.append({"role": "user", "parts": [{"text": new_prompt}]})
            response = client.models.generate_content(model=model, contents=conversation_history)
            conversation_history.append({"role": "model", "parts": [{"text": response.text}]})
            return response.text
        except Exception as e:
            # Fall back to old SDK with chat
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                # Convert conversation history to old SDK format
                formatted_history = []
                for msg in conversation_history:
                    if "role" in msg:
                        role = "user" if msg["role"] == "user" else "model"
                        content = msg["parts"][0]["text"] if "parts" in msg else msg.get("content", "")
                        formatted_history.append({"role": role, "parts": [content]})
                model_obj = genai.GenerativeModel(model)
                chat = model_obj.start_chat(history=formatted_history)
                response = chat.send_message(new_prompt)
                conversation_history.append({"role": "user", "parts": [{"text": new_prompt}]})
                conversation_history.append({"role": "model", "parts": [{"text": response.text}]})
                return response.text
            except Exception as e2:
                raise Exception(f"Both Gemini SDKs failed. New SDK error: {e}. Old SDK error: {e2}")
    else:  # OpenAI-compatible (NVIDIA, OpenAI, Anthropic)
        from openai import OpenAI
        if model.startswith(("deepseek-ai/", "mistralai/", "meta/")):
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", 
                           api_key=os.getenv("NVIDIA_API_KEY"))
            max_tokens = 16384 if "deepseek" in model else (8192 if "mistral" in model else 4096)
            extra = {"extra_body": {"chat_template_kwargs": {"thinking": True}}} if "deepseek" in model else {}
        else:
            max_tokens = 4096
            extra = {}
            if "gpt" in model:
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                extra["top_p"] = 0.7
            else:  # Claude - doesn't support top_p
                client = OpenAI(base_url="https://api.anthropic.com/v1", 
                               api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        conversation_history.append({"role": "user", "content": new_prompt})
        # Newer GPT models use max_completion_tokens and don't support temperature/top_p
        if "gpt" in model and ("gpt-5" in model or model.startswith(("o1", "o3"))):
            completion = client.chat.completions.create(
                model=model, messages=conversation_history,
                max_completion_tokens=max_tokens, stream=False
            )
        else:
            completion = client.chat.completions.create(
                model=model, messages=conversation_history,
                temperature=0.2, max_tokens=max_tokens, stream=False, **extra
            )
        response_text = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": response_text})
        return response_text

def generate_single(model, prompt):
    if "gemini" in model:
        try:
            # Try new SDK first
            from google import genai
            client = genai.Client()
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            # Fall back to old SDK
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model_obj = genai.GenerativeModel(model)
                response = model_obj.generate_content(prompt)
                return response.text
            except Exception as e2:
                raise Exception(f"Both Gemini SDKs failed. New SDK error: {e}. Old SDK error: {e2}")
    elif model.startswith(("deepseek-ai/", "mistralai/", "meta/")):
        from openai import OpenAI
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", 
                       api_key=os.getenv("NVIDIA_API_KEY"))
        max_tokens = 16384 if "deepseek" in model else (8192 if "mistral" in model else 4096)
        extra = {"extra_body": {"chat_template_kwargs": {"thinking": True}}} if "deepseek" in model else {}
        completion = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            temperature=0.2, top_p=0.7, max_tokens=max_tokens, stream=False, **extra
        )
        return completion.choices[0].message.content
    else:
        from openai import OpenAI
        if "gpt" in model:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            # Newer models (gpt-5, o1, o3) use max_completion_tokens and don't support temperature/top_p
            if "gpt-5" in model or model.startswith(("o1", "o3")):
                completion = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=4096
                )
            else:
                completion = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}],
                    temperature=0.2, top_p=0.7, max_tokens=4096
                )
        else:  # Claude - doesn't support top_p
            client = OpenAI(base_url="https://api.anthropic.com/v1", 
                           api_key=os.getenv("ANTHROPIC_API_KEY"))
            completion = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}],
                temperature=0.2, max_tokens=4096
            )
        return completion.choices[0].message.content

# Setup paths
model_name = MODEL.replace("/", "-")
output_dir = f"multi_chat_responses/{model_name}/trial_{TRIAL}"
os.makedirs(output_dir, exist_ok=True)

# Load prompts (sorted alphabetically)
prompt_files = sorted(glob("preset_prompts/multi_chat/*.txt"))
conversation = []

# Multi-turn conversation
for i, prompt_file in enumerate(prompt_files, 1):
    with open(prompt_file, "r") as f:
        user_prompt = f.read()
    
    response_text = generate_multi_turn(MODEL, conversation, user_prompt)
    
    with open(f"{output_dir}/response_turn_{i}.txt", "w", encoding='utf-8') as f:
        f.write(response_text)

# Grade final response with random grading model
GRADING_MODELS = ["gemini-2.5-pro", "claude-sonnet-4-5-20250929", "deepseek-ai/deepseek-v3.1"]
grading_model = random.choice(GRADING_MODELS)
print(f"Using grading model: {grading_model}")

with open("preset_prompts/grading_prompt.txt", "r") as f:
    grading_prompt = f.read()

grade_text = generate_single(grading_model, grading_prompt + '\n' + response_text)

grade_dir = f"multi_chat_grades/{model_name}/trial_{TRIAL}"
os.makedirs(grade_dir, exist_ok=True)
with open(f"{grade_dir}/grading_response.txt", "w", encoding='utf-8') as f:
    f.write(f"[Graded by: {grading_model}]\n\n{grade_text}")

