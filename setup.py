# setup.py
from setuptools import setup, find_packages

setup(
    name="mcp-axe",
    version="0.1.5",
    description="MCP plugin for accessibility testing using Axe-core",
    author="Manoj Kumar",
    author_email="your-email@example.com",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.22.0",
        "selenium>=4.10.0",
        "playwright>=1.44.0",
        "requests>=2.28.0",
        "toml>=0.10.2",
        "mcp>=1.6.0",
    ],
    extras_require={
        "dev": [
            "build",
            "twine",
            "pytest>=7.2.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-httpx>=0.18.0",
            "pytest-playwright>=0.5.2",
            "httpx>=0.24.0",
            "sseclient-py>=1.8.0",
            "flake8>=6.0.0",
            "black>=24.1.0",
            "isort>=6.0.0",
            "mypy>=1.4.0",
            "pre-commit>=3.4.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "mcp-axe = mcp_axe.server:main",
        ],
    },
)