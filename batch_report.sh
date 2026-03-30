#!/bin/bash

# List of channels
channels=(
    "https://whatsapp.com/channel/ABC123"
    "https://whatsapp.com/channel/DEF456"
    "https://whatsapp.com/channel/GHI789"
)

for channel in "${channels[@]}"; do
    echo "[*] Reporting channel: $channel"
    python channel_reporter.py --channel "$channel" --reports 50 --auto
    sleep 30
done
