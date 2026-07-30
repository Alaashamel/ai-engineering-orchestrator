from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PromptTemplate(BaseModel):
    name: str
    template: str
    variables: list[str]
    version: str = "1.0"
    description: str = ""

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


class PromptTemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, list[PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> None:
        name = template.name
        if name not in self._templates:
            self._templates[name] = []
        self._templates[name].append(template)

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

    def update(self, template: PromptTemplate) -> None:
        self.register(template)

    def delete(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False