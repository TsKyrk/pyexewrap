"""winpyfiles — Windows Python file association manager."""
from ._assoc import diagnose, AssocDiagnosis, ExtensionInfo, ProgIdInfo

__all__ = ["diagnose", "AssocDiagnosis", "ExtensionInfo", "ProgIdInfo"]
