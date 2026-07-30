from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional


class PromptTemplate:
    def __init__(self, name: str, template: str, variables: list[str]):
        self.name = name
        self.template = template
        self.variables = variables

    def render(self, **kwargs: Any) -> str:
        rendered = self.template
        for var in self.variables:
            value = kwargs.get(var, f"{{{var}}}")
            rendered = rendered.replace(f"{{{var}}}", str(value))
        return rendered

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "template": self.template,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptTemplate":
        return cls(
            name=data["name"],
            template=data["template"],
            variables=data["variables"],
        )


class PromptTemplateManager:
    def __init__(self, templates_dir: str = "prompt_templates"):
        self.templates_dir = templates_dir
        self.templates: dict[str, PromptTemplate] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        path = Path(self.templates_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self._create_default_templates()
            return

        for file_path in path.glob("*.yaml"):
            import yaml

            with open(file_path) as f:
                data = yaml.safe_load(f)
            if data and "name" in data:
                template = PromptTemplate.from_dict(data)
                self.templates[template.name] = template

    def _create_default_templates(self) -> None:
        defaults = [
            PromptTemplate(
                name="project_plan",
                template=(
                    "Analyze the following idea and create a project plan:\n\n"
                    "Idea: {idea}\n\n"
                    "Break down the idea into:\n"
                    "1. Core features\n"
                    "2. Technical requirements\n"
                    "3. Architecture overview\n"
                    "4. Implementation plan\n"
                    "5. Testing strategy\n\n"
                    "Return a structured project plan."
                ),
                variables=["idea"],
            ),
            PromptTemplate(
                name="code_review",
                template=(
                    "Review the following code for quality, security, and best practices:\n\n"
                    "Code:\n{code}\n\n"
                    "Provide:\n"
                    "1. Issues found\n"
                    "2. Suggestions for improvement\n"
                    "3. Security concerns\n"
                    "4. Performance considerations"
                ),
                variables=["code"],
            ),
        ]
        for template in defaults:
            self.templates[template.name] = template
            self._save_template(template)

    def _save_template(self, template: PromptTemplate) -> None:
        path = Path(self.templates_dir) / f"{template.name}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        import yaml

        with open(path, "w") as f:
            yaml.dump(template.to_dict(), f, default_flow_style=False)

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        return self.templates.get(name)

    def list_templates(self) -> list[str]:
        return list(self.templates.keys())

    def register_template(self, template: PromptTemplate) -> None:
        self.templates[template.name] = template
        self._save_template(template)