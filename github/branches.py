import requests
from typing import Optional, Dict
from pydantic import BaseModel, ValidationError
from github.common.utils import github_request
import mcp
from mcp_instance import register_tool


# Schema definitions
class CreateBranchOptions(BaseModel):
    ref: str
    sha: str


class CreateBranch(BaseModel):
    owner: str
    repo: str
    branch: str
    from_branch: Optional[str] = None


class GitHubReferenceSchema(BaseModel):
    object: Dict[str, str]


async def get_default_branch_sha(owner: str, repo: str) -> str:
    try:
        response = github_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/main"
        )
        data = GitHubReferenceSchema(**response)
        return data.object["sha"]
    except (requests.HTTPError, ValidationError):
        master_response = github_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/master"
        )
        if not master_response:
            raise ValueError(
                "Could not find default branch (tried 'main' and 'master')"
            )
        data = GitHubReferenceSchema(**master_response)
        return data.object["sha"]


@register_tool
async def create_branch(
    owner: str, repo: str, options: CreateBranchOptions
) -> GitHubReferenceSchema:
    full_ref = f"refs/heads/{options.ref}"
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs",
        method="POST",
        body={
            "ref": full_ref,
            "sha": options.sha,
        },
    )
    return GitHubReferenceSchema(**response)


@register_tool
async def get_branch_sha(owner: str, repo: str, branch: str) -> str:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    )
    data = GitHubReferenceSchema(**response)
    return data.object["sha"]


@register_tool
async def create_branch_from_ref(
    owner: str, repo: str, new_branch: str, from_branch: Optional[str] = None
) -> GitHubReferenceSchema:
    if from_branch:
        sha = get_branch_sha(owner, repo, from_branch)
    else:
        sha = get_default_branch_sha(owner, repo)
    return create_branch(owner, repo, CreateBranchOptions(ref=new_branch, sha=sha))


@register_tool
async def update_branch(
    owner: str, repo: str, branch: str, sha: str
) -> GitHubReferenceSchema:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
        method="PATCH",
        body={
            "sha": sha,
            "force": True,
        },
    )
    return GitHubReferenceSchema(**response)
