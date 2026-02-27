"""Coding tools — file I/O, code search, and sandboxed command execution."""

import glob as _glob
import logging
import os
import subprocess

from langchain_core.tools import tool

from app.config import settings

logger = logging.getLogger(__name__)

_OUTPUT_LIMIT = 50_000  # chars — prevents blowing up LLM context


def _resolve_workspace_path(relative_path: str) -> str:
    """Resolve *relative_path* against WORKSPACE_DIR.

    Raises ValueError if the resolved path escapes the workspace (e.g. via
    ``..`` traversal).
    """
    workspace = os.path.realpath(settings.WORKSPACE_DIR)
    resolved = os.path.realpath(os.path.join(workspace, relative_path))
    if not resolved.startswith(workspace + os.sep) and resolved != workspace:
        raise ValueError(
            f"Path traversal blocked: '{relative_path}' resolves outside workspace"
        )
    return resolved


# ---------------------------------------------------------------------------
# File I/O tools
# ---------------------------------------------------------------------------


@tool
def read_file(path: str) -> str:
    """Read the contents of a file in the workspace.

    Args:
        path: Relative path inside the workspace (e.g. ``src/main.py``).
    """
    try:
        resolved = _resolve_workspace_path(path)
    except ValueError as exc:
        return f"Error: {exc}"

    try:
        with open(resolved, "r", errors="replace") as fh:
            content = fh.read(_OUTPUT_LIMIT)
        if len(content) == _OUTPUT_LIMIT:
            content += "\n... [truncated at 50 000 chars]"
        return content
    except FileNotFoundError:
        return f"Error: file not found — {path}"
    except Exception as exc:
        return f"Error reading file: {exc}"


@tool
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file in the workspace.

    Args:
        path: Relative path inside the workspace.
        content: The full text content to write.
    """
    try:
        resolved = _resolve_workspace_path(path)
    except ValueError as exc:
        return f"Error: {exc}"

    try:
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "w") as fh:
            fh.write(content)
        byte_count = os.path.getsize(resolved)
        return f"Wrote {byte_count} bytes to {path}"
    except Exception as exc:
        return f"Error writing file: {exc}"


# ---------------------------------------------------------------------------
# Directory listing
# ---------------------------------------------------------------------------


@tool
def list_files(directory: str = ".", pattern: str = "*") -> str:
    """List files in the workspace matching a glob pattern.

    Args:
        directory: Relative directory inside the workspace (default root).
        pattern: Glob pattern (e.g. ``**/*.py`` for recursive Python files).
    """
    try:
        resolved = _resolve_workspace_path(directory)
    except ValueError as exc:
        return f"Error: {exc}"

    workspace = os.path.realpath(settings.WORKSPACE_DIR)
    full_pattern = os.path.join(resolved, pattern)
    matches = sorted(_glob.glob(full_pattern, recursive=True))

    # Return workspace-relative paths
    rel_paths = []
    for m in matches:
        if os.path.isfile(m):
            rel_paths.append(os.path.relpath(m, workspace))

    if not rel_paths:
        return "No files matched."

    output = "\n".join(rel_paths)
    if len(output) > _OUTPUT_LIMIT:
        output = output[:_OUTPUT_LIMIT] + "\n... [truncated]"
    return output


# ---------------------------------------------------------------------------
# Code search (runs directly on the API container — safe, read-only grep)
# ---------------------------------------------------------------------------


@tool
def search_code(query: str, path: str = ".", file_pattern: str = "") -> str:
    """Search for a text pattern in workspace files using grep.

    Args:
        query: The regex or literal string to search for.
        path: Relative directory to search within (default workspace root).
        file_pattern: Optional glob to restrict file types (e.g. ``*.py``).
    """
    try:
        resolved = _resolve_workspace_path(path)
    except ValueError as exc:
        return f"Error: {exc}"

    cmd = ["grep", "-rn", query, resolved]
    if file_pattern:
        cmd.insert(2, f"--include={file_pattern}")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
    except subprocess.TimeoutExpired:
        return "Error: search timed out after 15 seconds."

    output = result.stdout or result.stderr or "No matches found."

    # Strip absolute workspace prefix for cleaner output
    workspace = os.path.realpath(settings.WORKSPACE_DIR)
    output = output.replace(workspace + os.sep, "")

    if len(output) > _OUTPUT_LIMIT:
        output = output[:_OUTPUT_LIMIT] + "\n... [truncated]"
    return output


# ---------------------------------------------------------------------------
# Command execution — local or Docker sandboxed
# ---------------------------------------------------------------------------


@tool
def run_command(command: str, timeout: int = 0) -> str:
    """Run a shell command in the workspace directory.

    Depending on server configuration this runs either directly on the host
    (``SANDBOX_MODE=local``) or inside a Docker container
    (``SANDBOX_MODE=docker``).

    Args:
        command: The shell command to execute (passed to ``sh -c``).
        timeout: Max seconds to wait (0 = use server default, capped at 300).
    """
    if settings.SANDBOX_MODE == "local":
        return _run_local(command, timeout)
    return _run_docker(command, timeout)


def _run_local(command: str, timeout: int) -> str:
    """Execute a command directly on the host inside WORKSPACE_DIR."""
    effective_timeout = timeout if timeout > 0 else settings.SANDBOX_TIMEOUT
    effective_timeout = min(effective_timeout, 300)

    workspace = os.path.realpath(settings.WORKSPACE_DIR)
    os.makedirs(workspace, exist_ok=True)

    try:
        result = subprocess.run(
            ["sh", "-c", command],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=effective_timeout,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        output = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}\nEXIT CODE: {result.returncode}"

        if len(output) > _OUTPUT_LIMIT:
            output = output[:_OUTPUT_LIMIT] + "\n... [truncated]"
        return output

    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {effective_timeout}s"
    except Exception as exc:
        return f"Error running command: {exc}"


def _run_docker(command: str, timeout: int) -> str:
    """Execute a command inside a sandboxed Docker container."""
    try:
        import docker
    except ImportError:
        return "Error: Docker Python SDK is not installed. Run: pip install docker"

    effective_timeout = timeout if timeout > 0 else settings.SANDBOX_TIMEOUT
    effective_timeout = min(effective_timeout, 300)

    container = None
    try:
        client = docker.from_env()

        workspace_abs = os.path.realpath(settings.WORKSPACE_DIR)
        os.makedirs(workspace_abs, exist_ok=True)

        container = client.containers.run(
            image=settings.SANDBOX_IMAGE,
            command=["sh", "-c", command],
            working_dir="/workspace",
            volumes={
                workspace_abs: {"bind": "/workspace", "mode": "rw"},
            },
            network_mode="none" if not settings.SANDBOX_NETWORK else "bridge",
            mem_limit="512m",
            nano_cpus=500_000_000,  # 50 % of one CPU
            detach=True,
        )

        result = container.wait(timeout=effective_timeout)
        exit_code = result.get("StatusCode", -1)

        stdout = container.logs(stdout=True, stderr=False).decode(
            "utf-8", errors="replace"
        )
        stderr = container.logs(stdout=False, stderr=True).decode(
            "utf-8", errors="replace"
        )

        output = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}\nEXIT CODE: {exit_code}"

        if len(output) > _OUTPUT_LIMIT:
            output = output[:_OUTPUT_LIMIT] + "\n... [truncated]"
        return output

    except Exception as exc:
        return f"Error running command: {exc}"
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except Exception:
                pass
