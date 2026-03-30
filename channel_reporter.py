#!/usr/bin/env python3
import requests
import random
import time
import json
import hashlib
import ssl
import socket
from datetime import datetime
import os
import sys

# Termux colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

class FixedChannelReporter:
    def __init__(self):
        self.session = self.create_session()
        self.success = 0
        self.failed = 0
        self.rate_limited = False
        
    def create_session(self):
        """Create session with proper SSL handling for Termux"""
        session = requests.Session()
        
        # Bypass SSL verification issues in Termux
        session.verify = False
        
        # Set realistic headers
        session.headers.update({
            'User-Agent': self.random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
        })
        
        return session
    
    def random_user_agent(self):
        """Generate fresh user agent each request"""
        devices = [
            "SM-G998B", "iPhone14,2", "Pixel 6 Pro", "SM-F926B", 
            "Redmi Note 11", "OnePlus 9 Pro", "SM-A528B", "Xiaomi 12"
        ]
        device = random.choice(devices)
        
        if "iPhone" in device:
            return f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        else:
            android_ver = random.choice(["13", "12", "14"])
            chrome_ver = random.randint(110, 121)
            return f"Mozilla/5.0 (Linux; Android {android_ver}; {device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)} Mobile Safari/537.36"
    
    def extract_channel_id(self, channel_link):
        """Extract channel ID from any format"""
        channel_link = channel_link.strip()
        
        patterns = [
            "whatsapp.com/channel/",
            "wa.me/channel/",
            "chat.whatsapp.com/"
        ]
        
        for pattern in patterns:
            if pattern in channel_link:
                channel_id = channel_link.split(pattern)[-1].split("?")[0].split("/")[0]
                return channel_id.strip()
        
        # If no pattern matches, assume direct ID
        return channel_link
    
    def test_connection(self):
        """Test if internet connection works"""
        try:
            self.session.get("https://www.google.com", timeout=5)
            return True
        except:
            return False
    
    def submit_report(self, channel_id):
        """Submit report with multiple fallback methods"""
        
        if self.rate_limited:
            print(f"{YELLOW}  → Rate limited, cooling down...{RESET}")
            time.sleep(120)
            self.rate_limited = False
            self.session = self.create_session()
        
        # Multiple endpoints to try
        endpoints = [
            ("https://faq.whatsapp.com/contact/channel-abuse", "form"),
            ("https://www.whatsapp.com/contact/channel-abuse", "form"),
            ("https://web.whatsapp.com/channels/abuse", "json"),
        ]
        
        report_texts = [
            "Spam channel - sending unsolicited promotional content",
            "Harassment and abusive content in this channel",
            "Violation of WhatsApp channel policies - prohibited content",
            "Channel impersonating official organization",
            "Distributing harmful/misleading information"
        ]
        
        for endpoint, method in endpoints:
            try:
                payload = {
                    'channel': channel_id,
                    'report_type': random.randint(1, 8),
                    'description': random.choice(report_texts),
                    'timestamp': int(time.time()),
                    'session_id': hashlib.md5(os.urandom(16)).hexdigest()[:16]
                }
                
                if method == "form":
                    response = self.session.post(endpoint, data=payload, timeout=15)
                else:
                    response = self.session.post(endpoint, json=payload, timeout=15)
                
                if response.status_code == 200:
                    return True
                elif response.status_code == 429:
                    self.rate_limited = True
                    return False
                elif response.status_code in [403, 404]:
                    continue
                    
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                continue
            except Exception:
                continue
        
        return False
    
    def bulk_report(self, channel_id, count):
        """Send reports with adaptive delays"""
        
        print(f"\n{CYAN}╔════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║     CHANNEL REPORTING ACTIVE           ║{RESET}")
        print(f"{CYAN}╚════════════════════════════════════════╝{RESET}")
        print(f"{WHITE}Target: {YELLOW}{channel_id}{RESET}")
        print(f"{WHITE}Reports: {YELLOW}{count}{RESET}\n")
        
        # Test connection first
        print(f"{BLUE}[*] Testing connection...{RESET}", end=" ")
        if self.test_connection():
            print(f"{GREEN}OK{RESET}")
        else:
            print(f"{RED}FAILED - Check internet{RESET}")
            return
        
        for i in range(count):
            print(f"{WHITE}[{i+1}/{count}] Sending report{RESET}", end=" ")
            
            if self.submit_report(channel_id):
                self.success += 1
                print(f"{GREEN}✓ SUCCESS{RESET}")
                delay = random.uniform(3, 8)
            else:
                self.failed += 1
                print(f"{RED}✗ FAILED{RESET}")
                delay = random.uniform(8, 15)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                rate = (self.success / (i + 1)) * 100
                print(f"{BLUE}  → Progress: {i+1}/{count} | Success rate: {rate:.0f}%{RESET}")
            
            if i < count - 1:
                print(f"{BLUE}  → Waiting {delay:.0f}s{RESET}")
                time.sleep(delay)
        
        # Final summary
        print(f"\n{GREEN}════════════════════════════════════════{RESET}")
        print(f"{GREEN}[✓] COMPLETED{RESET}")
        print(f"{GREEN}[✓] Successful: {self.success}{RESET}")
        print(f"{RED}[✗] Failed: {self.failed}{RESET}")
        total = self.success + self.failed
        if total > 0:
            rate = (self.success / total) * 100
            print(f"{CYAN}[ℹ] Success Rate: {rate:.1f}%{RESET}")
        print(f"{GREEN}════════════════════════════════════════{RESET}")

def main():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════╗
║     WhatsApp Channel Reporter - E3 HACKER       ║
║           ONLY LINK REQUIRED- Termux Ready          ║
╚══════════════════════════════════════════════════╝{RESET}
    """)
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    reporter = FixedChannelReporter()
    
    # Get channel input
    channel_input = input(f"{WHITE}[?] Enter channel link or ID: {RESET}").strip()
    if not channel_input:
        print(f"{RED}[!] Channel required{RESET}")
        return
    
    channel_id = reporter.extract_channel_id(channel_input)
    print(f"{GREEN}[✓] Target: {channel_id}{RESET}")
    
    # Get report count
    try:
        count = int(input(f"{WHITE}[?] Number of reports (1-200): {RESET}") or "20")
        count = max(1, min(200, count))
    except:
        count = 20
    
    print(f"\n{YELLOW}[!] This will send {count} reports to channel{RESET}")
    confirm = input(f"{WHITE}[?] Continue? (y/n): {RESET}").lower()
    
    if confirm == 'y':
        reporter.bulk_report(channel_id, count)
    else:
        print(f"{RED}[!] Cancelled{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Interrupted{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
