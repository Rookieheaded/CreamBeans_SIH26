"""FastAPI dependency helpers."""

from backend.database.repository import Repository, get_repository


def repo_dependency() -> Repository:
    return get_repository()
