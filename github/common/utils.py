import json
import os
import re
import requests
from urllib.parse import urlencode, urljoin
from typing import Any, Dict, Optional, Union
from .errors import create_github_error

# Type alias for request options
RequestOptions = Dict[str, Union[str, Dict[str, str], Any]]


def parse_response_body(response: requests.Response) -> Union[Dict[str, Any], str]:
    content_type = response.headers.get("content-type")
    if content_type and "application/json" in content_type:
        return response.json()
    return response.text


def build_url(base_url: str, params: Dict[str, Union[str, int, None]]) -> str:
    url = base_url
    query_string = urlencode({k: v for k, v in params.items() if v is not None})
    return f"{url}?{query_string}" if query_string else url


async def github_request(
    url: str, options: Optional[RequestOptions] = None
) -> Union[Dict[str, Any], str]:
    options = options or {}
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        **options.get("headers", {}),
    }

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    print(token)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"Requesting {url} with headers {headers}")
    response = requests.request(
        method=options.get("method", "GET"),
        url=url,
        headers=headers,
        data=json.dumps(options.get("body")) if options.get("body") else None,
    )
    print(f"Response: {response.status_code} {response.text}")
    response_body = parse_response_body(response)

    if not response.ok:
        raise create_github_error(response.status_code, response_body)

    return response_body


def validate_branch_name(branch: str) -> str:
    sanitized = branch.strip()
    if not sanitized:
        raise ValueError("Branch name cannot be empty")
    if ".." in sanitized:
        raise ValueError("Branch name cannot contain '..'")
    if re.search(r"[\\s~^:?*[\\\\]]", sanitized):
        raise ValueError("Branch name contains invalid characters")
    if sanitized.startswith("/") or sanitized.endswith("/"):
        raise ValueError("Branch name cannot start or end with '/'")
    if sanitized.endswith(".lock"):
        raise ValueError("Branch name cannot end with '.lock'")
    return sanitized


def validate_repository_name(name: str) -> str:
    sanitized = name.strip().lower()
    if not sanitized:
        raise ValueError("Repository name cannot be empty")
    if not re.match(r"^[a-z0-9_.-]+$", sanitized):
        raise ValueError(
            "Repository name can only contain lowercase letters, numbers, hyphens, periods, and underscores"
        )
    if sanitized.startswith(".") or sanitized.endswith("."):
        raise ValueError("Repository name cannot start or end with a period")
    return sanitized


def validate_owner_name(owner: str) -> str:
    sanitized = owner.strip().lower()
    if not sanitized:
        raise ValueError("Owner name cannot be empty")
    if not re.match(r"^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){0,38}$", sanitized):
        raise ValueError(
            "Owner name must start with a letter or number and can contain up to 39 characters"
        )
    return sanitized


def check_branch_exists(owner: str, repo: str, branch: str) -> bool:
    try:
        github_request(f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}")
        return True
    except Exception as error:
        if hasattr(error, "status") and error.status == 404:
            return False
        raise


def check_user_exists(username: str) -> bool:
    try:
        github_request(f"https://api.github.com/users/{username}")
        return True
    except Exception as error:
        if hasattr(error, "status") and error.status == 404:
            return False
        raise
