"""Parses a legacy Python codebase and extracts function-level source,
filtered by a complexity threshold so trivial helpers don't waste
downstream AI review budget."""

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FunctionCandidate:
    name: str
    file: str
    source: str
    line_count: int


def _count_branches(node: ast.AST) -> int:
    """Cheap proxy for cyclomatic complexity: counts branching nodes."""
    branch_types = (ast.If, ast.For, ast.While, ast.Try, ast.With)
    return sum(1 for n in ast.walk(node) if isinstance(n, branch_types))


def scan_file(filepath: Path, min_branches: int = 1) -> list[FunctionCandidate]:
    source = filepath.read_text(errors="ignore")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _count_branches(node) < min_branches:
                continue
            func_source = ast.get_source_segment(source, node) or ""
            candidates.append(
                FunctionCandidate(
                    name=node.name,
                    file=str(filepath),
                    source=func_source,
                    line_count=func_source.count("\n") + 1,
                )
            )
    return candidates


def scan_directory(root: str, min_branches: int = 1, extensions: tuple[str, ...] = (".py",)) -> list[FunctionCandidate]:
    root_path = Path(root)
    results: list[FunctionCandidate] = []
    for ext in extensions:
        for filepath in root_path.rglob(f"*{ext}"):
            results.extend(scan_file(filepath, min_branches=min_branches))
    return results
