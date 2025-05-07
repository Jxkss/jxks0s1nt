import re
import os
import sys
import time
import json
import base64
import random
import asyncio
import getpass
import aiohttp
import requests
import ipaddress
import threading
import itertools
import webbrowser
from pythonping import ping
from pystyle import Colors, Colorate

CURRENT_VERSION = '2.1.3'

REPO_OWNER = "Jxkss"
REPO_NAME = "jxks0s1nt"

current_user = getpass.getuser()
proxy_failure_count = 0

os.system('title jxks0s1nt')

def colored_spinner(duration, message="Loading...", color_style=Colors.cyan_to_green):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    end_time = time.time() + duration
    
    def spin():
        while time.time() < end_time:
            sys.stdout.write('\r' + Colorate.Horizontal(color_style, f"{next(spinner)} {message}"))
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')
        sys.stdout.flush()
    
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.start()
    spinner_thread.join()

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return json.loads(content)
    except FileNotFoundError:
        print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] File not found: {file_path}"))
        return None
    except json.JSONDecodeError as e:
        print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] JSON decode error in {file_path}: {e}"))
        return None
    except Exception as e:
        print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] Error reading {file_path}: {e}"))
        return None

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_random_proxy():
    proxies = read_json('proxies.json')
    if proxies and len(proxies) > 0:
        return random.choice(proxies)
    return None

tested_proxies = {}

def get_working_proxy(max_failures=5, retry_count=0):
    global proxy_failure_count
    
    if retry_count > 3:
        print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Maximum retry attempts reached. Continuing without proxy."))
        return None
    
    proxies = read_json('proxies.json')
    if not proxies or len(proxies) == 0:
        print(Colorate.Horizontal(Colors.red_to_yellow, "[X] No proxies available in proxies.json. Add some in the Proxy Manager."))
        return None
    
    if retry_count > 0:
        proxy_failure_count = 0
    
    available_proxies = proxies.copy()
    
    while available_proxies and proxy_failure_count < max_failures:
        proxy = random.choice(available_proxies)
        available_proxies.remove(proxy)
        
        if retry_count > 0:
            if proxy in tested_proxies:
                tested_proxies[proxy] = False
        
        if proxy in tested_proxies and tested_proxies[proxy]:
            print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] Using previously verified proxy: {proxy}"))
            return proxy
        
        print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] Testing proxy: {proxy}"))
        if test_proxy(proxy):
            print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] Proxy test successful: {proxy}"))
            tested_proxies[proxy] = True
            proxy_failure_count = 0
            return proxy
        else:
            tested_proxies[proxy] = False
            proxy_failure_count += 1
            print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] Proxy test failed: {proxy} (Failure {proxy_failure_count}/{max_failures})"))
    
    if not available_proxies or proxy_failure_count >= max_failures:
        user_choice = input(Colorate.Horizontal(Colors.cyan_to_green, 
            f"[?] Failed to connect with {len(proxies)} different proxies. Continue trying with proxies? (Y/N): ")).strip().lower()
        if user_choice != 'y':
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Continuing without proxy."))
            proxy_failure_count = 0
            return None
        else:
            proxy_failure_count = 0
            
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Retrying with all proxies..."))
            return get_working_proxy(max_failures, retry_count + 1)
    
    print(" ")
    return None

def test_proxy(proxy):
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] Proxy test failed: {e}"))
        return False

def setup_proxy():
    config = read_json('config.json')

    if config:
        use_proxy = config.get('use_proxy', False)
    else:
        print(Colorate.Horizontal(Colors.cyan_to_green, "/"))
        user_input = input(Colorate.Horizontal(Colors.cyan_to_green, "[?] Do you want to use proxies for every request? (Y/N): ")).strip().lower() 
        if user_input == 'y':
            use_proxy = True
        else:
            use_proxy = False
        
        write_json('config.json', {'use_proxy': use_proxy})

    if use_proxy:
        proxy = get_random_proxy()
        if proxy:
            print(Colorate.Horizontal(Colors.cyan_to_green, "/"))
            print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] Using proxy: {proxy}"))
            proxy_def = proxy
        else:
            print(Colorate.Horizontal(Colors.red_to_yellow, "/"))
            print(Colorate.Horizontal(Colors.red_to_yellow, " [X] No proxies available in proxies.json. Add some in the Proxy Manager."))
            use_proxy = False
    else:
        print(Colorate.Color(Colors.gray, "/"))
        print(Colorate.Color(Colors.gray, "[!] Proxies are Disabled."))
    
    return use_proxy

class Requests:
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    async def sender(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.headers) as response:
                return await response.text()

def convert_ipv4_to_ipv6(ip):
    ipv4_obj = ipaddress.IPv4Address(ip)
    ipv4_int = int(ipv4_obj)
    ipv4_hex = f'{ipv4_int:08x}'
    ipv4_hex_parts = [ipv4_hex[:4], ipv4_hex[4:]]
    ipv6_str = f'::ffff:{ipv4_hex_parts[0]}:{ipv4_hex_parts[1]}'
    
    return ipv6_str

async def check_ip_status(ip):
    try:
        response = ping(ip, count=1, timeout=2)
        return response.success()
    except Exception:
        return False

async def url(ip):
    default_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
    try:
        with open("useragents.txt", "r") as user_file:
            user_agents = user_file.read().split('\n')
    except FileNotFoundError:
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        print(Colorate.Horizontal(Colors.red_to_yellow,"[X] useragents.txt not found. Using default user agents."))
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        
        user_agents = default_user_agents

    url = f"http://ip-api.com/json/{ip}"
    headers = {"User-Agent": random.choice(user_agents)}

    try:
        response = await Requests(url, headers=headers).sender()
        return json.loads(response)
    except Exception as e:
        print(f"[X] An error occurred while fetching the data: {e}")
        return None
    
async def lookup(ip):
    colored_spinner(0.3, " ", Colors.cyan_to_green)
    read = await url(ip)
    if read and read.get('status') == 'success':
        output = (Colorate.Horizontal(Colors.cyan_to_green,f"""
[!] Query: {read.get('query', 'N/A')}
[!] Status: {read.get('status', 'N/A')}

[⛱] Location:
    [-] Country: {read.get('country', 'N/A')}
    [-] Country Code: {read.get('countryCode', 'N/A')}
    [-] Region: {read.get('region', 'N/A')}
    [-] Region Name: {read.get('regionName', 'N/A')}
    [-] City: {read.get('city', 'N/A')}
    [-] Zip: {read.get('zip', 'N/A')}

[✈] Coordinates:
    [-] Latitude: {read.get('lat', 'N/A')}
    [-] Longitude: {read.get('lon', 'N/A')}

[🗓] Timezone: {read.get('timezone', 'N/A')}

[🛠] Network:
    [-] ISP: {read.get('isp', 'N/A')}
    [-] Organization: {read.get('org', 'N/A')}
    [-] AS: {read.get('as', 'N/A')}

"""))
        return output, read.get('city', 'N/A')
    else:
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        return Colorate.Horizontal(Colors.red_to_yellow,"[X] Error retrieving data!"), None

async def scan_port(ip, port, proxy=None):
    try:
        if proxy:
            import socket
            import socks
            
            proxy_host, proxy_port = proxy.split(':')
            proxy_port = int(proxy_port)
            
            socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
            socket.socket = socks.socksocket
            
        reader, writer = await asyncio.open_connection(ip, port)
        print(Colorate.Horizontal(Colors.cyan_to_green,f"[!] Port {port} Responded!"))
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        writer.close()
        await writer.wait_closed()
        
        if proxy:
            socks.set_default_proxy()
            socket.socket = socks._orig_socket
            
        return port
    except:
        if proxy:
            socks.set_default_proxy()
            socket.socket = socks._orig_socket
        return None

async def port_scan(ip, is_online):
    if not is_online:
         print(" ")
         print(Colorate.Horizontal(Colors.red_to_yellow, "[X] This IP address seems to not be responding"))
         return
    
    config = read_json('config.json')
    use_proxy = config.get('use_proxy', False) if config else False
    
    proxy = None
    if use_proxy:
        proxy = get_working_proxy()
        if proxy:
            print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] Using proxy for port scan: {proxy}"))
        else:
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Continuing port scan without proxy."))
    
    open_ports = []
    tasks = []
    for port in range(1, 10000):
        tasks.append(scan_port(ip, port, proxy))
     
    colored_spinner(1.5, " ", Colors.cyan_to_green)
    results = await asyncio.gather(*tasks)

    for result in results:
        if result is not None:
            open_ports.append(result)

    print(" ")
    print(Colorate.Horizontal(Colors.cyan_to_green, f"[-] Open ports: {', '.join(map(str, open_ports)) if open_ports else 'No open ports found.'}"))

class IPQS:
    _cached_api_key = None
    _cache_time = 0
    _cache_duration = 3600
    
    @staticmethod
    async def _fetch_api_key():
        # Check cache first
        current_time = time.time()
        if IPQS._cached_api_key and (current_time - IPQS._cache_time) < IPQS._cache_duration:
            return IPQS._cached_api_key
            
        try:
            encrypted_parts = [
                "aHR0cHM6Ly9ldXBob25pb3VzLXNmb2dsaWF0ZWxsYS01OGU0YjUubmV0bGlmeS5hcHA=",
                "Ly5uZXRsaWZ5L2Z1bmN0aW9ucy9nZXQtYXBpLWtleQ=="
            ]

            api_key_url = base64.b64decode(encrypted_parts[0]).decode('utf-8') + base64.b64decode(encrypted_parts[1]).decode('utf-8')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_key_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        encoded_key = data.get("api_key")
                        
                        api_key = base64.b64decode(encoded_key).decode('utf-8')
                        
                        IPQS._cached_api_key = api_key
                        IPQS._cache_time = current_time
                        
                        return api_key
                    else:
                        print(Colorate.Horizontal(Colors.red_to_yellow, 
                              f"[X] Failed to fetch API key: HTTP {response.status}"))
                        return None
        except Exception as e:
            print(Colorate.Horizontal(Colors.red_to_yellow, 
                  f"[X] Error fetching API key: {e}"))
            return None

    @staticmethod
    async def check_vpn_proxy(ip, headers):
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        parameters = {
            'user_agent': headers['User-Agent'],
            'user_language': headers['Accept-Language'].split(',')[0],
            'strictness': 0,
            'allow_public_access_points': 'true',
            'lighter_penalties': 'false'
        }

        api_key = await IPQS._fetch_api_key()
        
        if not api_key:
            print(" ")
            print(Colorate.Horizontal(Colors.red_to_yellow,"[X] Could not retrieve API key. Cannot check VPN/Proxy status."))
            user_input = input(Colorate.Horizontal(Colors.cyan_to_green, 
                              "[?] Would you like to enter your own IPQS API key? (Y/N): ")).strip().lower()
            if user_input == 'y':
                api_key = input(Colorate.Horizontal(Colors.cyan_to_green, "[?] Enter your IPQS API key: ")).strip()
            else:
                return

        result = IPQS.payment_transaction_fraud_prev(api_key, ip, parameters)

        if 'success' in result and result['success'] == True:
            if result['proxy'] == True:
                print(" ")
                print(Colorate.Horizontal(Colors.cyan_to_green,"[-] IP address is associated with a VPN/Proxy."))
            elif result['tor'] == True:
                print(" ")
                print(Colorate.Horizontal(Colors.cyan_to_green,"[-] IP address is associated with Tor."))
            else:
                print(" ")
                print(Colorate.Horizontal(Colors.cyan_to_green,"[-] IP address is not associated with a VPN or proxy."))
        else:
            print(" ")
            print(Colorate.Horizontal(Colors.red_to_yellow,"[X] Error occurred while checking IP address."))

    @staticmethod
    def payment_transaction_fraud_prev(key, ip: str, vars: dict = {}) -> dict:
        # Encrypted API endpoint base
        encrypted_endpoint = "aHR0cHM6Ly93d3cuaXBxdWFsaXR5c2NvcmUuY29tL2FwaS9qc29uL2lwLw=="
        
        # Decrypt endpoint
        endpoint_base = base64.b64decode(encrypted_endpoint).decode('utf-8')
        url = f"{endpoint_base}{key}/{ip}"
        
        response = requests.get(url, params=vars)
        return json.loads(response.text)


async def change_ip():
    print(" ")
    new_ip = input(Colorate.Horizontal(Colors.cyan_to_green, "[?] Enter new IP address: "))
    if is_valid_ip(new_ip):
        ipv6 = convert_ipv4_to_ipv6(new_ip)
        return new_ip
    else:
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        print(" ")
        print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid IP address format."))
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        return None

def is_valid_ip(ip):
    colored_spinner(0.5, " ", Colors.cyan_to_green)
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip) is not None

async def ping_test(ip, is_online):
    if not is_online:
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        print(Colorate.Horizontal(Colors.red_to_yellow, "[X] This IP address seems to not be responding"))
        return
    
    config = read_json('config.json')
    use_proxy = config.get('use_proxy', False) if config else False
    
    if use_proxy:
        proxy = get_working_proxy()
        if proxy:
            print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] Using proxy for ping test: {proxy}"))
            try:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                start_time = time.time()
                response = requests.get(f"http://{ip}", proxies=proxies, timeout=5)
                end_time = time.time()
                rtt = (end_time - start_time) * 1000
                return f"Ping successful through proxy! Round-trip time: {rtt:.2f} ms"
            except Exception as e:
                colored_spinner(0.5, " ", Colors.cyan_to_green)
                print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] Ping through proxy failed: {e}"))
                colored_spinner(0.5, " ", Colors.cyan_to_green)
                print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Falling back to direct ping..."))
        else:
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Continuing ping test without proxy."))
    
    try:
        response = ping(ip, count=4, timeout=2)
        if response.success():
            colored_spinner(0.3, " ", Colors.cyan_to_green)
            return f"Ping successful! Round-trip time: {response.rtt_avg_ms:.2f} ms"
        else:
            colored_spinner(0.5, " ", Colors.cyan_to_green)
            return Colorate.Horizontal(Colors.red_to_yellow, "[X] Ping failed. No response.")
    except Exception as e:
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] An error occurred during ping test: {e}"))
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        return None

async def get_random_user_agent():
    try:
        with open("useragents.txt", "r") as user_file:
            user_agents = user_file.read().split('\n')
    except FileNotFoundError:
        print(Colorate.Horizontal(Colors.red_to_yellow,"[X] useragents.txt not found. Using default user agents."))
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        ]

    return random.choice(user_agents)

async def generate_map(ip):
    colored_spinner(0.7, " ", Colors.cyan_to_green)
    read = await url(ip)
    if read and read.get('status') == 'success':
        print(Colorate.Horizontal(Colors.cyan_to_green,f"""
[✈] Coordinates:
    [-] Latitude: {read.get('lat', 'N/A')}
    [-] Longitude: {read.get('lon', 'N/A')}   
 
        """))

        map_link = f"https://www.google.com/maps/place/{read.get('lat', 'N/A')},{read.get('lon', 'N/A')}"
        custom_map_link = f"https://cache.ip-api.com/{read.get('lat', 'N/A')},{read.get('lon', 'N/A')}"
        print(Colorate.Horizontal(Colors.cyan_to_green, f"[⛴] Google Maps Link: https://www.google.com/maps/place/{read.get('lat', 'N/A')},{read.get('lon', 'N/A')}"))
        print(" ")
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        mapstatus = input(Colorate.Horizontal(Colors.cyan_to_green,"[?] Open The Link? (Y/N): "))
        if mapstatus == "Y":
            print(" ")
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Opening Link..."))
            colored_spinner(3, " ", Colors.cyan_to_green)
            webbrowser.open(map_link, new=0, autoraise=True)
        elif mapstatus == "y":
            print(" ")
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Opening Link..."))
            colored_spinner(3, " ", Colors.cyan_to_green)
            webbrowser.open(map_link, new=0, autoraise=True)
        else:
            return None
        
    else:
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        print(" ")
        print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Error retrieving data!"))
        colored_spinner(0.5, " ", Colors.cyan_to_green)

async def ipapi_is_scan(ip):
    colored_spinner(0.5, " ", Colors.cyan_to_green)
    api_key = "22a98314c1c288bb"
    url = f"https://api.ipapi.is?q={ip}&key={api_key}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            output = (Colorate.Horizontal(Colors.cyan_to_green, f"""
[!] General Information: 
    [-] IP: {data.get('ip', 'N/A')}
    [-] RIR: {data.get('rir', 'N/A')}
    [-] Bogon: {data.get('is_bogon', 'N/A')}
    [-] Mobile: {data.get('is_mobile', 'N/A')}
    [-] Crawler: {data.get('is_crawler', 'N/A')}
    [-] Data Center: {data.get('is_datacenter', 'N/A')}
    [-] Tor: {data.get('is_tor', 'N/A')}
    [-] Proxy: {data.get('is_proxy', 'N/A')}
    [-] VPN: {data.get('is_vpn', 'N/A')}
    [-] Abuser: {data.get('is_abuser', 'N/A')}
     
[!] Datacenter Info:
    [-] Name: {data.get('datacenter', {}).get('datacenter', 'N/A')}
    [-] Domain: {data.get('datacenter', {}).get('domain', 'N/A')}
    [-] Network: {data.get('datacenter', {}).get('network', 'N/A')}
     
[!] Company Info:
    [-] Name: {data.get('company', {}).get('name', 'N/A')}
    [-] Abuser Score: {data.get('company', {}).get('abuser_score', 'N/A')}
    [-] Domain: {data.get('company', {}).get('domain', 'N/A')}
    [-] Type: {data.get('company', {}).get('type', 'N/A')}
    [-] Network: {data.get('company', {}).get('network', 'N/A')}
    [-] Whois: {data.get('company', {}).get('whois', 'N/A')}
     
[!] Abuse Info:
    [-] Name: {data.get('abuse', {}).get('name', 'N/A')}
    [-] Address: {data.get('abuse', {}).get('address', 'N/A')}
    [-] Email: {data.get('abuse', {}).get('email', 'N/A')}
    [-] Phone: {data.get('abuse', {}).get('phone', 'N/A')}
     
[!] ASN Info:
    [-] ASN: {data.get('asn', {}).get('asn', 'N/A')}
    [-] Abuser Score: {data.get('asn', {}).get('abuser_score', 'N/A')}
    [-] Route: {data.get('asn', {}).get('route', 'N/A')}
    [-] Description: {data.get('asn', {}).get('descr', 'N/A')}
    [-] Country: {data.get('asn', {}).get('country', 'N/A')}
    [-] Active: {data.get('asn', {}).get('active', 'N/A')}
    [-] Organization: {data.get('asn', {}).get('org', 'N/A')}
    [-] Domain: {data.get('asn', {}).get('domain', 'N/A')}
    [-] Abuse Email: {data.get('asn', {}).get('abuse', 'N/A')}
    [-] Type: {data.get('asn', {}).get('type', 'N/A')}
    [-] Created: {data.get('asn', {}).get('created', 'N/A')}
    [-] Updated: {data.get('asn', {}).get('updated', 'N/A')}
    [-] RIR: {data.get('asn', {}).get('rir', 'N/A')}
    [-] Whois: {data.get('asn', {}).get('whois', 'N/A')}
     
[!] Location Info:
    [-] Continent: {data.get('location', {}).get('continent', 'N/A')}
    [-] Country: {data.get('location', {}).get('country', 'N/A')}
    [-] Country Code: {data.get('location', {}).get('country_code', 'N/A')}
    [-] State: {data.get('location', {}).get('state', 'N/A')}
    [-] City: {data.get('location', {}).get('city', 'N/A')}
    [-] Latitude: {data.get('location', {}).get('latitude', 'N/A')}
    [-] Longitude: {data.get('location', {}).get('longitude', 'N/A')}
    [-] Zip: {data.get('location', {}).get('zip', 'N/A')}
    [-] Timezone: {data.get('location', {}).get('timezone', 'N/A')}
    [-] Local Time: {data.get('location', {}).get('local_time', 'N/A')}
    [-] Local Time Unix: {data.get('location', {}).get('local_time_unix', 'N/A')}
    [-] DST: {data.get('location', {}).get('is_dst', 'N/A')}
            """))
            return output
        else:
            return Colorate.Horizontal(Colors.red_to_yellow, f"[X] Error fetching data from ipapi.is: {response.status_code}")
    except Exception as e:
        return Colorate.Horizontal(Colors.red_to_yellow, f"[X] An error occurred while fetching data: {e}")

async def manage_proxies():
    def validate_proxy(proxy):
        parts = proxy.split(":")
        return len(parts) == 2 and parts[0].count('.') == 3 and parts[1].isdigit()

    def read_json(file_name):
        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] {file_name} not found."))
            return []
        except json.JSONDecodeError as e:
            print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] Error decoding JSON from {file_name}: {e}"))
            return []

    def write_json(file_name, data):
        try:
            with open(file_name, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(Colorate.Horizontal(Colors.red_to_yellow, f"[X] Error writing to {file_name}: {e}"))

    async def add_proxy():
        proxies = read_json('proxies.json') or []
        print(Colorate.Horizontal(Colors.green_to_cyan, "[!] Current proxies list loaded."))
        while True:
            proxy = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter proxy (IP:Port) or type 'done' to finish: ")).strip()
            if proxy.lower() == 'done':
                break
            if validate_proxy(proxy):
                proxies.append(proxy)
                print(Colorate.Horizontal(Colors.green_to_cyan, "[!] Proxy added!"))
                print(" ")
            else:
                print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid proxy format. Please try again."))
        write_json('proxies.json', proxies)

    async def toggle_proxy_usage():
        config = read_json('config.json') or {}
        use_proxy = config.get('use_proxy', False)
        config['use_proxy'] = not use_proxy
        write_json('config.json', config)
        status = "enabled" if config['use_proxy'] else "disabled"
        print(" ")
        print(Colorate.Horizontal(Colors.green_to_cyan, f"[!] Proxy usage has been changed to '{status}'"))
        colored_spinner(3, " ", Colors.cyan_to_green)

    async def open_json_file(file_name):
        try:
            os.system(f'notepad "{file_name}"' if os.name == 'nt' else f'open "{file_name}"')
        except Exception as e:
            print(f"Debug: Failed to open {file_name}: {e}")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Colorate.Horizontal(Colors.cyan_to_green,
            rf'''
             __     __        ____      ___      __ 
            / /  __/ /_______/ __ \____<  /___  / /_
  ---  __  / / |/_/ //_/ ___/ / / / ___/ / __ \/ __/  --- 
      / /_/ />  </ ,< (__  ) /_/ (__  ) / / / / /_  
      \____/_/|_/_/|_/____/\____/____/_/_/ /_/\__/     #jxksdev
            '''
        ))
        print(Colorate.Horizontal(Colors.cyan_to_green,
            rf'''        /┌────────────────────────────────┐\    
         ┼─ 1. Add Proxies                │ ADI: {REPO_OWNER} - {REPO_NAME} - {CURRENT_VERSION}
         ┼─ 2. Change Proxy Usage         │ [?] = Input, [X] = Error, [!] = Status, [-] = Result
         ┼─ 3. Open Proxies JSON File     │ 
         ┼─ 4. Go Back                    │ Window: Proxy Management -/ (jxks0s1nt/proxy)
        \└────────────────────────────────┘/
         └─► Select A Proxy Management Option.
            
   ┌───({current_user}@jxks0s1nt/proxy)─[~]'''
        ))

        option = input(Colorate.Horizontal(Colors.cyan_to_green, "   └──$ ")).strip()
        if option == '1':
            colored_spinner(0.5, " ", Colors.cyan_to_green)
            await add_proxy()
        elif option == '2':
            colored_spinner(0.5, " ", Colors.cyan_to_green)
            await toggle_proxy_usage()
        elif option == '3':
            colored_spinner(0.5, " ", Colors.cyan_to_green)
            await open_json_file('proxies.json')
        elif option == '4':
            return
        else:
            print(" ")
            print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid option."))
            colored_spinner(1, " ", Colors.cyan_to_green)

async def extensive_scan(ip):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Colorate.Horizontal(Colors.cyan_to_green,
        rf'''
            __     __        ____      ___      __ 
           / /  __/ /_______/ __ \____<  /___  / /_
 ---  __  / / |/_/ //_/ ___/ / / / ___/ / __ \/ __/  ---
     / /_/ />  </ ,< (__  ) /_/ (__  ) / / / / /_  
     \____/_/|_/_/|_/____/\____/____/_/_/ /_/\__/     #jxksdev
    '''
    ))
    print(Colorate.Horizontal(Colors.cyan_to_green,
        rf'''       /┌───────────────────────────────┐\          
        ┼─ 1. Quick Scan (ip-api.com)   │ ADI: {REPO_OWNER} - {REPO_NAME} - {CURRENT_VERSION}
        ┼─ 2. Extensive Scan (ipapi.is) │ [?] = Input, [X] = Error, [!] = Status, [-] = Result
        ┼─ 3. Go Back                   │ Window: IP Scan -/ (jxks0s1nt/scan)
       \└───────────────────────────────┘/
        └─► Select An IP Scan Option.

   ┌───({current_user}@jxks0s1nt/scan)─[~]''' 
    ))

    option = input(Colorate.Horizontal(Colors.cyan_to_green, "   └──$ "))
    if option == '1':
        result, city = await lookup(ip)
        print(result)
    elif option == '2':
        result = await ipapi_is_scan(ip)
        print(result)
    elif option == '3':
        return
    else:
        print(" ")
        print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid option."))
        colored_spinner(0.5, " ", Colors.cyan_to_green)
        await extensive_scan(ip)

async def main():
    ip = None
    is_online = False
    while not ip:
        print(" ")
        print(Colorate.Horizontal(Colors.cyan_to_green, "            __     __        ____      ___      __            "))
        time.sleep(0.1)
        print(Colorate.Horizontal(Colors.cyan_to_green, "           / /  __/ /_______/ __ \____<  /___  / /_           "))
        time.sleep(0.1)
        print(Colorate.Horizontal(Colors.cyan_to_green, " ---  __  / / |/_/ //_/ ___/ / / / ___/ / __ \/ __/  ---      "))
        time.sleep(0.1)
        print(Colorate.Horizontal(Colors.cyan_to_green, "     / /_/ />  </ ,< (__  ) /_/ (__  ) / / / / /_             "))
        time.sleep(0.1)
        print(Colorate.Horizontal(Colors.cyan_to_green, "     \____/_/|_/_/|_/____/\____/____/_/_/ /_/\__/     #jxksdev"))
        print(" ")
        time.sleep(0.1)
        print(Colorate.Horizontal(Colors.cyan_to_green, " [?] Enter a valid IPv4 Adress."))
        print(" ")
        print(Colorate.Horizontal(Colors.cyan_to_green, f"   ┌───({current_user}@jxks0s1nt/setup)─[~]"))
        time.sleep(0.1)

        ip_input = input(Colorate.Horizontal(Colors.cyan_to_green, "   └──$ "))
        if is_valid_ip(ip_input):
            ip = ip_input
            ipv6 = convert_ipv4_to_ipv6(ip)
            is_online = await check_ip_status(ip)
        else:
            colored_spinner(0.2, " ", Colors.cyan_to_green)
            print(" ")
            print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid IP address format. Please enter a valid IP address."))
            colored_spinner(1, " ", Colors.cyan_to_green)
            os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        ip_state = "[ONLINE]" if is_online else "[OFFLINE]"
        config = read_json('config.json')
        use_proxy = config.get('use_proxy', False) if config else False
        print(Colorate.Horizontal(Colors.cyan_to_green,
            rf'''
            __     __        ____      ___      __ 
           / /  __/ /_______/ __ \____<  /___  / /_
 ---  __  / / |/_/ //_/ ___/ / / / ___/ / __ \/ __/  ---
     / /_/ />  </ ,< (__  ) /_/ (__  ) / / / / /_  
     \____/_/|_/_/|_/____/\____/____/_/_/ /_/\__/     #jxksdev
     '''))
        print(Colorate.Horizontal(Colors.cyan_to_green,
            rf'''       /┌────────────────────────────┐\         
        ┼─ 1. IP Scan                │ Github: https://github.com/Jxkss/jxks0s1nt
        ┼─ 2. Port Scan              │ Profile: https://jxks.dev 
        ┼─ 3. Check for VPN/Proxy    │ Contact: 'leywx' on Discord
        ┼─ 4. Ping Test              │
        ┼─ 5. Generate Map           │ [?] = Input, [X] = Error, [!] = Status, [-] = Result
        ┼─ 6. Change IP Address      │ ADI: {REPO_OWNER} - {REPO_NAME} - {CURRENT_VERSION}
        ┼─ 7. Manage Proxies         │ Proxy Status: {use_proxy}
        ┼─ 8. Update jxks0s1nt       │ 
        ┼─ 9. Exit jxks0s1nt         │ Window: Main -/ (jxks0s1nt/)
       \└────────────────────────────┘/
        └─► Using {ip} ({ipv6}) - {ip_state}
            
   ┌───({current_user}@jxks0s1nt/)─[~]'''))
        task = input(Colorate.Horizontal(Colors.cyan_to_green, "   └──$ "))
        
        headers = {
            'User-Agent': await get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9'
        }

        if task == '1':
            await extensive_scan(ip)
        elif task == '2':
            print(" ")
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Loading Results, It May Take a Few Seconds..."))
            print(" ")
            await port_scan(ip, is_online)
        elif task == '3':
            await IPQS.check_vpn_proxy(ip, headers)
        elif task == '6':
            new_ip = await change_ip()
            if new_ip:
                ip = new_ip
                ipv6 = convert_ipv4_to_ipv6(ip)
                is_online = await check_ip_status(ip)
                colored_spinner(0.5, " ", Colors.cyan_to_green)
                print(" ")
                print(Colorate.Horizontal(Colors.cyan_to_green, f"[!] IP address changed to {ip}"))
            else:
                colored_spinner(0.5, " ", Colors.cyan_to_green)
                print(" ")
                print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Failed to change IP address."))
                colored_spinner(0.5, " ", Colors.cyan_to_green)
        elif task == '4':
            print(' ')
            result = await ping_test(ip, is_online)
            if result:
                print(Colorate.Horizontal(Colors.cyan_to_green, f"[-] Ping Test Results: {result}"))
        elif task == '5':
            await generate_map(ip)
        elif task == '7':
            await manage_proxies()
        elif task == '8':
            colored_spinner(0.5, " ", Colors.cyan_to_green)
            webbrowser.open('https://github.com/Jxkss/jxks0s1nt')
            print(" ")
            print(Colorate.Horizontal(Colors.cyan_to_green, "[!] Opened Official Github Page"))
            colored_spinner(0.5, " ", Colors.cyan_to_green)
        elif task == '9':
            print(" ")
            print(Colorate.Horizontal(Colors.cyan_to_green, "[<3] Thank You For Using jxks0s1nt"))
            print(" ")
            colored_spinner(1, " ", Colors.cyan_to_green)
            sys.exit(0)
        else:
            colored_spinner(0.5, " ", Colors.cyan_to_green)
            print(" ")
            print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid option."))
            colored_spinner(0.5, " ", Colors.cyan_to_green)

        print(" ")
        input(Colorate.Horizontal(Colors.cyan_to_green, "[?] Press Enter to continue..."))

if __name__ == "__main__":
    print(" ")
    use_proxy = setup_proxy()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Colorate.Horizontal(Colors.red_to_yellow, "\n[X] jxks0s1nt has been interrupted. Exiting..."))
        colored_spinner(2, " ", Colors.cyan_to_green)
        sys.exit(0)
