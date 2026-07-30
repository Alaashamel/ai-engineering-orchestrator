from __future__ import annotations

from pathlib import Path


class FileSystemTool:
    def __init__(self, project_root: str):
        self.root = Path(project_root).resolve()

    def _resolve(self, path: str) -> Path:
        target = (self.root / path).resolve()
        if not str(target).startswith(str(self.root)):
            raise PermissionError(
                f"Access denied: {path} resolves outside project root"
            )
        return target

    def read_file(self, path: str) -> str:
        target = self._resolve(path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> str:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Written: {path}"

    def append_file(self, path: str, content: str) -> str:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        with open(target, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Appended: {path}" if existed else f"Created: {path}"

    def list_dir(self, path: str = ".") -> list[str]:
        target = self._resolve(path)
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        entries: list[str] = []
        for entry in sorted(target.iterdir()):
            suffix = "/" if entry.is_dir() else ""
            entries.append(f"{entry.name}{suffix}")
        return entries

    def delete_file(self, path: str) -> str:
        target = self._resolve(path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if target.is_file():
            target.unlink()
        elif target.is_dir():
            import shutil
            shutil.rmtree(target)
        return f"Deleted: {path}"

    def file_exists(self, path: str) -> bool:
        target = self._resolve(path)
        return target.exists()

    def list_files_by_extension(self, extension: str, base_path: str = ".") -> list[str]:
        target = self._resolve(base_path)
        files: list[str] = []
        for f in target.rglob(f"*{extension}"):
            rel = f.relative_to(self.root)
            files.append(str(rel.as_posix()))
        return sorted(files)
