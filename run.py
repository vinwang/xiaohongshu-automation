#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动化发布工具 - 启动脚本
"""

import sys
import os

# 添加 src 目录到 Python 路径
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

# 导入并运行主程序
from xhs_auto import main

if __name__ == '__main__':
    main()