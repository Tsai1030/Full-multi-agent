#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import path from 'path';

class ZiweiMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'ziwei-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // 列出可用工具
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'ziwei_chart',
            description: '獲取紫微斗數命盤',
            inputSchema: {
              type: 'object',
              properties: {
                gender: {
                  type: 'string',
                  enum: ['男', '女'],
                  description: '性別'
                },
                birth_year: {
                  type: 'integer',
                  description: '出生年份',
                  minimum: 1900,
                  maximum: 2100
                },
                birth_month: {
                  type: 'integer',
                  description: '出生月份',
                  minimum: 1,
                  maximum: 12
                },
                birth_day: {
                  type: 'integer',
                  description: '出生日期',
                  minimum: 1,
                  maximum: 31
                },
                birth_hour: {
                  type: 'string',
                  description: '出生時辰（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）'
                }
              },
              required: ['gender', 'birth_year', 'birth_month', 'birth_day', 'birth_hour']
            }
          }
        ]
      };
    });

    // 處理工具調用
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'ziwei_chart':
            return await this.callZiweiChart(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  async callZiweiChart(args) {
    // 簡單的模擬回應，實際應用中應該調用Python腳本
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            message: "紫微斗數命盤生成成功",
            data: {
              gender: args.gender,
              birth_date: `${args.birth_year}年${args.birth_month}月${args.birth_day}日${args.birth_hour}時`,
              main_star: "紫微星",
              palace: {
                命宮: ["紫微", "天機"],
                財帛: ["武曲", "天同"],
                兄弟: ["太陽", "巨門"],
                夫妻: ["天王", "貪狼"]
              }
            }
          }, null, 2)
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Ziwei MCP Server running on stdio');
  }
}

const server = new ZiweiMCPServer();
server.run().catch(console.error);