"""
SecureMortgageAI - AI-powered mortgage document assistant with PII protection
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="securemortgageai",
    version="1.0.0",
    author="GenAI Use Cases",
    description="AI-powered mortgage document assistant with PII protection and security guardrails",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/GenAI-Usecases",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11,<3.13",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "securemortgageai=app:main",
        ],
    },
    keywords="mortgage, rag, ai, pii, security, nlp, chatbot, openai, langchain",
    project_urls={
        "Documentation": "https://github.com/yourusername/GenAI-Usecases/blob/main/Mortgage_Rag/README.md",
        "Source": "https://github.com/yourusername/GenAI-Usecases",
        "Tracker": "https://github.com/yourusername/GenAI-Usecases/issues",
    },
)
