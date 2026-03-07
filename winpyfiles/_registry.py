"""Low-level Windows registry helpers. No business logic here."""
import winreg
from typing import Optional

HKCR = winreg.HKEY_CLASSES_ROOT
HKCU = winreg.HKEY_CURRENT_USER
HKLM = winreg.HKEY_LOCAL_MACHINE

HIVE_LABELS = {
    HKCR: "HKCR",
    HKCU: "HKCU",
    HKLM: "HKLM",
}


def read_value(hive: int, key_path: str, value_name: str = "") -> Optional[str]:
    """Return a registry string value, or None if the key/value is absent."""
    try:
        with winreg.OpenKey(hive, key_path) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return str(value)
    except OSError:
        return None
