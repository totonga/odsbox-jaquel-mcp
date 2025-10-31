from setuptools import setup, find_packages

setup(
    name="odsbox-jaquel-mcp",
    version="0.1.0",
    description="ASAM ODS Jaquel MCP Server - A Model Context Protocol server for creating and validating Jaquel queries",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Assistant",
    author_email="assistant@example.com",
    url="https://github.com/totonga/odsbox-jaquel-mcp",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["mcp>=0.1.0", "odsbox>=1.0.14"],
    extras_require={"dev": ["pytest>=7.0", "black>=23.0", "flake8>=6.0", "mypy>=1.0"]},
    entry_points={"console_scripts": ["odsbox-jaquel-mcp=odsbox_jaquel_mcp.server:main"]},
    python_requires=">=3.12.15",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
    ],
)
