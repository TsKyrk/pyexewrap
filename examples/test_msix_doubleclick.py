#!/usr/bin/env python -m pyexewrap
"""Test script: double-cliquer sur ce fichier pour vérifier que pyexewrap est invoqué par le MSIX launcher.

Si pyexewrap fonctionne correctement, tu verras ce message et un prompt de pause à la fin.
Si le shebang est ignoré, la fenêtre flashera et disparaîtra sans prompt.
"""
import sys
import os

print("=" * 50)
print("  Test MSIX + pyexewrap")
print("=" * 50)
print(f"Python : {sys.executable}")
print(f"Script : {__file__}")
print(f"PROMPT env : {os.environ.get('PROMPT', '<not set>')}")
print(f"pyexewrap_simulate_doubleclick : {os.environ.get('pyexewrap_simulate_doubleclick', '<not set>')}")
print()
print("Si tu vois ce message ET un prompt de pause apres,")
print("pyexewrap fonctionne correctement avec le MSIX launcher.")
