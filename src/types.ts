/**
 * 核心类型定义
 */

// 输入类型
export interface XHSInput {
  topic: string;
  accounts?: string[];
  word_count?: number;
  context?: string;
}

// 标题类型
export interface Title {
  original: string;
  type: 'positive' | 'negative';
}

// 内容结构
export interface ContentStructure {
  titles: Title[];
  final_title: string;
  content_outline: string[];
  tags: string[];
  subject: string;
  context: string;
  word_count: number;
}

// 完整内容
export interface XHSContent {
  title: string;
  content: string;
  tags: string[];
  images?: string[];
}

// 图片配置
export interface ImageConfig {
  cover_image: string;
  content_images: string[];
  content_images_count: number;
}

// 预览数据
export interface PreviewData {
  title: string;
  content: string;
  tags: string[];
  images: string[];
}

// 发布配置
export interface PublishConfig {
  title: string;
  content: string;
  tags: string[];
  images: string[];
  scheduled_time?: string;
  private?: boolean;
}

// 模块接口
export interface ContentGenerator {
  generateStructure(input: XHSInput): Promise<ContentStructure>;
  generateContent(structure: ContentStructure): Promise<XHSContent>;
}

export interface ImageGenerator {
  generateImagePrompts(content: XHSContent): Promise<ImageConfig>;
  generateImages(config: ImageConfig): Promise<string[]>;
}

export interface PreviewManager {
  generatePreview(data: PreviewData): string;
  showPreview(html: string): Promise<boolean>;
}

export interface Publisher {
  publish(config: PublishConfig): Promise<void>;
  schedulePublish(config: PublishConfig): Promise<void>;
}

// 配置类型
export interface Config {
  // LLM 配置
  llm: {
    apiKey: string;
    model: string;
    baseUrl: string;
  };

  // 图片生成配置
  image: {
    apiKey: string;
    model: string;
    baseUrl: string;
  };

  // 发布配置
  publish: {
    cookie: string;
    mcpUrl?: string;
  };

  // 本地存储配置
  storage: {
    outputDir: string;
    previewDir: string;
  };
}