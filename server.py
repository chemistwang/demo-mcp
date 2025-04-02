import json
import httpx
import datetime
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('MCP Demo')


async def fetch_weather(city: str) -> str:
    """
    获取天气
    :param city: 城市名(需要使用英文，如Beijing)
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    params = {
        "q": city
    }
    async with httpx.AsyncClient() as client:

        return (
            f"city---{city}\n"
            f"weather---晴天"
        )


@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用英文）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather(city)
    return data


@mcp.tool()
async def query_current_time() -> str:
    """
    查询时间，返回当前时间。
    :return: 格式化后的当前时间
    """
    return f"当前时间是 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


if __name__ == "__main__":
    mcp.run(transport='stdio')