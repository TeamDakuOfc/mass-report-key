#!/usr/bin/env python3
"""
🔥 Admin Runner - For testing GitHub updates
GitHub: https://github.com/TeamDakuOfc/mass-report-key
"""
import requests
import subprocess
import sys
import tempfile

GITHUB_MAIN_URL = "https://raw.githubusercontent.com/TeamDakuOfc/mass-report-key/main/main.py"

print("🛠️ Admin Test Runner")
response = requests.get(GITHUB_MAIN_URL)
if response.status_code == 200:
    exec(response.text)
else:
    print("❌ Update failed!")
