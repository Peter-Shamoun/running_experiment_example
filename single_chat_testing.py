import os
import random
from dotenv import load_dotenv
load_dotenv()

# Configuration
MODEL = "qwen/qwen3-4b:free"  # Options: gemini-*, gpt-*, claude-*, deepseek-ai/*, mistralai/*, meta/*
TRIAL = 10

# Helper function
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
    elif model.startswith("qwen/"):
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        completion = client.chat.completions.create(
            model=model, 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4096
        )
        return completion.choices[0].message.content
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
    else:  # OpenAI/Anthropic
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
model_name = MODEL.replace("/", "-").replace(":", "-")
output_dir = f"single_chat_responses/{model_name}/trial_{TRIAL}"
os.makedirs(output_dir, exist_ok=True)

# Load and run single chat
with open("preset_prompts/single_chat/single_chat_prompt.txt", "r") as f:
    single_chat_prompt = f.read()

response_text = generate_single(MODEL, single_chat_prompt)

with open(f"{output_dir}/response.txt", "w", encoding='utf-8') as f:
    f.write(response_text)

# Grade response with random grading model
GRADING_MODELS = ["gemini-2.5-pro", "deepseek-ai/deepseek-v3.1"]
grading_model = random.choice(GRADING_MODELS)
print(f"Using grading model: {grading_model}")

with open("preset_prompts/grading_prompt.txt", "r") as f:
    grading_prompt = f.read()

grade_text = generate_single(grading_model, grading_prompt + '\n' + response_text)

grade_dir = f"single_chat_grades/{model_name}/trial_{TRIAL}"
os.makedirs(grade_dir, exist_ok=True)
with open(f"{grade_dir}/grading_response.txt", "w", encoding='utf-8') as f:
    f.write(f"[Graded by: {grading_model}]\n\n{grade_text}")
