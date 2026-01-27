/**
 * 图片生成模块
 */

import axios from 'axios';
import {
  ImageGenerator,
  XHSContent,
  ImageConfig,
  Config
} from '../types';
import { ConfigManager } from '../config';

export class ImageGeneratorImpl implements ImageGenerator {
  private config: Config;
  private baseUrl: string;
  private apiKey: string;
  private model: string;

  constructor(configManager?: ConfigManager) {
    const manager = configManager || new ConfigManager();
    this.config = manager.get();
    this.baseUrl = this.config.image.baseUrl;
    this.apiKey = this.config.image.apiKey;
    this.model = this.config.image.model;
  }

  /**
   * 生成图片配置（Prompts）
   */
  async generateImagePrompts(content: XHSContent): Promise<ImageConfig> {
    const prompt = this.buildPromptGenerationPrompt(content);
    const response = await this.callLLM(prompt);

    // 解析 JSON 响应
    return this.parseJSONResponse(response);
  }

  /**
   * 生成图片
   */
  async generateImages(config: ImageConfig): Promise<string[]> {
    const images: string[] = [];

    // 生成封面图
    if (config.cover_image) {
      const coverImage = await this.generateSingleImage(config.cover_image);
      images.push(coverImage);
    }

    // 生成内容图
    for (const prompt of config.content_images) {
      const contentImage = await this.generateSingleImage(prompt);
      images.push(contentImage);
    }

    return images;
  }

  /**
   * 构建提示词生成提示词
   */
  private buildPromptGenerationPrompt(content: XHSContent): string {
    return `你是小红书配图专家，擅长把【文章观点】转化为【对应画面】。

标题：${content.title}

正文摘要：
${content.content}

请严格按以下步骤思考，但【不要输出思考过程】：

步骤1：从正文中提炼 2–3 个【明确、可被画面表达的核心观点】
步骤2：为每个观点生成一条【内容图 Prompt】，紧扣标题和正文的观点
步骤3：生成 1 条【封面图 Prompt】，紧扣标题要表达的观点

生成规则：
1.科技风格，浅色背景
2.不要出现emoji等特殊字符
3.不要生成平台logo，水印
4.图片中不出现乱码、假字、不可识别字符等错误内容
5.图片中无任何平台标识、角标、水印、Logo等元素
6.整体风格必须为充满科技质感的浅色风格
7.所有描述必须转化为清晰、具体、可视觉化的画面内容
8.使用视觉隐喻（图标、构图、色彩）代替文字

只输出严格 JSON，不要解释：

{
  "cover_image": "",
  "content_images": [],
  "content_images_count": 0
}`;
  }

  /**
   * 调用 LLM 生成图片提示词
   */
  private async callLLM(prompt: string): Promise<string> {
    const response = await axios.post(
      `${this.baseUrl}/chat/completions`,
      {
        model: this.config.llm.model,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      },
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data.choices[0].message.content;
  }

  /**
   * 生成单张图片
   */
  private async generateSingleImage(prompt: string): Promise<string> {
    const response = await axios.post(
      `${this.baseUrl}/images/generations`,
      {
        model: this.model,
        prompt: prompt,
        response_format: 'url',
        size: '1728x2304',
        watermark: false
      },
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data.data[0].url;
  }

  /**
   * 解析 JSON 响应
   */
  private parseJSONResponse(raw: string): ImageConfig {
    // 移除可能的 markdown 代码块标记
    let cleaned = String(raw)
      .replace(/^```json\s*/i, '')
      .replace(/^```\s*/i, '')
      .replace(/```\s*$/i, '')
      .trim();

    // 解析 JSON
    try {
      const parsed = JSON.parse(cleaned);
      return {
        cover_image: parsed.cover_image || '',
        content_images: parsed.content_images || [],
        content_images_count: parsed.content_images_count || 0
      };
    } catch (e) {
      // 如果解析失败，尝试提取 JSON 部分
      const match = cleaned.match(/\{[\s\S]*\}/);
      if (match) {
        try {
          const parsed = JSON.parse(match[0]);
          return {
            cover_image: parsed.cover_image || '',
            content_images: parsed.content_images || [],
            content_images_count: parsed.content_images_count || 0
          };
        } catch (e2) {
          throw new Error('配图JSON解析失败: ' + e2.message + '\\n原始内容: ' + raw);
        }
      }
      throw new Error('无法找到有效的配图JSON内容\\n原始内容: ' + raw);
    }
  }
}

// 导出为默认导出，方便测试
export { ImageGeneratorImpl as ImageGenerator };