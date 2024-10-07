from typing import Any, Dict, Optional

import json
from attrs import define, asdict


CONTENT_TYPES = {}


class Content:
    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:
        super().__init_subclass__(**kwargs)
        CONTENT_TYPES[cls.__name__] = cls

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self, recurse=True)
        data["type"] = self.__class__.__name__
        return data


@define
class Text(Content):
    text: str

    @property
    def summary(self):
        return "content:text\n" + self.text



@define
class ToolUse(Content):
    id: str
    name: str
    parameters: Any
    is_error: bool = False
    error_message: Optional[str] = None

    @property
    def summary(self):
        return f"content:tool_use:{self.name}\nparameters:{json.dumps(self.parameters)}"


@define
class ToolResult(Content):
    tool_use_id: str
    output: str
    is_error: bool = False

    @property
    def summary(self):
        return f"content:tool_result:error={self.is_error}\noutput:{self.output}"
