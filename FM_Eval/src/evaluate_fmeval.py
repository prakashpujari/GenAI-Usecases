import argparse
import json
from pathlib import Path
from typing import Any

import boto3
from fmeval.data_loaders.data_config import DataConfig
from fmeval.eval_algorithms.qa_accuracy import QAAccuracy, QAAccuracyConfig
from fmeval.eval_algorithms.toxicity import Toxicity, ToxicityConfig


class BedrockModelRunner:
    """
    Minimal model runner with a predict() method compatible with FMEval usage patterns.
    """

    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def predict(self, prompt: str) -> str:
        response = self.client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.2},
        )
        content = response.get("output", {}).get("message", {}).get("content", [])
        return "".join(chunk.get("text", "") for chunk in content if isinstance(chunk, dict)).strip()


def to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        return to_jsonable(value.to_dict())
    if hasattr(value, "__dict__"):
        return to_jsonable(value.__dict__)
    return value


def run_fmeval(
    input_file: Path,
    output_file: Path,
    model_id: str,
    region: str,
    algorithm: str,
    bertscore_model: str,
) -> None:
    dataset_config = DataConfig(
        dataset_name="support_ticket_summarization",
        dataset_uri=str(input_file),
        dataset_mime_type="application/jsonlines",
        model_input_location="prompt",
        target_output_location="reference",
    )

    model_runner = BedrockModelRunner(model_id=model_id, region=region)

    if algorithm == "toxicity":
        eval_algo = Toxicity(ToxicityConfig())
    else:
        eval_algo = QAAccuracy(
            QAAccuracyConfig(
                model_type_for_bertscore=bertscore_model,
            )
        )

    eval_output = eval_algo.evaluate(model=model_runner, dataset_config=dataset_config)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(to_jsonable(eval_output), file, indent=2, ensure_ascii=False)

    print(f"FMEval completed. Results saved to {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FMEval on Bedrock model")
    parser.add_argument("--input", default="data/prompts.jsonl", help="Input JSONL with prompt/reference")
    parser.add_argument("--output", default="outputs/fmeval_results.json", help="Evaluation output JSON")
    parser.add_argument("--model-id", default="amazon.nova-lite-v1:0", help="Bedrock model ID")
    parser.add_argument("--region", default="us-east-1", help="AWS region for Bedrock")
    parser.add_argument(
        "--algorithm",
        choices=["qa_accuracy", "toxicity"],
        default="qa_accuracy",
        help="FMEval algorithm to run (qa_accuracy is lighter for local machines)",
    )
    parser.add_argument(
        "--bertscore-model",
        default="roberta-large-mnli",
        help="Model used by QAAccuracy BERTScore metric",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_fmeval(
        input_file=Path(args.input),
        output_file=Path(args.output),
        model_id=args.model_id,
        region=args.region,
        algorithm=args.algorithm,
        bertscore_model=args.bertscore_model,
    )
