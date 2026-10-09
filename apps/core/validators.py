import re

from django import forms

PHONE_RE = re.compile(r"^(?:\+?38)?(0\d{9})$")


def normalize_phone(value: str) -> str:
    match = PHONE_RE.match(re.sub(r"[\s()\-]", "", value))
    if not match:
        raise forms.ValidationError("Введіть український номер, наприклад +380991112233.")
    return f"+38{match.group(1)}"