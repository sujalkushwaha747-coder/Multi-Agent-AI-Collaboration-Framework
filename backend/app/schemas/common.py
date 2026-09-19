from typing import Literal

TaskCategory = Literal["academic", "technical", "general"]
RunMode = Literal["single", "multi", "both"]


class ErrorResponse(dict):
    detail: str

