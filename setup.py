from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="prompt-firewall",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced AI Security System for Detecting Prompt Injection Attacks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Prompt_Firewall",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/Prompt_Firewall/issues",
        "Documentation": "https://github.com/yourusername/Prompt_Firewall#readme",
        "Source Code": "https://github.com/yourusername/Prompt_Firewall",
    },
    packages=find_packages(exclude=["tests", "notebooks", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "isort>=5.10.0",
        ],
        "api": [
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "streamlit>=1.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "prompt-firewall=src.firewall:main",
            "train-models=train_models:main",
            "evaluate-models=evaluate_models:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.yaml", "rules/*.yaml"],
    },
    keywords=[
        "llm",
        "security",
        "prompt-injection",
        "ai-safety",
        "machine-learning",
        "transformers",
        "bert",
        "nlp",
        "firewall",
        "threat-detection",
    ],
)
