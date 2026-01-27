#!/usr/bin/env node

/**
 * CLI 入口
 */

import { Command } from 'commander';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import { XHSAutomation, XHSInput } from './index';

const program = new Command();

program
  .name('xhs-auto')
  .description('小红书自动化发布工具')
  .version('1.0.0');

// 主命令
program
  .command('publish')
  .description('发布小红书笔记')
  .option('-t, --topic <topic>', '主题/选题')
  .option('-a, --accounts <accounts>', '账号列表（逗号分隔）')
  .option('-w, --word-count <count>', '字数', '600')
  .option('-c, --context <context>', '背景说明')
  .option('-q, --quick', '快速发布（跳过预览）')
  .option('-g, --generate-only', '只生成内容，不发布')
  .action(async (options) => {
    try {
      // 如果没有提供主题，通过交互式输入
      let input: XHSInput;

      if (options.topic) {
        input = {
          topic: options.topic,
          accounts: options.accounts ? options.accounts.split(',').map(a => a.trim()) : undefined,
          word_count: parseInt(options.word_count),
          context: options.context
        };
      } else {
        // 交互式输入
        const answers = await inquirer.prompt([
          {
            type: 'input',
            name: 'topic',
            message: '请输入主题/选题:',
            validate: (input) => input.trim().length > 0 || '主题不能为空'
          },
          {
            type: 'input',
            name: 'accounts',
            message: '请输入账号列表（逗号分隔，默认: 你的效率闺蜜）:',
            default: '你的效率闺蜜'
          },
          {
            type: 'input',
            name: 'word_count',
            message: '请输入字数:',
            default: '600',
            validate: (input) => !isNaN(parseInt(input)) || '请输入有效的数字'
          },
          {
            type: 'input',
            name: 'context',
            message: '请输入背景说明（可选）:'
          }
        ]);

        input = {
          topic: answers.topic,
          accounts: answers.accounts.split(',').map(a => a.trim()),
          word_count: parseInt(answers.word_count),
          context: answers.context
        };
      }

      const automation = new XHSAutomation();

      if (options.generateOnly) {
        await automation.generateOnly(input);
      } else if (options.quick) {
        await automation.quickPublish(input);
      } else {
        await automation.run(input);
      }

    } catch (error) {
      console.error(chalk.red('❌ 执行失败:'), error);
      process.exit(1);
    }
  });

// 历史记录命令
program
  .command('history')
  .description('查看发布历史')
  .option('-n, --limit <number>', '显示条数', '10')
  .action(async (options) => {
    try {
      const { PublisherImpl } = await import('./modules/publisher');
      const { ConfigManager } = await import('./config');

      const configManager = new ConfigManager();
      const publisher = new PublisherImpl(configManager);

      const history = publisher.getPublishHistory(parseInt(options.limit));

      if (history.length === 0) {
        console.log(chalk.yellow('📭 暂无发布记录'));
        return;
      }

      console.log(chalk.blue('\n📊 发布历史:\n'));
      history.forEach((record, index) => {
        console.log(chalk.bold(`${index + 1}. ${record.title}`));
        console.log(`   发布时间: ${record.publishTime}`);
        console.log(`   定时: ${record.scheduled ? '是' : '否'} ${record.scheduledTime ? '(' + record.scheduledTime + ')' : ''}`);
        console.log(`   标签: ${record.tags.join(', ')}`);
        console.log(`   图片: ${record.images.length} 张`);
        console.log('');
      });

    } catch (error) {
      console.error(chalk.red('❌ 获取历史记录失败:'), error);
      process.exit(1);
    }
  });

// 配置命令
program
  .command('config')
  .description('配置环境变量')
  .action(async () => {
    console.log(chalk.blue('\n⚙️  配置环境变量\n'));

    const answers = await inquirer.prompt([
      {
        type: 'password',
        name: 'doubaoApiKey',
        message: '请输入火山引擎 API Key:',
        mask: '*'
      },
      {
        type: 'input',
        name: 'doubaoModel',
        message: '请输入豆包模型名称:',
        default: 'doubao-seed-1-8-251228'
      },
      {
        type: 'password',
        name: 'xhsCookie',
        message: '请输入小红书 Cookie:',
        mask: '*'
      },
      {
        type: 'input',
        name: 'mcpUrl',
        message: '请输入 MCP 服务端 URL（可选）:',
        default: 'http://47.109.91.65:18060/mcp'
      }
    ]);

    // 生成 .env 文件
    const envContent = `# 火山引擎配置
DOUBAO_API_KEY=${answers.doubaoApiKey}
DOUBAO_MODEL=${answers.doubaoModel}
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 图片生成配置
DOUBAO_IMAGE_API_KEY=${answers.doubaoApiKey}
DOUBAO_IMAGE_MODEL=doubao-seedream-4-5-251128

# 小红书配置
XHS_COOKIE=${answers.xhsCookie}

# MCP 服务端（可选）
MCP_URL=${answers.mcpUrl}

# 输出目录
OUTPUT_DIR=./output
PREVIEW_DIR=./preview
`;

    const fs = await import('fs');
    fs.writeFileSync('.env', envContent);

    console.log(chalk.green('\n✅ 配置已保存到 .env 文件'));
    console.log(chalk.yellow('⚠️  请勿将 .env 文件提交到版本控制'));
  });

// 帮助命令
program
  .command('help')
  .description('显示帮助信息')
  .action(() => {
    program.outputHelp();
    console.log('\n示例:');
    console.log('  xhs-auto publish                    # 交互式发布');
    console.log('  xhs-auto publish -t "AI写作工具"   # 快速发布');
    console.log('  xhs-auto publish -t "AI写作工具" -q  # 快速发布（跳过预览）');
    console.log('  xhs-auto history                    # 查看历史');
    console.log('  xhs-auto config                     # 配置环境变量');
  });

// 解析命令行参数
program.parse(process.argv);

// 如果没有提供命令，显示帮助
if (!process.argv.slice(2).length) {
  program.outputHelp();
}