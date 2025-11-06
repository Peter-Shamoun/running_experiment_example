import os
import subprocess
import time
# Configuration
MODELS = [
    "claude-sonnet-4-5-20250929",
    "deepseek-ai/deepseek-v3.1",
    "gemini-2.5-pro",
    "gpt-5",
    "meta-llama/llama-3.1-8b-instruct",
    "mistralai/mistral-small-24b-instruct",
    "qwen/qwen3-4b:free"
]

# Test configurations: different trial counts for different test types
TEST_CONFIGS = [
    {"script": "single_chat_testing.py", "trials": 10}
]

# NOTE: multi_chat_testing.py requires manual/interactive input
# To run multi-chat tests, execute manually: python multi_chat_testing.py
# Do 1 trial per model, interacting with the model via command line prompts

# Run experiments
for test_config in TEST_CONFIGS:
    test_script = test_config["script"]
    trials = test_config["trials"]
    test_name = test_script.replace("_testing.py", "")
    print(f"\n{'='*60}")
    print(f"Running {test_name.upper()} experiments")
    print(f"Trials per model: {trials}")
    print('='*60)
    
    for model in MODELS:
        for trial in range(1, trials + 1):
            print(f"\n[{test_name}] Model: {model} | Trial: {trial}/{trials}")
            time.sleep(10)
            # Update the script with model and trial
            with open(test_script, "r") as f:
                content = f.read()
            
            # Replace MODEL and TRIAL lines
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("MODEL = "):
                    lines[i] = f'MODEL = "{model}"  # Options: gemini-*, gpt-*, claude-*, deepseek-ai/*, mistralai/*, meta/*'
                elif line.startswith("TRIAL = "):
                    lines[i] = f"TRIAL = {trial}"
            
            with open(test_script, "w") as f:
                f.write('\n'.join(lines))
            
            # Run the script
            try:
                subprocess.run(["python", test_script], check=True)
                print(f"[PASS] Completed successfully")
            except subprocess.CalledProcessError as e:
                print(f"[FAIL] Failed with error: {e}")
            except Exception as e:
                print(f"[ERROR] Error: {e}")

print(f"\n{'='*60}")
print("All experiments completed!")
print('='*60)

