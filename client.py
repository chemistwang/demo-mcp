import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from openai import OpenAI
from mcp.client.stdio import stdio_client

# 重新载入环境变量
os.environ.clear()
os.environ.update(os.environ)

load_dotenv()


class MCPClient:
    def __init__(self):
        """初始化MCP客户端"""
        self.exit_stack = AsyncExitStack()
        self.session = None
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 未设置")
        self.client = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)


    async def process_query(self, query: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

        messages.append({
            "role": "system",
            "content": f"Available tools: {available_tools}"
        })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=available_tools
        )

        # 处理返回的内容
        content = response.choices[0]
        if content.finish_reason == "tool_calls":
            # 如何是需要使用工具，就解析工具
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # 执行工具
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"\n\n[Calling tool {tool_name} with args {tool_args}]\n\n")
            
            # 将模型返回的调用哪个工具和工具执行完成后的数据都存入messages
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result.content[0].text,
                "tool_call_id": tool_call.id
            })

            # 将上面的结果再返回给大模型用于生产最终的结果
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            # print(f"tool response: {response}")
            return response.choices[0].message.content

        return content.message.content

    async def connect_to_server(self, server_script_path: str):
        """连接到 MCP 服务器并列出可用工具"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是.py或.js文件")

        command = sys.executable if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        # 启动 MCP 服务器并建立通信
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # 列出 MCP 服务器上的工具
        response = await self.session.list_tools()
        tools = response.tools
        print("\n已连接到服务器，支持以下工具：", [tool.name for tool in tools])


    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n MCP 客户端已启动！输入 'quit' 退出")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                response = await self.process_query(query)
                # print(f"\n [Mock Response] 你说的是： {query}")
                print(f"Response:   {response}")
            except Exception as e:
                print(f"\n ⚠️ 调用openAI发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()

async def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python client.py <server_script_path>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 

        
