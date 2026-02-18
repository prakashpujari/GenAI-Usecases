# Mortgage Assistant (GenAI)

Production-ready, enterprise-grade Mortgage Assistant with secure document ingestion, PII redaction, and RAG-based Q&A using AWS (Bedrock, Textract, Comprehend, OpenSearch) plus OpenAI for high-reasoning tasks.

## Architecture Overview

- **API Gateway + FastAPI** for external API access.
- **Microservices**: ingestion, PII redaction, LLM router, RAG.
- **AWS**: S3, Textract, Comprehend, DynamoDB, KMS, OpenSearch, Step Functions, ECS/Lambda.
- **Multi-LLM routing** between Bedrock and OpenAI, cost- and latency-aware.
- **Zero-trust PII**: detect, classify, tokenize, store in encrypted vault. No raw PII sent to external LLMs.

## Quick Start (Local)

1. Create a virtual environment.
2. Install dependencies from requirements.txt.
3. Copy `.env.example` to `.env` and fill values.
4. Run each service with uvicorn (see service docs).

## Services

- **API**: document upload and query endpoints.
- **Ingestion**: OCR, extraction, orchestration pipeline.
- **PII**: detection, tokenization, redaction, vault.
- **LLM Router**: multi-LLM selection and fallback.
- **RAG**: embeddings, vector store, retrieval, grounded answers.

## Deployment Notes

- Use **API Gateway + Lambda** for short tasks; **ECS/EKS** for long-running pipelines.
- Use **Step Functions** to orchestrate the pipeline: Upload → Extract → PII → Redact → Embed → Store → Retrieve → Generate.
- Ensure **KMS** encryption, VPC isolation, private endpoints, and least-privilege IAM.

See infra/terraform for reference infrastructure.
