/**
 * 配置管理
 */

import { Config } from './types';
import * as fs from 'fs';
import * as path from 'path';

export class ConfigManager {
  private config: Config;

  constructor(configPath?: string) {
    const defaultConfig: Config = {
      llm: {
        apiKey: process.env.DOUBAO_API_KEY || '',
        model: process.env.DOUBAO_MODEL || 'doubao-seed-1-8-251228',
        baseUrl: process.env.DOUBAO_BASE_URL || 'https://ark.cn-beijing.volces.com/api/v3'
      },
      image: {
        apiKey: process.env.DOUBAO_IMAGE_API_KEY || '',
        model: process.env.DOUBAO_IMAGE_MODEL || 'doubao-seedream-4-5-251128',
        baseUrl: process.env.DOUBAO_BASE_URL || 'https://ark.cn-beijing.volces.com/api/v3'
      },
      publish: {
        cookie: process.env.XHS_COOKIE || '',
        mcpUrl: process.env.MCP_URL || 'http://47.109.91.65:18060/mcp'
      },
      storage: {
        outputDir: process.env.OUTPUT_DIR || path.join(process.cwd(), 'output'),
        previewDir: process.env.PREVIEW_DIR || path.join(process.cwd(), 'preview')
      }
    };

    if (configPath && fs.existsSync(configPath)) {
      const customConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      this.config = { ...defaultConfig, ...customConfig };
    } else {
      this.config = defaultConfig;
    }
  }

  get(): Config {
    return this.config;
  }

  validate(): void {
    if (!this.config.llm.apiKey) {
      throw new Error('DOUBAO_API_KEY is required');
    }
    if (!this.config.image.apiKey) {
      throw new Error('DOUBAO_IMAGE_API_KEY is required');
    }
    if (!this.config.publish.cookie) {
      throw new Error('XHS_COOKIE is required');
    }

    // 确保输出目录存在
    if (!fs.existsSync(this.config.storage.outputDir)) {
      fs.mkdirSync(this.config.storage.outputDir, { recursive: true });
    }
    if (!fs.existsSync(this.config.storage.previewDir)) {
      fs.mkdirSync(this.config.storage.previewDir, { recursive: true });
    }
  }
}