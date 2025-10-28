# Experiment Framework

## Structure

`preset_prompts/` - Testing prompts
- `single_chat/` - Single prompt testing
- `multi_chat/` - Multi-turn conversation prompts (sorted alphabetically)
- `grading_prompt.txt` - LLM evaluator prompt for danger assessment

`single_chat_responses/` and `single_chat_grades/` - Organized by `{model_name}/trial_{n}/`

`multi_chat_responses/` and `multi_chat_grades/` - Organized by `{model_name}/trial_{n}/`

`.env` - Store API keys (copy from `.env.example`)

## Supported Models

**Proprietary:**
- `gemini-2.0-flash-exp`, `gemini-2.5-pro` (Google)
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` (OpenAI)
- `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022` (Anthropic)

**Open Source (via NVIDIA NIM):**
- `deepseek-ai/deepseek-v3.1`
- `mistralai/mistral-small-24b-instruct`
- `meta/llama-3.1-8b-instruct`

**Open Source (via OpenRouter):**
- `qwen/qwen3-4b`

## Usage

**Manual (single run):**
1. Edit `MODEL` and `TRIAL` in `single_chat_testing.py` or `multi_chat_testing.py`
2. Run: `python single_chat_testing.py` or `python multi_chat_testing.py`

**Automated (all models & trials):**
1. Edit `MODELS` and `TRIALS` in `run_experiments.py`
2. Run: `python run_experiments.py`

Files auto-organize into: `{test_type}/{model_name}/trial_{n}/`
