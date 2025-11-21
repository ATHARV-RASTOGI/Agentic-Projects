from unittest import async_case
from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Weathe")

@mcp.tool()

async def get_weather(location:str)->str:
    """Get the weather location"""
    return "Not true information"

if __name__ =="__main__":
    mcp.run(transport="streamable-http")