#!/usr/bin/env python3
"""
Multi-AI Orchestrator Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="multi-ai-orchestrator",
    version="1.0.0",
    author="Jeremy Smith",
    author_email="jeremy@oberaconnect.com",
    description="Unified orchestration framework for Claude CLI, Gemini CLI, and Fara-7B",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jerm71279/multi-ai-orchestrator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies (minimal - CLIs are external)
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mai=mai:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json"],
    },
)
