import os
import subprocess
import time
# Configuration
MODELS = [
    "qwen/qwen3-4b:free"
]

TRIALS = 10  # Number of trials per model
TEST_TYPES = ["single_chat_testing.py"]  # multi_chat_testing.py is now interactive - run manually

# NOTE: multi_chat_testing.py now requires interactive command-line input
# To run multi-chat tests, execute: python multi_chat_testing.py
# Then interact with the model via command line prompts

# Run experiments
for test_script in TEST_TYPES:
    test_name = test_script.replace("_testing.py", "")
    print(f"\n{'='*60}")
    print(f"Running {test_name.upper()} experiments")
    print('='*60)
    
    for model in MODELS:
        for trial in range(1, TRIALS + 1):
            print(f"\n[{test_name}] Model: {model} | Trial: {trial}")
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
                print(f"✓ Completed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed with error: {e}")
            except Exception as e:
                print(f"✗ Error: {e}")

print(f"\n{'='*60}")
print("All experiments completed!")
print('='*60)

