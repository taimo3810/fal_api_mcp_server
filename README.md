# fal_api_mcp_server MCP server

A MCP server project

## Components

### Resources

The server implements a simple note storage system with:
- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "fal_api_mcp_server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/tai.mori/PycharmProjects/fal_api_mcp_server",
        "run",
        "fal_api_mcp_server"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "fal_api_mcp_server": {
      "command": "uvx",
      "args": [
        "fal_api_mcp_server"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/tai.mori/PycharmProjects/fal_api_mcp_server run 2025-03-31T15:03:23.330Z [fal_api_mcp_server] [info] Initializing server...
2025-03-31T15:03:23.421Z [fal_api_mcp_server] [info] Server started and connected successfully
2025-03-31T15:03:23.509Z [fal_api_mcp_server] [info] Message from client: {"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}},"jsonrpc":"2.0","id":0}
error: Failed to spawn: `fal_api_mcp_server`
  Caused by: No such file or directory (os error 2)
2025-03-31T15:03:23.687Z [fal_api_mcp_server] [info] Server transport closed
2025-03-31T15:03:23.688Z [fal_api_mcp_server] [info] Client transport closed
2025-03-31T15:03:23.688Z [fal_api_mcp_server] [info] Server transport closed unexpectedly, this is likely due to the process exiting early. If you are developing this MCP server you can add output to stderr (i.e. `console.error('...')` in JavaScript, `print('...', file=sys.stderr)` in python) and it will appear in this log.
2025-03-31T15:03:23.688Z [fal_api_mcp_server] [error] Server disconnected. For troubleshooting guidance, please visit our [debugging documentation](https://modelcontextprotocol.io/docs/tools/debugging) {"context":"connection"}
2025-03-31T15:03:23.688Z [fal_api_mcp_server] [info] Client transport closed
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.