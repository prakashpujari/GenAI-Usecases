# AWS GenAI + FMEval (Simple End-to-End)

This project demonstrates a minimal end-to-end AWS GenAI workflow:

1. Run a simple GenAI use case on Amazon Bedrock (support ticket summarization).
2. Evaluate the model with AWS FMEval.

## Project Structure

- `data/prompts.jsonl`: sample prompts + reference outputs
- `src/genai_app.py`: calls Bedrock and writes generated outputs
- `src/evaluate_fmeval.py`: runs FMEval evaluation on Bedrock model (`qa_accuracy` by default)
- `outputs/`: generated outputs and evaluation artifacts

## Prerequisites

- Python 3.10 or 3.11 (recommended: 3.11 on Windows)
- AWS account with Amazon Bedrock access enabled
- AWS credentials configured locally (`aws configure`)
- Bedrock model access granted for the model you choose

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 1) Run the GenAI app

```powershell
python src/genai_app.py --model-id amazon.nova-lite-v1:0 --region us-east-1
```

This creates `outputs/model_outputs.jsonl`.

## 2) Run FMEval

```powershell
python src/evaluate_fmeval.py --model-id amazon.nova-lite-v1:0 --region us-east-1
```

This creates `outputs/fmeval_results.json`.

By default this runs `qa_accuracy` with `roberta-large-mnli` for BERTScore (valid in current FMEval).

Optional (higher-memory) toxicity eval:

```powershell
python src/evaluate_fmeval.py --algorithm toxicity --model-id amazon.nova-lite-v1:0 --region us-east-1
```

## Notes (Windows)

If you encounter Ray-related issues from FMEval on Windows, see FMEval troubleshooting and ensure Python is installed from python.org.

## Optional: Use a different model

You can switch model IDs in both commands, for example:

```powershell
python src/genai_app.py --model-id anthropic.claude-3-haiku-20240307-v1:0 --region us-east-1
python src/evaluate_fmeval.py --model-id anthropic.claude-3-haiku-20240307-v1:0 --region us-east-1
```
