"""GitHub Intelligence Gateway.

This module enables the system to interact with GitHub repositories.
It supports repository inspection, issue creation, pull request creation, and version tracking.
"""
import os
from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class GitHubEngine:
    """GitHub-powered repository intelligence engine."""

    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub engine."""
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        
        if not self.token:
            logger.warning("GitHub token not configured. Repository capabilities limited.")
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def analyze_repo(self, owner: str, repo: str) -> dict[str, Any]:
        """Analyze repository structure and provide insights.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository analysis
        """
        if not self.token:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "analysis": {},
            }
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get repository info
                async with session.get(
                    f"{self.api_base}/repos/{owner}/{repo}",
                    headers=self.headers,
                ) as resp:
                    if resp.status != 200:
                        return {
                            "success": False,
                            "error": f"Failed to fetch repo: {resp.status}",
                        }
                    repo_info = await resp.json()
                
                # Get default branch
                default_branch = repo_info.get("default_branch", "main")
                
                # Get directory structure (limited)
                async with session.get(
                    f"{self.api_base}/repos/{owner}/{repo}/contents",
                    headers=self.headers,
                    params={"ref": default_branch},
                ) as resp:
                    if resp.status == 200:
                        contents = await resp.json()
                        file_tree = [c.get("name") for c in contents if isinstance(c, dict)]
                    else:
                        file_tree = []
                
                # Get recent commits
                async with session.get(
                    f"{self.api_base}/repos/{owner}/{repo}/commits",
                    headers=self.headers,
                    params={"per_page": 5},
                ) as resp:
                    if resp.status == 200:
                        commits = await resp.json()
                        recent_commits = [
                            {
                                "message": c.get("commit", {}).get("message", ""),
                                "author": c.get("commit", {}).get("author", {}).get("name", ""),
                                "date": c.get("commit", {}).get("author", {}).get("date", ""),
                            }
                            for c in commits
                        ]
                    else:
                        recent_commits = []
                
                return {
                    "success": True,
                    "analysis": {
                        "name": repo_info.get("name"),
                        "description": repo_info.get("description"),
                        "default_branch": default_branch,
                        "language": repo_info.get("language"),
                        "stars": repo_info.get("stargazers_count", 0),
                        "forks": repo_info.get("forks_count", 0),
                        "open_issues": repo_info.get("open_issues_count", 0),
                        "file_tree": file_tree[:20],  # Limit to 20 files
                        "recent_commits": recent_commits,
                        "url": repo_info.get("html_url"),
                    },
                }
        except Exception as e:
            logger.error(f"GitHub repo analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Create an issue in the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: Optional list of labels
            
        Returns:
            Created issue info
        """
        if not self.token:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "issue": {},
            }
        
        import aiohttp
        
        payload = {
            "title": title,
            "body": body,
        }
        
        if labels:
            payload["labels"] = labels
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/repos/{owner}/{repo}/issues",
                    headers=self.headers,
                    json=payload,
                ) as resp:
                    if resp.status != 201:
                        error_text = await resp.text()
                        return {
                            "success": False,
                            "error": f"Failed to create issue: {resp.status} - {error_text}",
                        }
                    
                    issue = await resp.json()
                    
                    return {
                        "success": True,
                        "issue": {
                            "number": issue.get("number"),
                            "title": issue.get("title"),
                            "url": issue.get("html_url"),
                            "state": issue.get("state"),
                        },
                    }
        except Exception as e:
            logger.error(f"GitHub issue creation error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> dict[str, Any]:
        """Create a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            body: PR body/description
            head: Branch name containing changes
            base: Target branch (default: main)
            
        Returns:
            Created PR info
        """
        if not self.token:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "pr": {},
            }
        
        import aiohttp
        
        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/repos/{owner}/{repo}/pulls",
                    headers=self.headers,
                    json=payload,
                ) as resp:
                    if resp.status != 201:
                        error_text = await resp.text()
                        return {
                            "success": False,
                            "error": f"Failed to create PR: {resp.status} - {error_text}",
                        }
                    
                    pr = await resp.json()
                    
                    return {
                        "success": True,
                        "pr": {
                            "number": pr.get("number"),
                            "title": pr.get("title"),
                            "url": pr.get("html_url"),
                            "state": pr.get("state"),
                            "base": pr.get("base", {}).get("ref"),
                            "head": pr.get("head", {}).get("ref"),
                        },
                    }
        except Exception as e:
            logger.error(f"GitHub PR creation error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: Optional[str] = None
    ) -> dict[str, Any]:
        """Get file content from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            branch: Optional branch (defaults to default branch)
            
        Returns:
            File content
        """
        if not self.token:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "content": "",
            }
        
        import aiohttp
        import base64
        
        params = {}
        if branch:
            params["ref"] = branch
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self.headers,
                    params=params,
                ) as resp:
                    if resp.status != 200:
                        return {
                            "success": False,
                            "error": f"Failed to get file: {resp.status}",
                        }
                    
                    data = await resp.json()
                    
                    # Decode base64 content
                    content = ""
                    if data.get("content"):
                        content = base64.b64decode(data["content"]).decode("utf-8")
                    
                    return {
                        "success": True,
                        "content": content,
                        "path": data.get("path"),
                        "sha": data.get("sha"),
                        "size": data.get("size"),
                    }
        except Exception as e:
            logger.error(f"GitHub file content error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open"
    ) -> dict[str, Any]:
        """List repository issues.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            
        Returns:
            List of issues
        """
        if not self.token:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "issues": [],
            }
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/repos/{owner}/{repo}/issues",
                    headers=self.headers,
                    params={"state": state, "per_page": 20},
                ) as resp:
                    if resp.status != 200:
                        return {
                            "success": False,
                            "error": f"Failed to list issues: {resp.status}",
                        }
                    
                    issues = await resp.json()
                    
                    return {
                        "success": True,
                        "issues": [
                            {
                                "number": i.get("number"),
                                "title": i.get("title"),
                                "state": i.get("state"),
                                "labels": [l.get("name") for l in i.get("labels", [])],
                                "url": i.get("html_url"),
                            }
                            for i in issues
                        ],
                    }
        except Exception as e:
            logger.error(f"GitHub list issues error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_workflow_status(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None
    ) -> dict[str, Any]:
        """Get workflow/CI status for repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Optional branch name
            
        Returns:
            Workflow status
        """
        if not self.token:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "status": "unavailable",
            }
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get latest commit status
                ref = branch or "main"
                
                async with session.get(
                    f"{self.api_base}/repos/{owner}/{repo}/commits/{ref}/status",
                    headers=self.headers,
                ) as resp:
                    if resp.status != 200:
                        return {
                            "success": False,
                            "error": f"Failed to get status: {resp.status}",
                        }
                    
                    status = await resp.json()
                    
                    return {
                        "success": True,
                        "status": status.get("state"),
                        "branch": ref,
                        "total_checks": len(status.get("statuses", [])),
                    }
        except Exception as e:
            logger.error(f"GitHub workflow status error: {e}")
            return {
                "success": False,
                "error": str(e),
            }


# Global instance
_github_engine: Optional[GitHubEngine] = None


def get_github_engine() -> GitHubEngine:
    """Get the GitHub engine instance."""
    global _github_engine
    
    if _github_engine is None:
        _github_engine = GitHubEngine()
    
    return _github_engine
