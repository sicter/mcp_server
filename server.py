# server.py
from mcp.server.fastmcp import FastMCP
from github.common.utils import github_request, build_url
from mcp_instance import mcp, register_resource, register_tool, register_prompt

## Tool and resource implicit imports
import github.branches


@mcp.tool()
async def list_commits(
    owner: str, repo: str, page: int = None, per_page: int = None, sha: str = None
):
    """List commits for a repository"""
    params = {
        "page": str(page) if page is not None else None,
        "per_page": str(per_page) if per_page is not None else None,
        "sha": sha,
    }
    url = build_url(f"https://api.github.com/repos/{owner}/{repo}/commits", params)
    return await github_request(url)


if __name__ == "__main__":
    mcp.run()
