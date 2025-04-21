from setuptools import setup

setup(
    name='mcp-axe',
    version='0.0.1',
    description='MCP plugin for accessibility testing using Axe-core',
    author='Manoj Kumar Kumar',
    py_modules=['core', 'cli', 'server'],
    package_dir={'': 'src'},
    install_requires=[
        'typer>=0.9.0',
        'fastapi>=0.100.0',
        'uvicorn[standard]>=0.22.0',
        'selenium>=4.10.0',
        'playwright>=1.44.0',
        'axe-selenium-python>=1.2.0',
        'pyyaml>=6.0',
        'toml>=0.10.2',
        'requests>=2.28.0',
        'mcp==1.6.0',
    ],
    entry_points={
        'console_scripts': [
            'mcp-axe = cli:app',
        ],
    },
    include_package_data=True,
    python_requires='>=3.11',
)