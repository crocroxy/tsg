#!/usr/bin/env python3
"""
Continuously takes an Android screenshot via Termux API every INTERVAL seconds
and sends it to a configured webhook URL.

Requirements:
  • Termux API package: pkg install termux-api
  • Python requests: pip install requests
  • (Optional) termux-setup-storage if you need shared storage

Usage:
  • Edit WEBHOOK_URL to your endpoint
  • Run: python3 screenshot_service.py
"""
import os
import time
import subprocess
import requests
import json

# ===== Configuration =====
WEBHOOK_URL = "https://discord.com/api/webhooks/1365025141070893056/mdwqSvclv66nmHYpf-n-2VcG7K5pZCbGy-5ksKL4Cw_xumBSgD6Z1LECZJOa9eqJXE_-"
INTERVAL = 600          # Time between screenshots in seconds (10 minutes)
OUT_DIR = os.path.expanduser("~/screenshots")
CONFIG_FILE = os.path.expanduser("~/.screenshot_service_config.json")
# =========================

def screenshot_and_send(username):
    os.makedirs(OUT_DIR, exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'screenshot_{timestamp}.png'
    filepath = os.path.join(OUT_DIR, filename)
    # Capture screenshot
    subprocess.run(['termux-screenshot', '-f', filepath], check=True)
    # Send via webhook with embed
    with open(filepath, 'rb') as f:
        payload = {
            "username": username,
            "embeds": [{
                "title": f"Screenshot from {username}",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "image": {"url": f"attachment://{filename}"},
                "color": 0x00ff00,
                "footer": {"text": timestamp}
            }]
        }
        response = requests.post(
            WEBHOOK_URL,
            data={'payload_json': json.dumps(payload)},
            files={'file': (filename, f, 'image/png')}
        )
    print(f"[{timestamp}] Sent {filename}, status {response.status_code}")


def main():
    # Load or prompt for username
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as cf:
            name = json.load(cf).get('username')
    else:
        name = input("Enter your name for screenshot embeds: ").strip()
        with open(CONFIG_FILE, 'w') as cf:
            json.dump({'username': name}, cf)
    print(f"Starting screenshot loop: every {INTERVAL}s -> {WEBHOOK_URL} as {name}")
    while True:
        try:
            screenshot_and_send(name)
        except Exception as e:
            print(f"Error during capture/send: {e}")
        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()
