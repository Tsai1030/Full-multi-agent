# Claude MCP 設定指南

## 📋 概述

本指南將幫助您設定Claude MCP (Model Context Protocol) 服務，以便與我們的紫微斗數AI系統整合。

## 🔧 Claude MCP 設定步驟

### 1. 安裝Claude Desktop

首先需要安裝Claude Desktop應用程式：

- **Windows**: 從 [Claude官網](https://claude.ai/download) 下載安裝程式
- **macOS**: 從 App Store 或官網下載
- **Linux**: 使用官方提供的AppImage或deb包

### 2. 配置MCP服務器

在Claude Desktop中配置MCP服務器，需要修改配置文件：

#### Windows 配置路徑
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### macOS 配置路徑
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Linux 配置路徑
```
~/.config/Claude/claude_desktop_config.json
```

### 3. MCP配置文件內容

創建或編輯 `claude_desktop_config.json` 文件：

```json
{
  "mcpServers": {
    "ziwei-mcp-server": {
      "command": "node",
      "args": ["./mcp-server/ziwei-server.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

### 4. 創建MCP服務器

在項目根目錄創建MCP服務器：

```bash
mkdir mcp-server
cd mcp-server
npm init -y
npm install @modelcontextprotocol/sdk
```

### 5. MCP服務器實現

創建 `ziwei-server.js` 文件：

```javascript
#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
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
            description: '獲取紫微斗數命盤分析',
            inputSchema: {
              type: 'object',
              properties: {
                gender: {
                  type: 'string',
                  description: '性別（男/女）',
                  enum: ['男', '女']
                },
                birth_year: {
                  type: 'integer',
                  description: '出生年份（西元年）',
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
          },
          {
            name: 'web_scraper',
            description: '爬取網站數據',
            inputSchema: {
              type: 'object',
              properties: {
                url: {
                  type: 'string',
                  description: '目標網站URL'
                },
                params: {
                  type: 'object',
                  description: '請求參數'
                }
              },
              required: ['url']
            }
          },
          {
            name: 'data_parser',
            description: '解析網頁或數據內容',
            inputSchema: {
              type: 'object',
              properties: {
                html_content: {
                  type: 'string',
                  description: 'HTML內容'
                },
                parser_type: {
                  type: 'string',
                  description: '解析器類型',
                  enum: ['ziwei', 'general']
                }
              },
              required: ['html_content', 'parser_type']
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
          case 'web_scraper':
            return await this.callWebScraper(args);
          case 'data_parser':
            return await this.callDataParser(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`
            }
          ],
          isError: true
        };
      }
    });
  }

  async callZiweiChart(args) {
    return new Promise((resolve, reject) => {
      const pythonScript = path.join(process.cwd(), '..', 'src', 'mcp', 'tools', 'ziwei_tool.py');
      const python = spawn('python', [pythonScript, JSON.stringify(args)]);

      let output = '';
      let error = '';

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        error += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve({
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(result, null, 2)
                }
              ]
            });
          } catch (e) {
            reject(new Error(`Failed to parse Python output: ${e.message}`));
          }
        } else {
          reject(new Error(`Python script failed: ${error}`));
        }
      });
    });
  }

  async callWebScraper(args) {
    // 實現網頁爬取邏輯
    return {
      content: [
        {
          type: 'text',
          text: `Web scraping for ${args.url} - Implementation needed`
        }
      ]
    };
  }

  async callDataParser(args) {
    // 實現數據解析邏輯
    return {
      content: [
        {
          type: 'text',
          text: `Data parsing for ${args.parser_type} - Implementation needed`
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
```

### 6. 創建Python工具包裝器

創建 `src/mcp/tools/mcp_wrapper.py`：

```python
#!/usr/bin/env python3
"""
MCP工具包裝器
用於從Node.js調用Python紫微斗數工具
"""

import sys
import json
from ziwei_tool import ZiweiTool

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    try:
        args = json.loads(sys.argv[1])
        tool = ZiweiTool()
        result = tool.get_ziwei_chart(args)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 7. 啟動MCP服務器

```bash
# 在mcp-server目錄中
node ziwei-server.js
```

### 8. 重啟Claude Desktop

配置完成後，重啟Claude Desktop應用程式以載入新的MCP配置。

## 🔍 驗證設定

### 1. 檢查MCP連接

在Claude Desktop中，您應該能看到MCP服務器已連接的指示。

### 2. 測試工具調用

在Claude Desktop中嘗試以下對話：

```
請使用紫微斗數工具分析1990年5月15日午時出生的男性命盤
```

### 3. 檢查日誌

查看MCP服務器的輸出日誌，確認工具調用正常。

## 🛠️ 故障排除

### 常見問題

1. **MCP服務器無法啟動**
   - 檢查Node.js版本（需要16+）
   - 確認依賴包已安裝
   - 檢查文件路徑是否正確

2. **Python工具調用失敗**
   - 確認Python環境已激活
   - 檢查Python依賴包
   - 驗證文件權限

3. **Claude Desktop無法連接MCP**
   - 檢查配置文件語法
   - 確認文件路徑正確
   - 重啟Claude Desktop

### 調試命令

```bash
# 檢查MCP服務器狀態
node ziwei-server.js --debug

# 測試Python工具
python src/mcp/tools/mcp_wrapper.py '{"gender":"男","birth_year":1990,"birth_month":5,"birth_day":15,"birth_hour":"午"}'

# 檢查Claude Desktop日誌
# Windows: %APPDATA%\Claude\logs\
# macOS: ~/Library/Logs/Claude/
# Linux: ~/.local/share/Claude/logs/
```

## 📝 注意事項

1. **安全性**: MCP服務器運行在本地，確保只在可信環境中使用
2. **性能**: 大量請求可能影響系統性能
3. **更新**: 定期更新Claude Desktop和MCP SDK
4. **備份**: 備份配置文件以防意外丟失

## 🎯 下一步

設定完成後，您可以：

1. 測試完整的Multi-Agent工作流程
2. 整合RAG知識庫
3. 開發前端介面
4. 部署到生產環境

如果遇到任何問題，請檢查日誌文件或聯繫技術支持。
