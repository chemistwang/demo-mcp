# MCP Demo

支持查询天气 `query_weather` 和查询当前时间 `query_current_time`

## 1. 启用 ollama

启用 `ollama`，在 `.env` 文件中配置相关参数

## 2. 安装依赖

```bash
uv sync
```

## 3. 激活虚拟环境

```bash
source .venv/bin/activate
```

## 4. 运行

```bash
uv run client.py server.py
```

## 5. MCP 简介

- Anthropic MCP 发布通告：https://www.anthropic.com/news/model-context-protocol
- MCP GitHub 主页：https://github.com/modelcontextprotocol

### 5.1 Server 简介

根据 MCP 协议定义，`Server` 可以提供三种类型的标准能力，`Resources`、`Tools`、`Prompts`，每个`Server`可同时提供者三种类型能力或其中一种。

- Resources：资源，类似于文件数据读取，可以是文件资源或是 API 响应返回的内容。
- Tools：工具，第三方服务、功能函数，通过此可控制 LLM 可调用哪些函数。
- Prompts：提示词，为用户预先定义好的完成特定任务的模板。

### 5.2 协议

MCP 定义了 Client 与 Server 进行通讯的协议与消息格式，其支持两种类型通讯机制：标准输入输出通讯、基于 SSE 的 HTTP 通讯，分别对应着本地与远程通讯。Client 与 Server 间使用`JSON-RPC 2.0`格式进行消息传输。

- 本地通讯：使用了 stdio 传输数据，具体流程 Client 启动 Server 程序作为子进程，其消息通讯是通过`stdin/stdout`进行的，消息格式为`JSON-RPC 2.0`。
- 远程通讯：Client 与 Server 可以部署在任何地方，Client 使用 SSE 与 Server 进行通讯，消息的格式为`JSON-RPC 2.0`，Server 定义了`/see与/messages`接口用于推送与接收数据。

### 5.3 导航

- MCP 官方服务器合集：https://github.com/modelcontextprotocol/servers
- MCP Github 热门导航：https://github.com/punkpeye/awesome-mcp-servers
