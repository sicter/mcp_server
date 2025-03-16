from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python", # Executable
    args=["server.py"], # Optional command line arguments
    env=None # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()

            # Get a prompt
            prompt = await session.get_prompt("echo_prompt", arguments={"message": "value"})

            # List available resources
            resources = await session.list_resources()

            # List available tools
            tools = await session.list_tools()

            # Read a resource
            resource = await session.read_resource("greeting://John")

            # Call a tool
            result = await session.call_tool("add", arguments={"a": 1, "b": 2})

            print(prompts)
            print(prompt)
            print(resources)
            print(tools)
            print(resource)
            print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())