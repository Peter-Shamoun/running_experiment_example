import os
import sys
import json
import random
from dotenv import load_dotenv
load_dotenv()

# Configuration
MODEL = "gpt-5"
TRIAL = 4

# Helper functions (same as multi_chat_testing.py)
def generate_multi_turn(model, conversation_history, new_prompt):
    if "gemini" in model:
        try:
            from google import genai
            client = genai.Client()
            conversation_history.append({"role": "user", "parts": [{"text": new_prompt}]})
            response = client.models.generate_content(model=model, contents=conversation_history)
            conversation_history.append({"role": "model", "parts": [{"text": response.text}]})
            return response.text
        except Exception as e:
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
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
    else:
        from openai import OpenAI
        if model.startswith("qwen/"):
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
            max_tokens = 4096
            extra = {}
        elif model.startswith(("deepseek-ai/", "mistralai/", "meta/")):
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY"))
            max_tokens = 16384 if "deepseek" in model else (8192 if "mistral" in model else 4096)
            extra = {"extra_body": {"chat_template_kwargs": {"thinking": True}}} if "deepseek" in model else {}
        else:
            max_tokens = 4096
            extra = {}
            if "gpt" in model:
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                extra["top_p"] = 0.7
            else:
                client = OpenAI(base_url="https://api.anthropic.com/v1", api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        conversation_history.append({"role": "user", "content": new_prompt})
        if "gpt" in model and ("gpt-5" in model or model.startswith(("o1", "o3"))):
            completion = client.chat.completions.create(model=model, messages=conversation_history, max_completion_tokens=max_tokens, stream=False)
        else:
            completion = client.chat.completions.create(model=model, messages=conversation_history, temperature=0.2, max_tokens=max_tokens, stream=False, **extra)
        response_text = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": response_text})
        return response_text

def generate_single(model, prompt):
    if "gemini" in model:
        try:
            from google import genai
            client = genai.Client()
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
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
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
        completion = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.2, max_tokens=4096)
        return completion.choices[0].message.content
    elif model.startswith(("deepseek-ai/", "mistralai/", "meta/")):
        from openai import OpenAI
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY"))
        max_tokens = 16384 if "deepseek" in model else (8192 if "mistral" in model else 4096)
        extra = {"extra_body": {"chat_template_kwargs": {"thinking": True}}} if "deepseek" in model else {}
        completion = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.2, top_p=0.7, max_tokens=max_tokens, stream=False, **extra)
        return completion.choices[0].message.content
    else:
        from openai import OpenAI
        if "gpt" in model:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if "gpt-5" in model or model.startswith(("o1", "o3")):
                completion = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_completion_tokens=4096)
            else:
                completion = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.2, top_p=0.7, max_tokens=4096)
        else:
            client = OpenAI(base_url="https://api.anthropic.com/v1", api_key=os.getenv("ANTHROPIC_API_KEY"))
            completion = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.2, max_tokens=4096)
        return completion.choices[0].message.content

# Setup
model_name = MODEL.replace("/", "-").replace(":", "-")
output_dir = f"multi_chat_responses/{model_name}/trial_{TRIAL}"
os.makedirs(output_dir, exist_ok=True)

conversation_file = f"{output_dir}/conversation_state.json"
history_file = f"{output_dir}/full_conversation_history.txt"

# Load or initialize conversation
if os.path.exists(conversation_file):
    with open(conversation_file, "r") as f:
        data = json.load(f)
        conversation = data["conversation"]
        full_history = data["full_history"]
        turn = data["turn"]
else:
    conversation = []
    full_history = []
    turn = 1

# Check for command
if len(sys.argv) < 2:
    print("Usage: python multi_chat_conversation.py '<prompt>' OR python multi_chat_conversation.py done")
    sys.exit(1)

user_input = sys.argv[1]

if user_input.lower() == "done":
    # Grade the conversation
    print("\n" + "="*60)
    print("Grading conversation...")
    print("="*60 + "\n")
    
    GRADING_MODELS = ["gemini-2.5-pro", "deepseek-ai/deepseek-v3.1"]
    grading_model = random.choice(GRADING_MODELS)
    print(f"Using grading model: {grading_model}\n")
    
    with open("preset_prompts/grading_prompt.txt", "r") as f:
        grading_prompt = f.read()
    
    full_conversation_text = ""
    for entry in full_history:
        full_conversation_text += f"{'='*60}\nTURN {entry['turn']}\n{'='*60}\n\n"
        full_conversation_text += f"USER PROMPT:\n{entry['user_prompt']}\n\n{'-'*60}\n\n"
        full_conversation_text += f"MODEL RESPONSE:\n{entry['model_response']}\n\n"
    
    grade_text = generate_single(grading_model, grading_prompt + '\n\nFULL CONVERSATION HISTORY:\n\n' + full_conversation_text)
    
    grade_dir = f"multi_chat_grades/{model_name}/trial_{TRIAL}"
    os.makedirs(grade_dir, exist_ok=True)
    
    with open(f"{grade_dir}/grading_response.txt", "w", encoding='utf-8') as f:
        f.write(f"[Graded by: {grading_model}]\n\n{'='*60}\nGRADE\n{'='*60}\n\n")
        f.write(grade_text)
        f.write(f"\n\n{'='*60}\nFULL CONVERSATION THAT WAS GRADED\n{'='*60}\n\n")
        f.write(full_conversation_text)
    
    print("\nGRADING COMPLETE")
    print(f"Grade saved to: {grade_dir}/grading_response.txt\n")
    print(grade_text)
    
    # Clean up conversation state
    os.remove(conversation_file)
    sys.exit(0)

# Send prompt and get response
try:
    response_text = generate_multi_turn(MODEL, conversation, user_input)
    
    # Save turn
    with open(f"{output_dir}/response_turn_{turn}.txt", "w", encoding='utf-8', errors='replace') as f:
        f.write(f"USER PROMPT:\n{user_input}\n\n{'='*60}\n\nMODEL RESPONSE:\n{response_text}")
    
    # Update history
    full_history.append({"turn": turn, "user_prompt": user_input, "model_response": response_text})
    
    # Save state
    with open(conversation_file, "w") as f:
        json.dump({"conversation": conversation, "full_history": full_history, "turn": turn + 1}, f)
    
    # Print response
    try:
        print(f"\n{'='*60}")
        print(f"TURN {turn} - Model: {MODEL}")
        print('='*60)
        print(response_text)
        print('='*60 + "\n")
    except UnicodeEncodeError:
        print(f"\n{'='*60}")
        print(f"TURN {turn} - Model: {MODEL}")
        print('='*60)
        print(response_text.encode('ascii', 'replace').decode('ascii'))
        print('='*60 + "\n")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

