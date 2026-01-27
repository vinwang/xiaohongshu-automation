/**
 * 内容生成模块
 */

import axios from 'axios';
import {
  ContentGenerator,
  XHSInput,
  ContentStructure,
  XHSContent,
  Config
} from '../types';
import { ConfigManager } from '../config';

export class ContentGeneratorImpl implements ContentGenerator {
  private config: Config;
  private baseUrl: string;
  private apiKey: string;
  private model: string;

  constructor(configManager?: ConfigManager) {
    const manager = configManager || new ConfigManager();
    this.config = manager.get();
    this.baseUrl = this.config.llm.baseUrl;
    this.apiKey = this.config.llm.apiKey;
    this.model = this.config.llm.model;
  }

  /**
   * 生成内容结构（标题、大纲、标签）
   */
  async generateStructure(input: XHSInput): Promise<ContentStructure> {
    const prompt = this.buildStructurePrompt(input);
    const response = await this.callLLM(prompt, true);

    // 解析 JSON 响应
    const structure = this.parseJSONResponse(response);

    return {
      ...structure,
      subject: input.topic,
      context: input.context || '',
      word_count: input.word_count || 600
    };
  }

  /**
   * 生成完整内容
   */
  async generateContent(structure: ContentStructure): Promise<XHSContent> {
    const prompt = this.buildContentPrompt(structure);
    const response = await this.callLLM(prompt, false);

    // 解析 Markdown 响应
    const content = this.parseMarkdownResponse(response);

    return {
      title: content.title,
      content: content.content,
      tags: content.tags
    };
  }

  /**
   * 构建结构生成提示词
   */
  private buildStructurePrompt(input: XHSInput): string {
    return `你是一位资深的小红书内容创作专家。

【你的任务】
根据用户的内容需求，**严格填充下面的 JSON 结构**，不得输出任何多余文字。

====================
【输入信息】
用户需求：
主题：${input.topic}
字数：${input.word_count || 600}
背景：${input.context || ''}

====================
【标题创作技巧（请参照以下规则）】：

1. 采用二极管标题法进行创作：
   1.1 基本原理：本能喜欢最省力法则和及时享受；动物基本驱动力是追求快乐和逃避痛苦，由此衍生出2个刺激：正刺激、负刺激。
   1.2 标题公式：
      - 正面刺激：产品或方法+只需1秒（短期）+便可开挂（逆天效果）
      - 负面刺激：你不X+绝对会后悔（天大损失）+（紧迫感）

2. 使用具有吸引力的标题：
   2.1 使用标点符号，创造紧迫感和惊喜感 (如：！、？、…等)
   2.2 采用具有挑战性和悬念的表述
   2.3 利用正面刺激和负面刺激
   2.4 融入热点话题和实用工具
   2.5 描述具体的成果和效果

3. 从小红书搜索爆款关键词选择1-2个使用

4. 控制字数在20字以内，文本尽量简短

5.只完成【标题与大纲】：
  5.1 生成5个标题（<20字，二极管标题法）
  5.2 给出最终标题，字数小于20字
  5.3 输出正文大纲
  5.4 给出5个标签

6.生成的内容用中文

====================
**输出格式必须只输出下面 JSON，不得添加解释、注释、markdown、换行说明**
{
  "titles": [{"original": "标题文字", "type": "positive|negative"}],
  "final_title": "最终标题",
  "content_outline": ["大纲要点1", "大纲要点2"],
  "tags": ["#标签1", "#标签2"],
  "subject": "主题",
  "context": "背景",
  "word_count": 字数
}`;
  }

  /**
   * 构建内容生成提示词
   */
  private buildContentPrompt(structure: ContentStructure): string {
    return `你是一位资深的小红书内容创作专家，将根据用户的内容需求，循以下规则执行任务。
用户需求：
标题：${structure.final_title}
主题：${structure.subject}
大纲：${structure.content_outline.join('\\n')}
背景：${structure.context}

## 正文创作规则：
*注意：你不需要用到背景信息中的全部内容，只需要利用好能够服务写作主题的内容。首先思考哪部分内容对于写作主题是有帮助的，再输出文案*
1. 风格匹配：从主题${structure.subject}、正文${structure.content_outline}明确赛道、受众、卖点及风格偏好，匹配对应风格（生活类→轻松/亲切/愉快；职场干货类→严肃/真诚/建议；情感成长类→温馨/沉思/鼓励；活动促销类→激动/热情/欢乐）。开篇钩子需为与受众强相关的高频痛点问题或近期平台热议的争议话题，需能精准击中受众需求，确保开篇3秒内抓住受众注意力。
2. 内容要求：结尾设互动（开放式问题/投票/晒图），结构清晰（吸睛标题、痛点引入、核心内容、互动引导），口语化表达，字数50–${structure.word_count}字。
3. 严格围绕大纲${structure.content_outline}创作，背景信息限定为与主题${structure.subject}直接相关的行业数据、用户普遍认知事实，仅在补充说明核心内容时按需选用，不得引入无关信息。
4. 提供图片搭配建议：根据文案主题给出图片风格（如清新/复古/科技感）、构图技巧（对角线/对称/特写）、色彩搭配及必备元素（产品图/场景图/对比图）的具体建议，不要出现emoji等特殊字符，保持清爽，直接给出风格，不要出现"小红书封面"这种提示。

输出 Markdown：
## 标题
${structure.final_title}

## 正文
（正文）
## 图片建议
（图片建议）

## 标签
${structure.tags.join(' ')}`;
  }

  /**
   * 调用 LLM API
   */
  private async callLLM(prompt: string, useJsonMode: boolean): Promise<string> {
    const response = await axios.post(
      `${this.baseUrl}/chat/completions`,
      {
        model: this.model,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
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
   * 解析 JSON 响应
   */
  private parseJSONResponse(raw: string): any {
    // 移除可能的 markdown 代码块标记
    let cleaned = String(raw)
      .replace(/^```json\s*/i, '')
      .replace(/^```\s*/i, '')
      .replace(/```\s*$/i, '')
      .trim();

    // 解析 JSON
    try {
      return JSON.parse(cleaned);
    } catch (e) {
      // 如果解析失败，尝试提取 JSON 部分
      const match = cleaned.match(/\{[\s\S]*\}/);
      if (match) {
        try {
          return JSON.parse(match[0]);
        } catch (e2) {
          throw new Error('JSON 解析失败: ' + e2.message + '\\n原始内容: ' + raw);
        }
      }
      throw new Error('无法找到有效的 JSON 内容\\n原始内容: ' + raw);
    }
  }

  /**
   * 解析 Markdown 响应
   */
  private parseMarkdownResponse(raw: string): { title: string; content: string; tags: string[] } {
    const title = raw.match(/## 标题([\s\S]*?)## 正文/)?.[1]?.trim() || '';
    const content = raw.match(/## 正文([\s\S]*?)## 图片建议/)?.[1]?.trim() || '';
    const tags = raw.match(/## 标签([\s\S]*)$/)?.[1]?.trim().split(/\s+/).filter(Boolean) || [];

    return { title, content, tags };
  }
}

// 导出为默认导出，方便测试
export { ContentGeneratorImpl as ContentGenerator };