import re
from typing import Optional

class WowheadParseHelper:

    @staticmethod
    def extract_content(pattern: str, html_string: str) -> Optional[str]:
        match = re.search(pattern, html_string)
        return match.group(1) if match else None
