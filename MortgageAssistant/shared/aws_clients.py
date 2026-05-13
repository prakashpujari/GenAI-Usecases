from __future__ import annotations

from botocore.config import Config
import boto3

from shared.config import settings


_default_config = Config(
    retries={"max_attempts": 5, "mode": "standard"},
    connect_timeout=settings.request_timeout_s,
    read_timeout=settings.request_timeout_s,
)


def s3_client():
    return boto3.client("s3", region_name=settings.aws_region, config=_default_config)


def textract_client():
    return boto3.client("textract", region_name=settings.aws_region, config=_default_config)


def comprehend_client():
    return boto3.client("comprehend", region_name=settings.aws_region, config=_default_config)


def dynamodb_resource():
    return boto3.resource("dynamodb", region_name=settings.aws_region, config=_default_config)


def kms_client():
    return boto3.client("kms", region_name=settings.aws_region, config=_default_config)


def bedrock_runtime_client():
    return boto3.client("bedrock-runtime", region_name=settings.bedrock_region, config=_default_config)
