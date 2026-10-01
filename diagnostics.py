"""Short provider diagnostics with credentials removed."""
import re


def safe_error(exc, keys=()):
    message = str(exc)
    for key in keys:
        if key:
            message = message.replace(key, "[REDACTED]")
    message = re.sub(r"\b(?:gsk_|AIza)[A-Za-z0-9_-]+", "[REDACTED]", message)
    message = re.sub(r"(?i)(bearer\s+)[^\s\"']+", r"\1[REDACTED]", message)
    message = re.sub(r"(?i)((?:api[_-]?key|key|token)=)[^&\s]+", r"\1[REDACTED]", message)
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    return f"{type(exc).__name__}" + (f" · HTTP {code}" if code else "") + ": " + message[:1800]
