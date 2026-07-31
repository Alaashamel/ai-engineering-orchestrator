from __future__ import annotations

import difflib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


class PromptTemplate(BaseModel):
    name: str
    template: str
    variables: list[str]
    version: str = "1.0"
    description: str = ""
    tags: list[str] = []
    created_at: str = ""
    created_by: str = "system"

    def render(self, **kwargs: Any) -> str:
        rendered = self.template
        for var in self.variables:
            value = kwargs.get(var, f"{{{var}}}")
            rendered = rendered.replace(f"{{{var}}}", str(value))
        return rendered


class PromptTemplateVersion(BaseModel):
    template_name: str
    version: str
    template: str
    variables: list[str]
    created_at: str = ""
    created_by: str = "system"
    tags: list[str] = []
    description: str = ""
    diff_from_previous: str = ""


class PromptTemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, list[PromptTemplate]] = {}
        self._version_tags: dict[str, dict[str, str]] = {}

    def register(self, template: PromptTemplate) -> None:
        name = template.name
        if not template.created_at:
            template.created_at = datetime.now(timezone.utc).isoformat()
        if name not in self._templates:
            self._templates[name] = []
        self._templates[name].append(template)
        return template

    def get_latest(self, name: str) -> PromptTemplate | None:
        versions = self._templates.get(name, [])
        if not versions:
            return None
        return versions[-1]

    def get_version(self, name: str, version: str) -> PromptTemplate | None:
        versions = self._templates.get(name, [])
        for t in versions:
            if t.version == version:
                return t
        return None

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def list_versions(self, name: str) -> list[str]:
        versions = self._templates.get(name, [])
        return [t.version for t in versions]

    def diff(self, name: str, version_a: str, version_b: str) -> str:
        a = self.get_version(name, version_a)
        b = self.get_version(name, version_b)
        if not a or not b:
            return f"Cannot diff: version(s) not found for '{name}'"
        diff = difflib.unified_diff(
            a.template.splitlines(keepends=True),
            b.template.splitlines(keepends=True),
            fromfile=f"{name} v{version_a}",
            tofile=f"{name} v{version_b}",
        )
        return "".join(diff)

    def rollback(self, name: str, target_version: str) -> PromptTemplate | None:
        versions = self._templates.get(name, [])
        target = self.get_version(name, target_version)
        if not target:
            return None
        new_version = self._bump_version(versions[-1].version if versions else "0.0")
        rolled = PromptTemplate(
            name=name,
            template=target.template,
            variables=target.variables,
            version=new_version,
            description=f"Rollback to v{target_version}: {target.description}",
            tags=target.tags + ["rollback"],
            created_by="system",
        )
        self.register(rolled)
        return rolled

    def tag_version(self, name: str, version: str, tag: str) -> bool:
        tmpl = self.get_version(name, version)
        if not tmpl:
            return False
        if name not in self._version_tags:
            self._version_tags[name] = {}
        self._version_tags[name][tag] = version
        return True

    def get_by_tag(self, name: str, tag: str) -> PromptTemplate | None:
        tags = self._version_tags.get(name, {})
        version = tags.get(tag)
        if not version:
            return None
        return self.get_version(name, version)

    def list_tags(self, name: str) -> dict[str, str]:
        return self._version_tags.get(name, {})

    def get_version_history(self, name: str) -> list[dict[str, Any]]:
        versions = self._templates.get(name, [])
        history = []
        for i, v in enumerate(versions):
            entry: dict[str, Any] = {
                "version": v.version,
                "description": v.description,
                "created_at": v.created_at,
                "created_by": v.created_by,
                "tags": v.tags,
            }
            if i > 0:
                entry["diff_from_previous"] = self.diff(
                    name, versions[i - 1].version, v.version
                )
            history.append(entry)
        return history

    def update(self, template: PromptTemplate) -> PromptTemplate:
        existing = self.get_latest(template.name)
        new_version = self._bump_version(
            existing.version if existing else "0.0"
        )
        template.version = new_version
        if not template.created_at:
            template.created_at = datetime.now(timezone.utc).isoformat()
        self.register(template)
        return template

    def delete(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            self._version_tags.pop(name, None)
            return True
        return False

    @staticmethod
    def _bump_version(current: str) -> str:
        parts = current.split(".")
        if len(parts) == 2:
            major, minor = parts
            return f"{major}.{int(minor) + 1}"
        return f"{current}.1"
