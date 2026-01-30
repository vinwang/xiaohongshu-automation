#!/usr/bin/env python3
"""
MCP Server 启动脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server.server import main

if __name__ == "__main__":
    print("🚀 启动小红书自动化 MCP Server...")
    asyncio.run(main())