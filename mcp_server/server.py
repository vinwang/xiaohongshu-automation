#!/usr/bin/env python3
"""
MCP Server - 小红书自动化工具
支持 Claude Desktop、Cursor 等 MCP 客户端
"""

import asyncio
import json
from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools.content import generate_content_tool
from .tools.images import generate_images_tool
from .tools.publish import publish_note_tool
from .tools.query import get_note_tool, search_notes_tool

# 创建 MCP Server 实例
server = Server("xiaohongshu-automation")

# 注册工具
@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 MCP 工具"""
    return [
        generate_content_tool,
        generate_images_tool,
        publish_note_tool,
        get_note_tool,
        search_notes_tool,
    ]

# 处理工具调用
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "xhs_generate_content":
            from .tools.content import handle_generate_content
            result = await handle_generate_content(arguments)
        elif name == "xhs_generate_images":
            from .tools.images import handle_generate_images
            result = await handle_generate_images(arguments)
        elif name == "xhs_publish_note":
            from .tools.publish import handle_publish_note
            result = await handle_publish_note(arguments)
        elif name == "xhs_get_note":
            from .tools.query import handle_get_note
            result = await handle_get_note(arguments)
        elif name == "xhs_search_notes":
            from .tools.query import handle_search_notes
            result = await handle_search_notes(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "success": False
        }, ensure_ascii=False))]

# 启动 Server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())