"""Log filter that scrubs API key patterns from log messages."""

import logging
import re

# Patterns for known API key formats
_KEY_PATTERNS = re.compile(
    r"(sk-ant-api03-[A-Za-z0-9_-]{20,})"  # Anthropic
    r"|(sk-[A-Za-z0-9]{20,})"              # OpenAI
    r"|(AIza[A-Za-z0-9_-]{30,})"           # Google
)


class KeyScrubFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _KEY_PATTERNS.sub("[REDACTED]", record.msg)
        if record.args:
            scrubbed = []
            for arg in record.args if isinstance(record.args, tuple) else (record.args,):
                if isinstance(arg, str):
                    scrubbed.append(_KEY_PATTERNS.sub("[REDACTED]", arg))
                else:
                    scrubbed.append(arg)
            record.args = tuple(scrubbed)
        return True
