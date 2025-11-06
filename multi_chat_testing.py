import os
import random
from dotenv import load_dotenv
load_dotenv()

# Configuration
MODEL = "gpt-4o"  # Options: gemini-*, gpt-*, claude-*, deepseek-ai/*, mistralai/*, meta/*, qwen/*
TRIAL = 1

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
    else:  # OpenAI-compatible (OpenRouter, NVIDIA, OpenAI, Anthropic)
        from openai import OpenAI
        if model.startswith(("qwen/", "meta-llama/")):
            # Route qwen and meta-llama models through OpenRouter
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
            max_tokens = 4096
            extra = {}
        elif model.startswith(("deepseek-ai/", "mistralai/")):
            # Route deepseek and mistralai through NVIDIA
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", 
                           api_key=os.getenv("NVIDIA_API_KEY"))
            max_tokens = 16384 if "deepseek" in model else 8192
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
    elif model.startswith(("qwen/", "meta-llama/")):
        # Route qwen and meta-llama models through OpenRouter
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
    elif model.startswith(("deepseek-ai/", "mistralai/")):
        # Route deepseek and mistralai through NVIDIA
        from openai import OpenAI
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", 
                       api_key=os.getenv("NVIDIA_API_KEY"))
        max_tokens = 16384 if "deepseek" in model else 8192
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
model_name = MODEL.replace("/", "-").replace(":", "-")
output_dir = f"multi_chat_responses/{model_name}/trial_{TRIAL}"
os.makedirs(output_dir, exist_ok=True)

# Interactive multi-turn conversation
conversation = []  # For API conversation history
full_conversation_history = []  # Track FULL conversation: user prompts + model responses
turn = 1

print(f"\n{'='*60}")
print(f"Interactive Multi-Chat Testing")
print(f"Model: {MODEL}")
print(f"Trial: {TRIAL}")
print('='*60)
print("\nInstructions:")
print("  - Type your message and press Enter to send")
print("  - Type 'done' (without quotes) when finished to grade the conversation")
print("  - Type 'quit' to exit without grading")
print(f"\n{'='*60}\n")

while True:
    # Get user input
    user_prompt = input(f"[Turn {turn}] You: ").strip()
    
    # Check for exit commands
    if user_prompt.lower() == 'quit':
        print("\nExiting without grading...")
        exit(0)
    elif user_prompt.lower() == 'done':
        if turn == 1:
            print("\nNo conversation to grade. Exiting...")
            exit(0)
        print("\n" + "="*60)
        print("Conversation completed. Starting grading...")
        print("="*60 + "\n")
        break
    
    if not user_prompt:
        print("(Empty input, please type a message or 'done' to finish)")
        continue
    
    # Get model response
    try:
        response_text = generate_multi_turn(MODEL, conversation, user_prompt)
        print(f"\n[Turn {turn}] Assistant: {response_text}\n")
        
        # Save individual turn with BOTH user prompt and model response
        with open(f"{output_dir}/response_turn_{turn}.txt", "w", encoding='utf-8') as f:
            f.write(f"USER PROMPT:\n{user_prompt}\n\n{'='*60}\n\nMODEL RESPONSE:\n{response_text}")
        
        # Store FULL conversation history (both user prompts and model responses)
        full_conversation_history.append({
            "turn": turn,
            "user_prompt": user_prompt,
            "model_response": response_text
        })
        
        turn += 1
    except Exception as e:
        print(f"\n[ERROR] Failed to get response from model: {e}\n")
        continue

# Save full conversation history to a single file
full_conversation_text = ""
for entry in full_conversation_history:
    full_conversation_text += f"{'='*60}\n"
    full_conversation_text += f"TURN {entry['turn']}\n"
    full_conversation_text += f"{'='*60}\n\n"
    full_conversation_text += f"USER PROMPT:\n{entry['user_prompt']}\n\n"
    full_conversation_text += f"{'-'*60}\n\n"
    full_conversation_text += f"MODEL RESPONSE:\n{entry['model_response']}\n\n"

with open(f"{output_dir}/full_conversation_history.txt", "w", encoding='utf-8') as f:
    f.write(full_conversation_text)

# Grade full conversation history with random grading model
GRADING_MODELS = ["gemini-2.5-pro", "deepseek-ai/deepseek-v3.1"]
grading_model = random.choice(GRADING_MODELS)
print(f"Using grading model: {grading_model}\n")

with open("preset_prompts/grading_prompt.txt", "r") as f:
    grading_prompt = f.read()

# Use the full conversation text for grading
print("Sending full conversation history to grader...")
grade_text = generate_single(grading_model, grading_prompt + '\n\nFULL CONVERSATION HISTORY:\n\n' + full_conversation_text)

grade_dir = f"multi_chat_grades/{model_name}/trial_{TRIAL}"
os.makedirs(grade_dir, exist_ok=True)

# Save the grade with full conversation included
with open(f"{grade_dir}/grading_response.txt", "w", encoding='utf-8') as f:
    f.write(f"[Graded by: {grading_model}]\n\n")
    f.write("="*60 + "\n")
    f.write("GRADE\n")
    f.write("="*60 + "\n\n")
    f.write(grade_text)
    f.write("\n\n" + "="*60 + "\n")
    f.write("FULL CONVERSATION THAT WAS GRADED\n")
    f.write("="*60 + "\n\n")
    f.write(full_conversation_text)

print("\n" + "="*60)
print("GRADING COMPLETE")
print("="*60)
print(f"\nGrade saved to: {grade_dir}/grading_response.txt")
print(f"Full conversation saved to: {output_dir}/full_conversation_history.txt")
print(f"\nGrading Summary:")
print("-"*60)
print(grade_text)
print("-"*60)

