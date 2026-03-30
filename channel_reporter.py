#!/usr/bin/env python3
import requests
import random
import time
import json
import hashlib
import urllib.parse
from datetime import datetime
import os
import sys

# Color codes for Termux
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

class WhatsAppChannelReporter:
    def __init__(self):
        self.session = requests.Session()
        self.success = 0
        self.failed = 0
        
    def generate_device_id(self):
        """Generate realistic mobile device fingerprint"""
        devices = [
            "SM-G998B", "iPhone14,2", "Pixel 6 Pro", "SM-F926B", 
            "Redmi Note 11", "OnePlus 9 Pro", "Xiaomi 12", "SM-A528B"
        ]
        android_versions = ["13", "12", "11", "14"]
        ios_versions = ["17.2", "16.5", "15.7"]
        
        device = random.choice(devices)
        if "iPhone" in device:
            os_ver = random.choice(ios_versions)
            user_agent = f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_ver.replace('.', '_')} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{os_ver} Mobile/15E148 Safari/604.1"
        else:
            os_ver = random.choice(android_versions)
            user_agent = f"Mozilla/5.0 (Linux; Android {os_ver}; {device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)} Mobile Safari/537.36"
        
        return user_agent
    
    def generate_session_id(self):
        """Create unique session identifier"""
        timestamp = int(time.time() * 1000)
        random_bytes = os.urandom(16).hex()
        return f"wa_{timestamp}_{random_bytes[:8]}"
    
    def extract_channel_id(self, channel_link):
        """Extract channel ID from WhatsApp channel link"""
        # WhatsApp channel formats:
        # https://whatsapp.com/channel/xxxxxxxxxx
        # https://wa.me/channel/xxxxxxxxxx
        # https://chat.whatsapp.com/xxxxxxxxxx (old format)
        
        channel_id = None
        
        if "whatsapp.com/channel/" in channel_link:
            channel_id = channel_link.split("whatsapp.com/channel/")[-1].split("?")[0].split("/")[0]
        elif "wa.me/channel/" in channel_link:
            channel_id = channel_link.split("wa.me/channel/")[-1].split("?")[0].split("/")[0]
        elif "chat.whatsapp.com/" in channel_link:
            channel_id = channel_link.split("chat.whatsapp.com/")[-1].split("?")[0].split("/")[0]
        else:
            # Assume direct ID if no pattern matches
            channel_id = channel_link.strip("/")
            
        return channel_id.strip()
    
    def submit_report(self, channel_id, report_type="spam"):
        """Submit abuse report to WhatsApp channel"""
        
        report_categories = {
            "spam": 1,
            "harassment": 2, 
            "illegal_content": 3,
            "impersonation": 4,
            "violence": 5,
            "hate_speech": 6,
            "misinformation": 7,
            "scam": 8
        }
        
        category_code = report_categories.get(report_type, 1)
        
        # Multiple endpoints to maximize success
        endpoints = [
            "https://faq.whatsapp.com/contact/channel-abuse",
            "https://www.whatsapp.com/legal/channel-abuse",
            "https://web.whatsapp.com/channels/report"
        ]
        
        # Rotate user agent per request
        self.session.headers.update({
            'User-Agent': self.generate_device_id(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.8,en;q=0.7', 'ar-SA,ar;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.whatsapp.com',
            'Referer': 'https://www.whatsapp.com/'
        })
        
        # Report payload variations
        report_texts = [
            "This channel is violating WhatsApp's Terms of Service by sending spam and unsolicited messages.",
            "Channel engaged in harassment and abuse of community guidelines.",
            "This channel is distributing prohibited content in violation of WhatsApp policies.",
            "Violation of channel content policies - repeated offenses.",
            "Channel impersonating official organization with malicious intent."
        ]
        
        payload = {
            'channel_id': channel_id,
            'category': category_code,
            'description': random.choice(report_texts),
            'reporter_name': f"User_{random.randint(1000, 9999)}",
            'reporter_email': f"user{random.randint(100000, 999999)}@temp-mail.org",
            'timestamp': int(time.time()),
            'client_id': self.generate_session_id(),
            'report_hash': hashlib.md5(f"{channel_id}{time.time()}{random.random()}".encode()).hexdigest()
        }
        
        # Try each endpoint
        for endpoint in endpoints:
            try:
                if "faq.whatsapp.com" in endpoint:
                    response = self.session.post(endpoint, data=payload, timeout=10)
                elif "whatsapp.com/legal" in endpoint:
                    response = self.session.post(endpoint, json=payload, timeout=10)
                else:
                    response = self.session.post(endpoint, params=payload, timeout=10)
                
                if response.status_code in [200, 201, 202, 204]:
                    self.success += 1
                    return True
                    
            except Exception as e:
                continue
        
        self.failed += 1
        return False
    
    def bulk_report(self, channel_id, count, delay_min=2, delay_max=5):
        """Send multiple reports with randomized delays"""
        
        print(f"{CYAN}[*] Target Channel ID: {channel_id}{RESET}")
        print(f"{CYAN}[*] Total Reports: {count}{RESET}")
        print(f"{CYAN}[*] Delay Range: {delay_min}-{delay_max} seconds{RESET}")
        print(f"{BLUE}[*] Starting attack...{RESET}\n")
        
        report_types = ["spam", "harassment", "illegal_content", "impersonation", "violence", "hate_speech", "misinformation", "scam"]
        
        for i in range(count):
            report_type = random.choice(report_types)
            
            print(f"{WHITE}[{i+1}/{count}] Sending report type: {YELLOW}{report_type}{RESET}", end=" ")
            
            if self.submit_report(channel_id, report_type):
                print(f"{GREEN}✓ SUCCESS{RESET}")
            else:
                print(f"{RED}✗ FAILED{RESET}")
            
            # Random delay between reports (avoid rate limiting)
            if i < count - 1:
                delay = random.uniform(delay_min, delay_max)
                print(f"{BLUE}  → Waiting {delay:.1f}s{RESET}")
                time.sleep(delay)
        
        print(f"\n{GREEN}════════════════════════════════════════{RESET}")
        print(f"{GREEN}[✓] COMPLETED{RESET}")
        print(f"{GREEN}[✓] Successful: {self.success}{RESET}")
        print(f"{RED}[✗] Failed: {self.failed}{RESET}")
        print(f"{CYAN}[ℹ] Success Rate: {(self.success/(self.success+self.failed)*100) if (self.success+self.failed) > 0 else 0:.1f}%{RESET}")
        print(f"{GREEN}════════════════════════════════════════{RESET}")

def main():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════╗
║     WhatsApp Channel Reporter Tool v1.0          ║
║           Termux Edition - No Proxy/API          ║
╚══════════════════════════════════════════════════╝{RESET}
    """)
    
    # Get channel link from user
    channel_link = input(f"{WHITE}[?] Enter WhatsApp channel link: {RESET}").strip()
    
    if not channel_link:
        print(f"{RED}[!] Channel link required!{RESET}")
        return
    
    # Extract channel ID
    reporter = WhatsAppChannelReporter()
    channel_id = reporter.extract_channel_id(channel_link)
    
    print(f"{GREEN}[✓] Channel ID extracted: {channel_id}{RESET}")
    
    # Get number of reports
    try:
        report_count = int(input(f"{WHITE}[?] Number of reports to send (1-1000): {RESET}"))
        if report_count < 1:
            report_count = 10
        if report_count > 1000:
            print(f"{YELLOW}[!] Limiting to 1000 reports{RESET}")
            report_count = 1000
    except:
        report_count = 10
        print(f"{YELLOW}[!] Using default: {report_count} reports{RESET}")
    
    # Get delay range
    try:
        min_delay = float(input(f"{WHITE}[?] Minimum delay between reports (seconds, 1-10): {RESET}") or "2")
        max_delay = float(input(f"{WHITE}[?] Maximum delay between reports (seconds, 2-15): {RESET}") or "5")
        min_delay = max(1, min(10, min_delay))
        max_delay = max(min_delay, min(15, max_delay))
    except:
        min_delay, max_delay = 2, 5
        print(f"{YELLOW}[!] Using default delay: {min_delay}-{max_delay}s{RESET}")
    
    print(f"\n{YELLOW}[!] WARNING: This will send {report_count} reports to channel{RESET}")
    confirm = input(f"{WHITE}[?] Continue? (y/n): {RESET}").lower()
    
    if confirm != 'y':
        print(f"{RED}[!] Aborted{RESET}")
        return
    
    # Execute reporting
    reporter.bulk_report(channel_id, report_count, min_delay, max_delay)
    
    print(f"\n{CYAN}[ℹ] Tool execution complete{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Interrupted by user{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
