#!/bin/bash

# Colors for Termux
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
RESET='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║     WhatsApp Channel Reporter         ║${RESET}"
echo -e "${CYAN}║           Bash Edition                ║${RESET}"
echo -e "${CYAN}╚════════════════════════════════════════╝${RESET}"
echo ""

# Get channel ID
echo -ne "${WHITE}[?] Enter channel link or ID: ${RESET}"
read channel_input

# Extract channel ID
channel_id=$(echo "$channel_input" | sed -n 's/.*channel\/\([^?]*\).*/\1/p')
if [ -z "$channel_id" ]; then
    channel_id="$channel_input"
fi

echo -e "${GREEN}[✓] Target: $channel_id${RESET}"

# Get number of reports
echo -ne "${WHITE}[?] Number of reports (1-100): ${RESET}"
read report_count
if [ -z "$report_count" ]; then
    report_count=20
fi

# Get delay between reports
echo -ne "${WHITE}[?] Delay between reports (seconds, 2-10): ${RESET}"
read delay
if [ -z "$delay" ]; then
    delay=3
fi

echo ""
echo -e "${YELLOW}[!] This will send $report_count reports to channel${RESET}"
echo -ne "${WHITE}[?] Continue? (y/n): ${RESET}"
read confirm

if [ "$confirm" != "y" ]; then
    echo -e "${RED}[!] Cancelled${RESET}"
    exit 0
fi

echo ""
echo -e "${BLUE}[*] Starting attack...${RESET}"
echo ""

success=0
failed=0

for i in $(seq 1 $report_count); do
    echo -ne "${WHITE}[$i/$report_count] Sending report${RESET} "
    
    # Random user agent
    ua="Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36"
    
    # Send report using curl
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "https://faq.whatsapp.com/contact/channel-abuse" \
        -H "User-Agent: $ua" \
        -H "Accept: text/html,application/xhtml+xml" \
        -H "Accept-Language: en-US,en;q=0.9" \
        -d "channel=$channel_id&report_type=1&description=Spam%20channel%20violating%20WhatsApp%20policies" \
        --max-time 10 \
        --insecure 2>/dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "202" ]; then
        echo -e "${GREEN}✓ SUCCESS${RESET}"
        ((success++))
        sleep_time=$delay
    else
        echo -e "${RED}✗ FAILED (HTTP $response)${RESET}"
        ((failed++))
        sleep_time=$((delay + 2))
    fi
    
    # Progress every 10 reports
    if [ $((i % 10)) -eq 0 ]; then
        rate=$((success * 100 / i))
        echo -e "${BLUE}  → Progress: $i/$report_count | Success rate: $rate%${RESET}"
    fi
    
    # Wait between reports
    if [ $i -lt $report_count ]; then
        echo -e "${BLUE}  → Waiting ${sleep_time}s${RESET}"
        sleep $sleep_time
    fi
done

# Summary
echo ""
echo -e "${GREEN}════════════════════════════════════════${RESET}"
echo -e "${GREEN}[✓] COMPLETED${RESET}"
echo -e "${GREEN}[✓] Successful: $success${RESET}"
echo -e "${RED}[✗] Failed: $failed${RESET}"
total=$((success + failed))
if [ $total -gt 0 ]; then
    rate=$((success * 100 / total))
    echo -e "${CYAN}[ℹ] Success Rate: ${rate}%${RESET}"
fi
echo -e "${GREEN}════════════════════════════════════════${RESET}"
