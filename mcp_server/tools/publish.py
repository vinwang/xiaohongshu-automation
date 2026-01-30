"""
发布工具
使用 xhs SDK 发布小红书笔记
"""

from typing import Dict, Any

from mcp.types import Tool
from ..adapters.xhs_client import XhsClientAdapter

# 工具定义
publish_note_tool = Tool(
    name="xhs_publish_note",
    description="发布小红书笔记（需要配置 xhs SDK 和 Cookie）",
    inputSchema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "笔记标题"
            },
            "content": {
                "type": "string",
                "description": "笔记正文"
            },
            "images": {
                "type": "array",
                "description": "图片路径列表（本地文件路径）",
                "items": {"type": "string"}
            },
            "tags": {
                "type": "array",
                "description": "标签列表",
                "items": {"type": "string"}
            },
            "cookie": {
                "type": "string",
                "description": "小红书 Cookie（必需）"
            }
        },
        "required": ["title", "content", "images", "cookie"]
    }
)

async def handle_publish_note(arguments: Dict[str, Any]) -> Dict:
    """
    处理发布请求
    
    Args:
        arguments: 工具参数
        
    Returns:
        发布结果
    """
    try:
        # 初始化 xhs 客户端
        cookie = arguments.get("cookie")
        adapter = XhsClientAdapter(cookie=cookie)
        
        # 发布笔记
        result = await adapter.publish_note(
            title=arguments["title"],
            content=arguments["content"],
            images=arguments["images"],
            tags=arguments.get("tags", [])
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
            "message": "发布失败"
        }