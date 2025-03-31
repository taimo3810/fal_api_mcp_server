import logging
import os
from collections.abc import Sequence
from typing import Any

import base64
from fal_client import async_client
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import EmbeddedResource, ImageContent, Resource, TextContent, Tool
from pydantic import AnyUrl

# 環境変数の読み込み
load_dotenv()

# ログの準備
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fal-image-server")

# fal.ai 認証情報の確認
if not os.getenv("FAL_KEY"):
    logger.warning(
        "FAL_KEY environment variable is recommended."
    )

# サーバの準備
app = Server(name="fal-image-server")


# 利用可能なリソース一覧 (fal.ai はステートレスなので空リストを返す)
@app.list_resources()
async def list_resources() -> list[Resource]:
    # fal.ai は主にステートレスなモデル実行のため、
    # 永続的なリソースの概念は薄い。空リストを返す。
    return []


# 特定のリソースの取得 (呼び出されない想定)
@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    # このサーバーではリソースを提供しないためエラーを返す
    raise ValueError(f"This server does not provide resources like: {uri}")


# 利用可能なツール一覧 (画像生成ツール)
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate_image",
            description="Generate an image based on a text prompt using fal.ai FLUX.1 [pro].",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt to generate the image from.",
                    },
                    "image_size": {
                        "type": "string",
                        "description": "The desired image size (e.g., 'landscape_4_3', 'square_hd'). Defaults to 'landscape_4_3'.",
                        "enum": [
                            "square_hd",
                            "square",
                            "portrait_4_3",
                            "portrait_16_9",
                            "landscape_4_3",
                            "landscape_16_9",
                        ],
                        "default": "landscape_4_3",
                    },
                    "num_images": {
                        "type": "integer",
                        "description": "The number of images to generate.",
                        "default": 1,
                    },
                    "enable_safety_checker": {
                        "type": "boolean",
                        "description": "Enable the safety checker.",
                        "default": True,
                    },
                    "safety_tolerance": {
                        "type": "string",
                        "description": "Safety tolerance level (1-6). Higher is more permissive.",
                        "enum": ["1", "2", "3", "4", "5", "6"],
                        "default": "2",
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output image format.",
                        "enum": ["jpeg", "png"],
                        "default": "jpeg",
                    },
                    # 必要に応じて他のパラメータを追加可能 (seed など)
                },
                "required": ["prompt"],
            },
        )
    ]


# ツールの呼び出し (画像生成)
@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    if name != "generate_image":
        raise ValueError(f"Unknown tool: {name}")

    if not isinstance(arguments, dict) or "prompt" not in arguments:
        raise ValueError("Invalid arguments: 'prompt' is required.")

    # 引数を取得 (デフォルト値付き)
    prompt = arguments["prompt"]
    image_size = arguments.get("image_size", "landscape_4_3")
    num_images = arguments.get("num_images", 1)
    enable_safety_checker = arguments.get("enable_safety_checker", True)
    safety_tolerance = arguments.get("safety_tolerance", "2")
    output_format = arguments.get("output_format", "jpeg")

    logger.info(
        f"Generating image using fal-ai/flux-pro/v1.1 with prompt: '{prompt}', "
        f"size: {image_size}, num: {num_images}, safety: {enable_safety_checker} ({safety_tolerance}), format: {output_format}"
    )

    try:
        result = await async_client.run(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": num_images,
                "enable_safety_checker": enable_safety_checker,
                "safety_tolerance": safety_tolerance,
                "output_format": output_format,
                # "seed": arguments.get("seed"), # 必要なら追加
            },
        )

        print(result)

        # fal.ai のレスポンス形式に合わせて結果を処理
        # {"images": [{"url": "...", "content_type": "..."}], "prompt": "..."}
        if (
            not isinstance(result, dict)
            or "images" not in result
            or not isinstance(result["images"], list)
        ):
            logger.error(f"Unexpected response format from fal.ai: {result}")
            raise RuntimeError("Failed to parse image generation result from fal.ai.")

        image_contents = []
        async with httpx.AsyncClient() as client:
            for image_info in result["images"]:
                # レスポンス形式に合わせて content_type も取得
                if (
                    isinstance(image_info, dict)
                    and "url" in image_info
                    and "content_type" in image_info
                ):
                    image_url = image_info["url"]
                    # content_type をレスポンスから取得、なければデフォルト
                    content_type = image_info.get("content_type", "image/jpeg")
                    try:
                        # 画像URLから画像データを非同期にダウンロード
                        response = await client.get(image_url)
                        response.raise_for_status()
                        image_bytes = response.content
                        
                        base64_image = base64.b64encode(image_bytes).decode("utf-8")
                        image_contents.append(
                            ImageContent(
                                type="image", data=base64_image, mimeType=content_type
                            )
                        )
                        logger.info(
                            f"Successfully downloaded image from {image_url} ({content_type})"
                        )
                    except httpx.HTTPStatusError as e:
                        logger.error(f"Failed to download image from {image_url}: {e}")
                        image_contents.append(
                            TextContent(
                                type="text", text=f"Error downloading image: {e}"
                            )
                        )
                    except Exception as e:
                        logger.error(
                            f"An error occurred while processing image {image_url}: {e}"
                        )
                        image_contents.append(
                            TextContent(
                                type="text", text=f"Error processing image: {e}"
                            )
                        )

                else:
                    logger.warning(
                        f"Skipping invalid image info in fal.ai response: {image_info}"
                    )

        if not image_contents:
            return [
                TextContent(
                    type="text",
                    text="No images were generated or downloaded successfully.",
                )
            ]

        return image_contents

    except Exception as e:
        logger.error(f"An error occurred in call_tool: {e}")
        raise RuntimeError(f"An error occurred in call_tool: {e}")


# メイン
async def main():
    # イベントループの問題を回避するためにここにインポート
    from mcp.server.stdio import stdio_server

    # サーバの実行
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
