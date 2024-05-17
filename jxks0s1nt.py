import re
import os
import sys
import json
import time
import random
import asyncio
import aiohttp
import requests
from pystyle import Colors, Colorate

os.system('title jxks0s1nt - Made With Love By Jxks')

class Requests:
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    async def sender(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.headers) as response:
                return await response.text()

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
        print(Colorate.Horizontal(Colors.red_to_yellow,"[X] useragents.txt not found. Using default user agents."))
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

[⛴] Google Maps Link: https://www.google.com/maps/place/{read.get('lat', 'N/A')},{read.get('lon', 'N/A')}
"""))
        return output, read.get('city', 'N/A')
    else:
        return Colorate.Horizontal(Colors.red_to_yellow,"[X] Error retrieving data!"), None

async def scan_port(ip, port):
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        print(Colorate.Horizontal(Colors.cyan_to_green,f"[!] Port {port} Responded!"))
        writer.close()
        await writer.wait_closed()
        return port
    except:
        return None

async def port_scan(ip):
    open_ports = []
    tasks = []
    for port in range(1, 10000):
        tasks.append(scan_port(ip, port))

    results = await asyncio.gather(*tasks)

    for result in results:
        if result is not None:
            open_ports.append(result)

    print(" ")
    print(Colorate.Horizontal(Colors.cyan_to_green, f"[-] Open ports: {', '.join(map(str, open_ports)) if open_ports else Colorate.Horizontal(Colors.cyan_to_green,'No open ports found')}"))



class IPQS:
    key = "B95ZfBY2JF1HzSmgGjGVm3v2Hg1TAVGw"

    @staticmethod
    async def check_vpn_proxy(ip, headers):
        parameters = {
            'user_agent': headers['User-Agent'],
            'user_language': headers['Accept-Language'].split(',')[0],
            'strictness': 0,
            'allow_public_access_points': 'true',
            'lighter_penalties': 'false'
        }

        result = IPQS.payment_transaction_fraud_prev(IPQS.key, ip, parameters)

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
        url = f"https://www.ipqualityscore.com/api/json/ip/{key}/{ip}"
        response = requests.get(url, params=vars)
        return json.loads(response.text)

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

def is_valid_ip(ip):
    pattern = re.compile(
        r"^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$")
    return bool(pattern.match(ip))

async def main():
    while True:
        print(Colorate.Horizontal(Colors.cyan_to_green,
        rf'''
     __        __           _______          ____        __
    |__|__  __|  | __  _____\   _  \   _____/_   | _____/  |_
    |  \  \/  /  |/ / /  ___/  /_\  \ /  ___/|   |/    \   __\
    |  |>    <|    <  \___ \\  \_/   \\___ \ |   |   |  \  |
/\__|  /__/\_ \__|_ \/____  >\_____  /____  >|___|___|  /__|
\______|     \/    \/     \/       \/     \/          \/     #Jxksdev | DONT SKID

     '''))
        ip = input(Colorate.Horizontal(Colors.cyan_to_green,"[?] IP address: "))
        if not is_valid_ip(ip):
            print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid IP address format. Please try again."))
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        break

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Colorate.Horizontal(Colors.cyan_to_green,
            rf'''
     __        __           _______          ____        __
    |__|__  __|  | __  _____\   _  \   _____/_   | _____/  |_
    |  \  \/  /  |/ / /  ___/  /_\  \ /  ___/|   |/    \   __\
    |  |>    <|    <  \___ \\  \_/   \\___ \ |   |   |  \  |
/\__|  /__/\_ \__|_ \/____  >\_____  /____  >|___|___|  /__|
\______|     \/    \/     \/       \/     \/          \/     #Jxksdev | DONT SKID
     '''))
        print(Colorate.Horizontal(Colors.cyan_to_green,
            rf'''
┌────────────────────────────┐
│        -jxks0s1nt-         │ Github: https://github.com/Jxkss
├────────────────────────────┤ Profile: https://jxks.dev            
├─ 1. Extensive Scan         │ Contact: 'jxksdev' on Discord
├─ 2. Port scan              │
├─ 3. Check for VPN/Proxy    │ [?] = Input, [X] = Error, [!] = Status, [-] = Result
├─ 4. Exit jxks0s1nt         │
└┬───────────────────────────┘ 
 └─► Using {ip}
                            '''))
        task = input(Colorate.Horizontal(Colors.cyan_to_green,"[?] Option: "))
        
        headers = {
            'User-Agent': await get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9'
        }

        if task == '1':
            output, _ = await lookup(ip)
            print(output)
        elif task == '2':
            print(" ")
            await port_scan(ip)
        elif task == '3':
            await IPQS.check_vpn_proxy(ip, headers)
        elif task == '4':
            sys.exit(0)
        else:
            print(Colorate.Horizontal(Colors.red_to_yellow, "[X] Invalid option."))

        print(" ")
        input(Colorate.Horizontal(Colors.cyan_to_green, "[?] Press Enter to continue..."))

if __name__ == "__main__":
    asyncio.run(main())
