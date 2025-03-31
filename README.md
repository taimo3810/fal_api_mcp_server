# fal-api-mcp-server

A Model Context Protocol (MCP) server that provides image generation capabilities using fal.ai's FLUX.1 Pro model.

## Components

### Resources

This server does not provide any persistent resources as fal.ai is primarily a stateless model execution service.

### Tools

The server implements one tool:

- **generate_image**: Generates images based on text prompts using fal.ai FLUX.1 Pro
  - Required parameters:
    - `prompt`: The text prompt to generate the image from
  - Optional parameters:
    - `image_size`: The desired image size (default: "landscape_4_3")
      - Options: "square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"
    - `num_images`: The number of images to generate (default: 1)
    - `enable_safety_checker`: Enable the safety checker (default: true)
    - `safety_tolerance`: Safety tolerance level 1-6, higher is more permissive (default: "2")
    - `output_format`: Output image format, "jpeg" or "png" (default: "jpeg")

## Configuration

This server requires a fal.ai API key to function properly. You can obtain an API key by signing up at [fal.ai](https://www.fal.ai/).

The API key should be provided as an environment variable:

```
FAL_KEY=your_fal_ai_api_key
```

You can set this environment variable in your shell, or create a `.env` file in the same directory as the server with the above content.

## Demo

[Demo Video Coming Soon]

<!-- 
To add your demo video:
1. Upload your video to a hosting service (YouTube, Vimeo, etc.)
2. Replace the placeholder above with the embed code or link
3. For GitHub markdown, you can use:
   [![Demo Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
-->

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
  ```json
  "mcpServers": {
    "fal-api-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/fal-api-mcp-server",
        "run",
        "fal-api-mcp-server"
      ],
      "env": {
        "FAL_KEY": "your_fal_ai_api_key"
      }
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
  ```json
  "mcpServers": {
    "fal-api-mcp-server": {
      "command": "uvx",
      "args": [
        "fal-api-mcp-server"
      ],
      "env": {
        "FAL_KEY": "your_fal_ai_api_key"
      }
    }
  }
  ```
</details>

### Usage

Once the server is configured and running, you can use it with Claude to generate images. Example prompts:

- "Generate an image of a mountain landscape at sunset"
- "Create a portrait of a cyberpunk character with neon lights"
- "Show me a futuristic cityscape with flying cars"

Claude will use the fal.ai FLUX.1 Pro model to generate the requested images.

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
npx @modelcontextprotocol/inspector uv --directory /path/to/fal-api-mcp-server run fal-api-mcp-server
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
