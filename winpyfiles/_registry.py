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


def write_value(hive: int, key_path: str, value: str, value_name: str = "") -> None:
    """Write a registry string value, creating the key if needed. Requires admin for HKLM."""
    with winreg.CreateKeyEx(hive, key_path, access=winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)


def delete_value(hive: int, key_path: str, value_name: str = "") -> None:
    """Delete a registry value. Silent if the key or value does not exist."""
    try:
        with winreg.OpenKey(hive, key_path, access=winreg.KEY_WRITE) as key:
            winreg.DeleteValue(key, value_name)
    except OSError:
        pass


def is_admin() -> bool:
    """Return True if the current process has administrator privileges."""
    import ctypes
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False
