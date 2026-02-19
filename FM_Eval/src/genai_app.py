import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import boto3


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def invoke_bedrock(client: Any, model_id: str, prompt: str, max_tokens: int = 300, temperature: float = 0.2) -> str:
    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    )

    content = response.get("output", {}).get("message", {}).get("content", [])
    if not content:
        return ""

    parts = [chunk.get("text", "") for chunk in content if isinstance(chunk, dict)]
    return "".join(parts).strip()


def run_generation(input_file: Path, output_file: Path, model_id: str, region: str) -> None:
    client = boto3.client("bedrock-runtime", region_name=region)

    outputs: List[Dict[str, Any]] = []
    for item in read_jsonl(input_file):
        prompt = item["prompt"]
        model_output = invoke_bedrock(client, model_id=model_id, prompt=prompt)

        outputs.append(
            {
                "id": item.get("id"),
                "prompt": prompt,
                "reference": item.get("reference"),
                "model_output": model_output,
            }
        )

    write_jsonl(output_file, outputs)
    print(f"Wrote {len(outputs)} records to {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple Bedrock GenAI use case app")
    parser.add_argument("--input", default="data/prompts.jsonl", help="Input JSONL with fields: prompt, reference")
    parser.add_argument("--output", default="outputs/model_outputs.jsonl", help="Generated output JSONL")
    parser.add_argument("--model-id", default="amazon.nova-lite-v1:0", help="Bedrock model ID")
    parser.add_argument("--region", default="us-east-1", help="AWS region for Bedrock")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_generation(
        input_file=Path(args.input),
        output_file=Path(args.output),
        model_id=args.model_id,
        region=args.region,
    )
