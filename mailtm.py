# mailtm.py

import json
import random
import secrets
import time
from typing import Optional

import requests


class MailTmApi:
    def __init__(self, proxy: Optional[str] = None, timeout: int = 25):
        self.session = requests.session()
        self.timeout = timeout
        self.session.headers = {
            'authority': 'api.mail.gw',
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://mail.tm',
            'pragma': 'no-cache',
            'referer': 'https://mail.tm/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

        # Proxy handling: Prioritize passed proxy, then fall back to file.
        self.proxy = proxy
        if self.proxy:
            self.session.proxies = {'http': 'http://' + self.proxy, 'https': 'http://' + self.proxy}
        else:
            try:
                with open("proxy.txt", "r") as f:
                    proxies = [line.strip() for line in f if line.strip()]
                    if proxies:
                        self.proxy = random.choice(proxies)
                        self.session.proxies = {'http': 'http://' + self.proxy, 'https': 'http://' + self.proxy}
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"[MailTmApi ERROR] Error loading proxy from proxy.txt: {e}. Not using a proxy.")

    def get_random_avaible_domain(self):
        """Fetches a random available domain from the Mail.tm API."""
        try:
            response = self.session.get('https://api.mail.gw/domains', timeout=self.timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            domains = response.json().get("hydra:member", [])
            if domains:
                return random.choice(domains)["domain"]
            else:
                print("Error: No domains found in the API response.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching domains: {e}")
            return None

    def get_random_mail(self, domain):
        """Creates a new random email account for the given domain."""
        if not domain:
            print("Error: A domain must be provided to create a mail account.")
            return None

        nickname = secrets.token_hex(5)
        password = secrets.token_hex(7)

        json_data = {
            'address': f'{nickname}@{domain}',
            'password': password,
        }

        try:
            response_account = self.session.post('https://api.mail.gw/accounts', json=json_data, timeout=self.timeout)
            response_account.raise_for_status()

            response_token = self.session.post('https://api.mail.gw/token', json=json_data, timeout=self.timeout)
            response_token.raise_for_status()

            token_data = response_token.json()
            if "token" not in token_data:
                print("Error: 'token' not found in token response.")
                return None

            return {
                "email": f'{nickname}@{domain}',
                "password": password,
                "token": token_data["token"]
            }
        except requests.exceptions.RequestException as e:
            print(f"Error creating mail or getting token: {e}")
            if e.response is not None:
                print(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    def get_emails(self, mail_token):
        """Fetches emails for the account associated with the given token."""
        if not mail_token:
            print("Error: Mail token must be provided to fetch emails.")
            return []

        self.session.headers['authorization'] = f'Bearer {mail_token}'
        try:
            response = self.session.get('https://api.mail.gw/messages', timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("hydra:member", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching emails: {e}")
            if e.response is not None:
                print(f"Response content: {e.response.text}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return []