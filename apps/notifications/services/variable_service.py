import re
from apps.core.constants.messages import MISSING_REQUIRED_VARIABLES

class VariableService:
    VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    @classmethod
    def extract_variables(cls, template_body: str) -> list[str]:
        if not template_body:
            return []
        return list(set(cls.VARIABLE_PATTERN.findall(template_body)))

    @classmethod
    def validate_context(cls, template_body: str, context: dict) -> tuple[bool, str]:
        required = cls.extract_variables(template_body)
        provided_keys = set(context.keys()) if context else set()
        missing = [var for var in required if var not in provided_keys]
        if missing:
            return False, f"{MISSING_REQUIRED_VARIABLES}{', '.join(missing)}"
        return True, ""

    @classmethod
    def render_template(cls, template_body: str, context: dict) -> str:
        if not template_body:
            return ""
        ctx = context or {}
        def replace_var(match):
            var_name = match.group(1).strip()
            return str(ctx.get(var_name, match.group(0)))
        return cls.VARIABLE_PATTERN.sub(replace_var, template_body)
