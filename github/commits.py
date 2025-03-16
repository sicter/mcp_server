from typing import Optional, Dict
from github.common.utils import build_url, github_request
from mcp_instance import register_tool
from pydantic import BaseModel


# Schema definition
class ListCommitsSchema(BaseModel):
    owner: str
    repo: str
    sha: Optional[str] = None
    page: Optional[int] = None
    per_page: Optional[int] = None


@register_tool
def list_commits(
    owner: str,
    repo: str,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    sha: Optional[str] = None,
) -> Dict:
    """
    Fetches a list of commits for a repository/branch
    """
    url = build_url(
        f"https://api.github.com/repos/{owner}/{repo}/commits",
        {
            "page": str(page) if page is not None else None,
            "per_page": str(per_page) if per_page is not None else None,
            "sha": sha,
        },
    )
    return github_request(url)
