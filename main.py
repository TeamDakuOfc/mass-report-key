import os
import requests
import hashlib
import time
import json
from time import sleep
from configparser import ConfigParser
from os import system, name
from threading import Thread, active_count
import csv
import phonenumbers
from phonenumbers import PhoneNumber, PhoneNumberFormat
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
import random
import re
from emailtools import generate
from datetime import datetime

# ========== LICENSE SYSTEM (UPDATED) ==========
GITHUB_LICENSE_URL = "https://raw.githubusercontent.com/TeamDakuOfc/mass-report-key/refs/heads/main/key.json"  # Yahan apna GitHub raw link dalo
GITHUB_REPO_URL = "https://github.com/TeamDakuOfc/mass-report-key.git"  # GitHub API for update
GITHUB_TOKEN = "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"  # Personal Access Token banao
LICENSE_CACHE_FILE = "license_cache.json"

software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value, SoftwareName.OPERA.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1200)

THREADS = 600
PROXIES_TYPES = ('http', 'socks4', 'socks5')

errors = open('errors.txt', 'a+')

time_out = 15
success_count = 0
error_count = 0
target_username = ""
target_link = ""
target_members = ""

class LicenseManager:
    def __init__(self):
        self.device_id = self._generate_device_id()
        self.keys_data = None
        self.current_key = None
        self.load_cache()
    
    def _generate_device_id(self):
        """Unique device fingerprint"""
        import platform
        import uuid
        mac = hex(uuid.getnode())
        hostname = platform.node()
        system_info = f"{platform.system()}_{platform.release()}"
        device_hash = hashlib.sha256(f"{hostname}_{mac}_{system_info}_{time.time()}".encode()).hexdigest()
        return device_hash[:16].upper()
    
    def load_cache(self):
        """Load cached license info"""
        try:
            if os.path.exists(LICENSE_CACHE_FILE):
                with open(LICENSE_CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                    if cache.get("device_id") == self.device_id:
                        self.current_key = cache.get("key")
                        print(f"✅ Cached license: {self.current_key[:8]}... for {self.device_id}")
        except:
            pass
    
    def save_cache(self, key):
        """Save license to local cache"""
        cache = {
            "device_id": self.device_id,
            "key": key,
            "activated": int(time.time())
        }
        with open(LICENSE_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    
    def fetch_keys(self):
        """GitHub se keys fetch"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(GITHUB_LICENSE_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                self.keys_data = response.json()
                return True
            return False
        except:
            print("⚠️ Cannot fetch license data (using cache)")
            return False
    
    def bind_device_to_key(self, key):
        """Key ko GitHub JSON mein device bind karega"""
        try:
            if not self.keys_data:
                self.fetch_keys()
            
            if not self.keys_data or "keys" not in self.keys_data:
                return False
            
            if key not in self.keys_data["keys"]:
                return False
            
            key_data = self.keys_data["keys"][key]
            
            # Already bound check
            if key_data.get("device_id") == self.device_id:
                return True
            
            # Update device_id
            key_data["device_id"] = self.device_id
            self.keys_data["keys"][key] = key_data
            
            # GitHub API se JSON update
            return self.update_github_json()
            
        except Exception as e:
            print(f"⚠️ Auto-binding failed: {e}")
            return True  # Offline continue karo
    
    def update_github_json(self):
        """GitHub repo mein JSON update"""
        try:
            # Current file content fetch
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(GITHUB_REPO_URL, headers=headers)
            if response.status_code != 200:
                return False
            
            file_data = response.json()
            current_content = file_data['content']
            current_sha = file_data['sha']
            
            # New content encode
            new_content = json.dumps(self.keys_data, indent=2)
            new_content_b64 = base64.b64encode(new_content.encode()).decode()
            
            # Update payload
            payload = {
                "message": f"Auto-bind device {self.device_id} to key",
                "content": new_content_b64,
                "sha": current_sha
            }
            
            update_response = requests.put(GITHUB_REPO_URL, headers=headers, json=payload)
            return update_response.status_code == 200
            
        except:
            return False
    
    def validate_key(self, key):
        """Complete key validation"""
        # Fetch latest data
        self.fetch_keys()
        
        if not self.keys_data or "keys" not in self.keys_data:
            return {"valid": False, "error": "Invalid license format"}
        
        key_data = self.keys_data["keys"].get(key)
        if not key_data:
            return {"valid": False, "error": "Invalid license key"}
        
        now = int(time.time())
        expires = key_data.get("expires", 0)
        
        # Expiry check
        if expires and expires < now:
            return {"valid": False, "error": f"License expired on {datetime.fromtimestamp(expires).strftime('%Y-%m-%d')}"}
        
        # Device binding (allow if null or matches)
        bound_device = key_data.get("device_id")
        if bound_device and bound_device != self.device_id:
            return {"valid": False, "error": f"Key bound to: {bound_device} (Yours: {self.device_id})"}
        
        # Auto bind if not bound
        if not bound_device:
            print(f"🔗 Binding device {self.device_id} to key...")
            if self.bind_device_to_key(key):
                print("✅ Device bound successfully!")
            else:
                print("⚠️ Auto-bind failed, continuing offline...")
        
        days_left = "∞" if not expires else max(0, (expires - now) // 86400)
        
        return {
            "valid": True,
            "expires": expires or 9999999999,
            "days_left": days_left,
            "features": ["full", "export", "api", "unlimited"],  # All features always
            "device_id": self.device_id,
            "key": key
        }
    
    def activate(self):
        """License activation"""
        print(f"\n🔑 DEVICE ID: {self.device_id}")
        print("-" * 50)
        
        # Try cache first
        if self.current_key:
            result = self.validate_key(self.current_key)
            if result["valid"]:
                self.show_license_banner(result)
                return result
        
        # Manual activation
        key = input("📝 Enter License Key: ").strip().upper()
        print("🔍 Validating...")
        
        result = self.validate_key(key)
        
        if result["valid"]:
            self.current_key = key
            self.save_cache(key)
            self.show_license_banner(result)
            return result
        else:
            print(f"\n❌ ERROR: {result['error']}")
            print("\n💡 Contact admin:")
            print("   Key: " + key)
            print("   Your Device: " + self.device_id)
            exit(1)
    
    def show_license_banner(self, info):
        """Premium license banner"""
        expires_date = "Never" if info["days_left"] == "∞" else datetime.fromtimestamp(info["expires"]).strftime("%Y-%m-%d")
        print("\n" + "="*80)
        print(f"""
\033[1;32m
███████╗███╗   ██╗███████╗ █████╗ ██████╗ ████████╗    ██████╗ ██╗  ██╗
██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██║ ██╔╝
█████╗  ██╔██╗ ██║█████╗  ███████║██║  ██║   ██║       ██████╔╝█████╔╝ 
██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██║██║  ██║   ██║       ██╔══██╗██╔═██╗ 
███████╗██║ ╚████║███████╗██║  ██║██████╔╝   ██║       ██████╔╝██║  ██╗
╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝       ╚═════╝ ╚═╝  ╚═╝
\033[1;36m                                             PREMIUM UNLIMITED v2.0\033[0m
        """)
        print(f"✅ \033[1;32mKey Activated:\033[0m {info['key']}")
        print(f"🔗 \033[1;35mDevice Bound:\033[0m {info['device_id']}")
        print(f"⏰ \033[1;33mExpires:\033[0m {expires_date} ({info['days_left']} days)")
        print(f"✨ \033[1;36mFeatures:\033[0m Full Access - Unlimited Threads/Targets")
        print("="*80 + "\n")

# Global license instance
license_mgr = LicenseManager()

# ========== ALL ORIGINAL CODE (UNCHANGED) ==========
def generate_random_phone_number():
    while True:
        country_code = "+{}".format(random.randint(1, 999))
        national_number = str(random.randint(1000000000, 9999999999))
        phone_number_str = country_code + national_number
        try:
            phone_number = phonenumbers.parse(phone_number_str)
            if phonenumbers.is_valid_number(phone_number):
                return phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            continue

def extract_username_from_link(link):
    patterns = [
        r't\.me/([a-zA-Z0-9_]+)',
        r'telegram\.me/([a-zA-Z0-9_]+)',
        r'telegram\.dog/([a-zA-Z0-9_]+)',
        r't\.me/joinchat/[^/]+',
        r'telegram\.me/joinchat/[^/]+',
        r'https://t\.me/([a-zA-Z0-9_]+)',
        r'https://telegram\.me/([a-zA-Z0-9_]+)',
        r'https://t\.me/+[^/]+',
        r'https://telegram\.dog/([a-zA-Z0-9_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return link

def get_random_line(filename, username, link, members):
    with open(filename, 'r') as file:
        lines = file.readlines()
        line = random.choice(lines).strip()
        return line.replace('{username}', username)\
                   .replace('{channel_link}', link)\
                   .replace('{member_count}', members)\
                   .replace('{admin}', username)

def control(proxy, proxy_type, username, link, members, mode):
    global success_count
    global error_count
    
    USER_AGENT = user_agent_rotator.get_random_user_agent()
    url = 'https://telegram.org/support'
    try:
        response = requests.get(url, proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'}, timeout=time_out)
    except AttributeError:
        error_count += 1
        pass
    except Exception as e:
        error_count += 1
        return errors.write(f'{e}\n')
        
    cookies = response.cookies
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', action="/support")

    if not form:
        print("Form not found on the page.")
        exit()

    if mode == "channelban":
        message_file = "channel_ban.txt"
        mode_display = "CHANNEL BAN 🔥"
    elif mode == "accountban":
        message_file = "account_ban.txt"
        mode_display = "ACCOUNT BAN 🔥"
    elif mode == "channelunban":
        message_file = "channel_unban.txt"
        mode_display = "CHANNEL UNBAN 🛡️"
    elif mode == "accountunban":
        message_file = "account_unban.txt"
        mode_display = "ACCOUNT UNBAN 🛡️"
    else:
        message_file = "message.txt"
        mode_display = "CUSTOM 📝"

    message = get_random_line(message_file, username, link, members)
    email = generate('gmail')
    phone = generate_random_phone_number()

    message_input = form.find('textarea', id='support_problem')
    email_input = form.find('input', id='support_email')
    phone_input = form.find('input', id='support_phone')

    if message_input:
        message_input['value'] = message
    if email_input:
        email_input['value'] = email
    if phone_input:
        phone_input['value'] = phone

    data = {input_tag['name']: input_tag.get('value', '') for input_tag in form.find_all(['input', 'textarea'])}

    hidden_inputs = form.find_all('input', type='hidden')
    for hidden_input in hidden_inputs:
        data[hidden_input['name']] = hidden_input['value']

    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.post(url, data=data, cookies=cookies, headers=headers)
        if response.status_code == 200:
            print(f"✅ [{mode_display}] {username} | {link[:30]}... | {members} members | Proxy: {proxy[:15]}...")
            success_count += 1
        else:
            error_count += 1
    except:
        error_count += 1
    
def get_views_from_saved_proxies(proxy_type, proxies, username, link, members, mode):
    for proxy in proxies:
        control(proxy.strip(), proxy_type, username, link, members, mode)

def start_view(username, link, members, mode):
    while True:
        threads = []
        for proxy_type in PROXIES_TYPES:
            with open(f"{proxy_type}_proxies.txt", 'r') as file:
                proxies = file.readlines()
            chunked_proxies = [proxies[i:i + 70] for i in range(0, len(proxies), 70)]
            for chunk in chunked_proxies:
                thread = Thread(target=get_views_from_saved_proxies, args=(proxy_type, chunk, username, link, members, mode))
                threads.append(thread)
                thread.start()
        for t in threads:
            t.join()

E = '\033[1;31m'
B = '\033[2;36m'
G = '\033[1;32m'
S = '\033[1;33m'
Y = '\033[1;33m'
P = '\033[1;35m'

def check_views(mode_display, username, link):
    global success_count, error_count
    
    while True:
        print(f'{G}[🚀 TOTAL THREADS ]: {B}{active_count()} ⇝⇝⇝⇝')
        print(f'{G}[✅ SUCCESS REPORTS ]: {S}{success_count}')
        print(f'{G}[❌ FAILED REPORTS ]: {E}{error_count}')
        print(f'{G}[📋 MODE]: {Y}{mode_display}')
        print(f'{G}[🎯 TARGET]: {P}{username} | {link}')
        print("-"*60)
        sleep(4)

def show_menu():
    print("\n" + "="*70)
    print(f"""
\033[1;32m
            ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
            ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
            ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║
            ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║
            ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝
            ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝
\033[1;31m                         Team -  G0D 0F B4NN3R\033[0m
""")
    print("=" * 70)
    print("\033[1;35m (1) 📢 Channel Ban   (2) 👤 Account Ban   (3) 📢 Channel Unban\033[0m")   
    print("\033[1;35m (4) 👤 Account Unban (5) 📝 Custom Mode\033[0m")
    print("=" * 70)

def get_target_info(mode):
    global target_username, target_link, target_members
    
    print(f"\n{G}🎯 TARGET INPUT ({mode.upper()})")
    print("-"*40)
    
    if "channel" in mode:
        target_link = input(f"{G}🔗 Enter Channel Link: {S}").strip()
        target_username = extract_username_from_link(target_link)
        print(f"{G}👤 Extracted Username: {P}{target_username}")
        
        admin_username = input(f"{G}👨‍💼 Enter Admin Username (or press Enter for channel): {S}")
        if admin_username.strip():
            target_username = admin_username.strip()
            print(f"{G}🎯 Using Admin: {P}{target_username}")
        
        target_members = input(f"{G}👥 Enter Member Count (or press Enter for random): {S}")
        if not target_members.strip():
            target_members = str(random.randint(1000, 50000))
        else:
            target_members = target_members.strip()
    else:
        target_username = input(f"{G}👤 Enter Account Username: {S}").strip()
        target_link = f"https://t.me/{target_username}"
        target_members = "N/A"
    
    print(f"\n{G}✅ TARGET READY!")
    print(f"{P}Username: {target_username}")
    print(f"{P}Link: {target_link}")
    print(f"{P}Members: {target_members}")

def main():
    # LICENSE CHECK FIRST
    license_info = license_mgr.activate()
    
    show_menu()
    choice = input(f"{G}💀 Select Mode (1-5): {S}")
    
    if choice == "1":
        mode = "channelban"
        mode_display = "CHANNEL BAN ATTACK 🔥"
    elif choice == "2":
        mode = "accountban"
        mode_display = "ACCOUNT BAN ATTACK 🔥"
    elif choice == "3":
        mode = "channelunban"
        mode_display = "CHANNEL UNBAN APPEAL 🛡️"
    elif choice == "4":
        mode = "accountunban"
        mode_display = "ACCOUNT UNBAN APPEAL 🛡️"
    elif choice == "5":
        mode = "custom"
        mode_display = "CUSTOM MODE 📝"
    else:
        print(f"{E}❌ Invalid choice!")
        exit()
    
    get_target_info(mode)
    
    print(f"\n{G}🚀 LAUNCHING {mode_display.upper()}")
    print(f"{G}📁 Using: {mode}.txt")
    
    Thread(target=start_view, args=(target_username, target_link, target_members, mode)).start()
    Thread(target=check_views, args=(mode_display, target_username, target_link)).start()

if __name__ == "__main__":
    main()