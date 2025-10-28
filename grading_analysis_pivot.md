# Grading Analysis - Model Performance Summary

## Reproducibility by Model and Chat Type

| Model | Single Chat | Multi Chat |
|-------|-------------|------------|
| claude-sonnet-4-5-20250929 | 90.0% | 0.0% |
| deepseek-ai-deepseek-v3.1 | 100.0% | 60.0% |
| gemini-2.5-pro | 100.0% | 40.0% |
| gpt-5 | 10.0% | 20.0% |
| meta-llama-3.1-8b-instruct | 0.0% | 10.0% |
| mistralai-mistral-small-24b-instruct | 60.0% | 20.0% |

## Danger Rate by Model and Chat Type

| Model | Single Chat | Multi Chat |
|-------|-------------|------------|
| claude-sonnet-4-5-20250929 | 90.0% | 20.0% |
| deepseek-ai-deepseek-v3.1 | 90.0% | 100.0% |
| gemini-2.5-pro | 100.0% | 100.0% |
| gpt-5 | 30.0% | 90.0% |
| meta-llama-3.1-8b-instruct | 70.0% | 80.0% |
| mistralai-mistral-small-24b-instruct | 0.0% | 100.0% |

## Overall Statistics

| Chat Type | Reproducible | Dangerous |
|-----------|-------------|-----------|
| Single Chat | 60.0% | 63.3% |
| Multi Chat | 25.0% | 81.7% |

---

### Key Insights

**Most Reproducible (Single Chat):**
- DeepSeek v3.1 & Gemini 2.5 Pro: 100%
- Claude Sonnet 4.5: 90%

**Most Reproducible (Multi Chat):**
- DeepSeek v3.1: 60%
- Gemini 2.5 Pro: 40%

**Highest Danger Rate (Single Chat):**
- Gemini 2.5 Pro: 100%
- DeepSeek v3.1 & Claude Sonnet 4.5: 90%

**Highest Danger Rate (Multi Chat):**
- Gemini 2.5 Pro, DeepSeek v3.1, Mistral Small: 100%
- GPT-5: 90%

**Notable Patterns:**
- Multi-chat conversations yield 2.4× less reproducible designs (25% vs 60%)
- Multi-chat conversations are 1.3× more dangerous (81.7% vs 63.3%)
- Mistral Small shows extreme variance: 0% dangerous (single) vs 100% dangerous (multi)
- GPT-5 shows strongest safety measures in single chat (10% reproducible, 30% dangerous)

