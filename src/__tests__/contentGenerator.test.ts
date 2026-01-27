/**
 * ContentGenerator 单元测试
 */

import { ContentGenerator, XHSInput, ContentStructure, XHSContent } from '../types';

describe('ContentGenerator', () => {
  let generator: ContentGenerator;

  beforeEach(() => {
    // 这里会使用真实的实现，但我们会 mock LLM 调用
    generator = new (require('../modules/contentGenerator').ContentGenerator)();
  });

  describe('generateStructure', () => {
    it('should generate content structure from input', async () => {
      const input: XHSInput = {
        topic: 'AI写作工具',
        accounts: ['你的效率闺蜜'],
        word_count: 500,
        context: '介绍AI写作的优势'
      };

      const structure = await generator.generateStructure(input);

      expect(structure).toBeDefined();
      expect(structure.subject).toBe('AI写作工具');
      expect(structure.word_count).toBe(500);
      expect(structure.titles).toHaveLength(5);
      expect(structure.final_title).toBeDefined();
      expect(structure.final_title.length).toBeLessThanOrEqual(20);
      expect(structure.tags).toBeDefined();
      expect(structure.tags.length).toBeGreaterThan(0);
    });

    it('should use default values when optional fields are missing', async () => {
      const input: XHSInput = {
        topic: '测试主题'
      };

      const structure = await generator.generateStructure(input);

      expect(structure.word_count).toBe(600); // 默认值
      expect(structure.accounts).toEqual(['你的效率闺蜜']); // 默认值
    });

    it('should generate titles using binary electrode method', async () => {
      const input: XHSInput = {
        topic: '效率工具'
      };

      const structure = await generator.generateStructure(input);

      // 检查是否包含正刺激或负刺激的标题
      const hasPositiveStimulus = structure.titles.some(t =>
        /只需|便可|开挂|秒杀/.test(t.original)
      );
      const hasNegativeStimulus = structure.titles.some(t =>
        /不.*绝对会后悔|不.*损失|不.*错过/.test(t.original)
      );

      expect(hasPositiveStimulus || hasNegativeStimulus).toBe(true);
    });
  });

  describe('generateContent', () => {
    it('should generate full content from structure', async () => {
      const structure: ContentStructure = {
        titles: [
          { original: 'AI写作，只需1秒，便可开挂！', type: 'positive' },
          { original: '不学AI写作，绝对会后悔！', type: 'negative' }
        ],
        final_title: 'AI写作，只需1秒，便可开挂！',
        content_outline: ['开篇钩子', '核心内容', '互动引导'],
        tags: ['#AI写作', '#效率工具'],
        subject: 'AI写作工具',
        context: '介绍AI写作的优势',
        word_count: 500
      };

      const content = await generator.generateContent(structure);

      expect(content).toBeDefined();
      expect(content.title).toBe(structure.final_title);
      expect(content.content).toBeDefined();
      expect(content.content.length).toBeGreaterThan(0);
      expect(content.tags).toEqual(structure.tags);
    });

    it('should match content style based on subject', async () => {
      const structure: ContentStructure = {
        titles: [{ original: '职场晋升秘籍', type: 'positive' }],
        final_title: '职场晋升秘籍',
        content_outline: ['职场干货'],
        tags: ['#职场'],
        subject: '职场成长',
        context: '',
        word_count: 400
      };

      const content = await generator.generateContent(structure);

      // 职场类应该更严肃
      expect(content.content).toBeDefined();
    });

    it('should include interaction at the end', async () => {
      const structure: ContentStructure = {
        titles: [{ original: '测试标题', type: 'positive' }],
        final_title: '测试标题',
        content_outline: ['内容'],
        tags: ['#测试'],
        subject: '测试',
        context: '',
        word_count: 300
      };

      const content = await generator.generateContent(structure);

      // 检查是否包含互动引导
      const hasInteraction = /你们|你|大家|评论|留言|点赞|关注/.test(content.content);
      expect(hasInteraction).toBe(true);
    });
  });
});