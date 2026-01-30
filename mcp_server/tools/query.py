"""
查询工具
使用 xhs SDK 查询小红书笔记
"""

from typing import Dict, Any

from mcp.types import Tool
from ..adapters.xhs_client import XhsClientAdapter

# 工具定义
get_note_tool = Tool(
    name="xhs_get_note",
    description="获取小红书笔记详情（需要配置 xhs SDK 和 Cookie）",
    inputSchema={
        "type": "object",
        "properties": {
            "note_id": {
                "type": "string",
                "description": "笔记 ID"
            },
            "cookie": {
                "type": "string",
                "description": "小红书 Cookie（必需）"
            }
        },
        "required": ["note_id", "cookie"]
    }
)

search_notes_tool = Tool(
    name="xhs_search_notes",
    description="搜索小红书笔记（需要配置 xhs SDK 和 Cookie）",
    inputSchema={
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "搜索关键词"
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "default": 1
            },
            "cookie": {
                "type": "string",
                "description": "小红书 Cookie（必需）"
            }
        },
        "required": ["keyword", "cookie"]
    }
)

async def handle_get_note(arguments: Dict[str, Any]) -> Dict:
    """处理获取笔记请求"""
    try:
        cookie = arguments.get("cookie")
        adapter = XhsClientAdapter(cookie=cookie)
        result = await adapter.get_note(arguments["note_id"])
        return result
    except ImportError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "xhs SDK 未安装，请运行: pip install xhs"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "获取笔记失败"
        }

async def handle_search_notes(arguments: Dict[str, Any]) -> Dict:
    """处理搜索笔记请求"""
    try:
        cookie = arguments.get("cookie")
        adapter = XhsClientAdapter(cookie=cookie)
        result = await adapter.search_notes(
            arguments["keyword"],
            arguments.get("page", 1)
        )
        return result
    except ImportError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "xhs SDK 未安装，请运行: pip install xhs"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "搜索笔记失败"
        }