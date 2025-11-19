# Setup odsbox_jaquel_mcp MCP Server

## Step by Step

* Create virtual environment at `????\.venv`
  ```
  cd /D ????
  python -m venv .venv
  ```
* Activate virtual environment
  ```
  ????\.venv\Scripts\activate
  ```
* Install mcp server and dependencies to local `.venv`
  ```
  pip install ????\odsbox_jaquel_mcp-0.2.10-py3-none-any.whl
  ```
* Add MCP Server to VSCode with path `????\.venv\Scripts\odsbox-jaquel-mcp.exe` as `stdio`

## VSCode

`.vscode\mcp.json`

```
{
	"servers": {
		"my-mcp-server-313ed3d1": {
			"type": "stdio",
			"command": "C:\\temp\\odsbox_jaquel_mcp\\.venv\\Scripts\\odsbox-jaquel-mcp.exe",
			"args": []
		}
	},
	"inputs": []
}
```

## Installation

What installation:

![Setup odsbox_jaquel_mcp](setup_odsbox_jaquel_mcp.gif)
