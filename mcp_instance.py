from mcp.server.fastmcp import FastMCP

# Shared MCP instance
mcp = FastMCP("Demo")


def register_tool(func):
    return mcp.tool()(func)


def register_resource(uri_template):
    def decorator(func):
        return mcp.resource(uri_template)(func)

    return decorator


def register_prompt(func):
    return mcp.prompt()(func)
