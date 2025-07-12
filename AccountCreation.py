# AccountCreation.py

import json
import os
import re
import sys
import time
import html
import uuid
import random
from typing import Optional
from queue import Queue, Empty  # <--- MODIFIED: Added Empty for timeout exception
import threading

from github import Github, UnknownObjectException
from github.GithubException import GithubException

from curl_cffi import requests
from mailtm import MailTmApi
from tqdm import tqdm
import proxy_scraper_checker

# --- CONFIGURATION ---
PROXY_SOURCES_FILE = "proxy_sources.txt"
SOCKS4_PROXY_SOURCES = []
SOCKS5_PROXY_SOURCES = []
NUM_THREADS = 50  # Number of worker threads for account creation

DEEVID_SIGNUP_URL = "https://sp.deevid.ai/auth/v1/signup?redirect_to=https%3A%2F%2Fdeevid.ai"
DEEVID_LOGIN_URL = "https://sp.deevid.ai/auth/v1/token?grant_type=password"
DEEVID_ACCOUNT_INFO_URL = "https://api.deevid.ai/account/info"
DEEVID_CREDIT_CHECK_URL = "https://api.deevid.ai/subscription/plan"
EMAIL_CHECK_RETRIES = 5
EMAIL_CHECK_INTERVAL = 5
POST_VERIFICATION_DELAY = 0.5
REQUEST_TIMEOUT = 10  # Increased timeout for more reliability with various proxies

# --- GITHUB CONFIGURATION ---
# The token is securely read from an environment variable set by GitHub Actions
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "BoghosDavtyan/Fives-day"  # e.g., "johndoe/my-accounts-list"
GITHUB_FILE_PATH = "accounts.txt"  # The file in the repo to append accounts to

SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhYmFzZSIsICJpYXQiOiAxNzM0OTY5NjAwLAogICJleHAiOiAxODkyNzM2MDAwCn0.4NnK23LGYvKPGuKI5rwQn2KbLMzzdE4jXpHwbGCqPqY"

BASE_AUTH_HEADERS = {
    "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}", "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://deevid.ai", "Referer": "https://deevid.ai/",
    "X-Client-Info": "supabase-ssr/0.3.0", "x-supabase-api-version": "2024-01-01",
}


def get_api_headers(access_token, visitor_id, device_id):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Origin": "https://deevid.ai",
        "Referer": "https://deevid.ai/",
        "x-device": "DESKTOP",
        "x-device-id": device_id,
        "x-lang": "en",
        "x-os": "WINDOWS",
        "x-platform": "WEB",
        "x-visitor-id": visitor_id
    }


def add_to_github_list(email: str, password: str):
    if not GITHUB_TOKEN:
        tqdm.write("[GITHUB ERROR] GitHub token is not configured. Cannot save account.")
        return

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
    except Exception as e:
        tqdm.write(f"[GITHUB ERROR] Could not connect to GitHub or get repo '{GITHUB_REPO}'. Error: {e}")
        return

    new_credential = f"{email}:{password}\n"
    commit_message = f"Add account {email}"

    for i in range(5):
        try:
            try:
                file_contents = repo.get_contents(GITHUB_FILE_PATH)
                sha = file_contents.sha
                current_content = file_contents.decoded_content.decode('utf-8')
                new_content = current_content + new_credential
                repo.update_file(path=GITHUB_FILE_PATH, message=commit_message, content=new_content, sha=sha)
                tqdm.write(f"[GITHUB SUCCESS] Appended {email} to {GITHUB_REPO}/{GITHUB_FILE_PATH}")
                return

            except UnknownObjectException:
                tqdm.write(f"[GITHUB INFO] File '{GITHUB_FILE_PATH}' not found. Creating it.")
                repo.create_file(path=GITHUB_FILE_PATH, message=f"Create accounts file and add {email}",
                                 content=new_credential)
                tqdm.write(f"[GITHUB SUCCESS] Created file and added {email} to {GITHUB_REPO}/{GITHUB_FILE_PATH}")
                return

        except GithubException as e:
            if e.status == 409:
                tqdm.write(f"[GITHUB WARN] Conflict detected (409). Retrying... (Attempt {i + 1}/5)")
                time.sleep(random.uniform(1, 3))
                continue
            else:
                tqdm.write(f"[GITHUB ERROR] An unexpected GitHub error occurred: {e.status} {e.data}")
                return
        except Exception as e:
            tqdm.write(f"[GITHUB ERROR] A general error occurred: {e}")
            return

    tqdm.write("[GITHUB FATAL] Failed to update GitHub file after multiple retries. Giving up on this account.")


def load_sources_from_file(filename: str) -> list[str]:
    if not os.path.exists(filename):
        print(f"[WARNING] Source file '{filename}' not found. No sources will be loaded.")
        return []
    try:
        with open(filename, 'r') as f:
            sources = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return sources
    except Exception as e:
        print(f"[ERROR] Could not read source file '{filename}': {e}")
        return []


# Removed progress_monitor function from here as it's now internal to proxy_scraper_checker

def find_verification_link(email_body_str: str) -> str | None:
    try:
        body_decoded_html = html.unescape(email_body_str)
        match = re.search(r'<a href="([^"]+)">Verify Your Email Address</a>', body_decoded_html)
        if match:
            return match.group(1)
    except Exception:
        # Suppress printing for cleaner output
        pass
    return None


def attempt_account_creation_with_proxy(proxy: str) -> str:
    """
    Tries to create an account using a given proxy.
    Returns a status string: 'SUCCESS_BALANCE', 'SUCCESS_ZERO', or 'FAILURE'.
    """
    try:
        with requests.Session() as s:
            s.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            s.timeout = REQUEST_TIMEOUT
            s.impersonate = "chrome120"

            # 1. Email Generation
            try:
                mail_api = MailTmApi(proxy=proxy, timeout=REQUEST_TIMEOUT)
                domain = mail_api.get_random_avaible_domain()
                if not domain: return "FAILURE"
                account = mail_api.get_random_mail(domain)
                if not account: return "FAILURE"
                email, password, mail_token = account["email"], account["password"], account["token"]
            except Exception:
                return "FAILURE"

            # 2. Sign-up
            try:
                signup_payload = {"email": email, "password": password}
                response = s.post(DEEVID_SIGNUP_URL, headers=BASE_AUTH_HEADERS, json=signup_payload)
                if response.status_code != 200:
                    return "FAILURE"
            except requests.errors.RequestsError:
                return "FAILURE"

            # 3. Email Verification
            verification_link = None
            for _ in range(EMAIL_CHECK_RETRIES):
                try:
                    emails = mail_api.get_emails(mail_token)
                    if emails:
                        for email_header in emails:
                            if "support@service.deevid.ai" in email_header.get("from", {}).get("address", ""):
                                email_id = email_header["id"]
                                email_body_response = mail_api.session.get(f"https://api.mail.gw/messages/{email_id}")
                                email_html = email_body_response.json().get('html', [''])[0]
                                verification_link = find_verification_link(email_html)
                                break
                except requests.errors.RequestsError:
                    return "FAILURE"
                if verification_link:
                    break
                time.sleep(EMAIL_CHECK_INTERVAL)

            if not verification_link:
                return "FAILURE"

            # 4. Visit verification link
            try:
                verify_response = s.get(verification_link, allow_redirects=False)
                if not (300 <= verify_response.status_code < 400):
                    return "FAILURE"
                time.sleep(POST_VERIFICATION_DELAY)
            except requests.errors.RequestsError:
                return "FAILURE"

            # 5. Login and Check Balance
            try:
                login_payload = {"email": email, "password": password}
                login_response = s.post(DEEVID_LOGIN_URL, headers=BASE_AUTH_HEADERS, json=login_payload)
                if login_response.status_code != 200:
                    return "FAILURE"

                access_token = login_response.json().get("access_token")
                if not access_token:
                    return "FAILURE"

                visitor_id = str(uuid.uuid4())
                device_id = str(random.randint(10 ** 9, 10 ** 10 - 1))
                api_headers = get_api_headers(access_token, visitor_id, device_id)
                s.get(DEEVID_ACCOUNT_INFO_URL, headers=api_headers)

                credit_response = s.get(DEEVID_CREDIT_CHECK_URL, headers=api_headers)
                if credit_response.status_code != 200:
                    return "FAILURE"

                credit_data = credit_response.json()
                credit_balance = credit_data.get("data", {}).get("data", {}).get("message_quota", {}).get("quota_count")

                if credit_balance is not None:
                    if credit_balance > 0:
                        add_to_github_list(email, password)
                        return "SUCCESS_BALANCE"
                    else:
                        return "SUCCESS_ZERO"
                else:
                    return "FAILURE"

            except requests.errors.RequestsError:
                return "FAILURE"
    except Exception:
        return "FAILURE"


def worker(proxy_q: Queue, result_q: Queue):
    """Worker thread function to process proxies from the queue."""
    while True:
        proxy = proxy_q.get()
        try:
            status = attempt_account_creation_with_proxy(proxy)
            result_q.put(status)
        except Exception:
            result_q.put("FAILURE")
        finally:
            proxy_q.task_done()


def main():
    """
    Main function to run a single cycle of proxy scraping and account creation.
    This is designed to be run as a scheduled job (e.g., via GitHub Actions).
    """
    if not GITHUB_TOKEN:
        print("[FATAL] GitHub token is not configured. Set the GITHUB_TOKEN environment variable.")
        sys.exit(1)
    if not GITHUB_REPO:
        print("[FATAL] GitHub repository is not configured. Set the GITHUB_REPO environment variable.")
        sys.exit(1)

    proxy_queue = Queue()
    results_queue = Queue()

    print(f"[INFO] Starting {NUM_THREADS} worker threads...")
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=worker, args=(proxy_queue, results_queue), daemon=True)
        thread.start()

    print(f"\n{'#' * 25} Starting Proxy Scraping Cycle {'#' * 25}")

    http_proxy_sources = load_sources_from_file(PROXY_SOURCES_FILE)
    if not http_proxy_sources:
        print("[FATAL] No proxy sources found. Please create 'proxy_sources.txt'.")
        return  # Exit the script

    print("[INFO] Scraping and checking proxies from provided online sources...")
    # The proxy_scraper_checker library now handles its own progress display.
    proxies = proxy_scraper_checker.get_proxies(
        http_urls=http_proxy_sources,
        socks4_urls=SOCKS4_PROXY_SOURCES,
        socks5_urls=SOCKS5_PROXY_SOURCES
        # No progress_queue argument here for proxy_scraper_checker v0.1.0 as it's not needed/expected
    )

    if not proxies:
        print("\n[WARN] The proxy scraper returned no working proxies for this run.")
        return  # Exit the script

    num_proxies = len(proxies)
    print(f"\n[SUCCESS] Loaded {num_proxies} working proxies for this run.")
    print(f"\n{'#' * 25} Starting Account Creation Attempts {'#' * 25}")

    stats = {"bal": 0, "zero": 0, "fail": 0}

    random.shuffle(proxies)
    for proxy in proxies:
        proxy_queue.put(proxy)

    # MODIFIED: Added timeout for results_queue.get() to prevent main thread from hanging
    with tqdm(total=num_proxies, desc="Creating Accounts", unit="proxy") as creation_pbar:
        for i in range(num_proxies):
            try:
                # Wait for a result, but for a maximum of 60 seconds.
                # If a worker thread hangs, we don't want to block indefinitely.
                result = results_queue.get(timeout=60) 
            except Empty:
                # If no result appears after the timeout, assume the worker is stuck/failed.
                # Log a warning and count it as a failure, then continue processing.
                tqdm.write(f"[WARN] Result collection timed out for proxy {i+1}. Assuming failure for this attempt.")
                result = "FAILURE" # Assign a failure status to account for the hung worker
            
            if result == "SUCCESS_BALANCE":
                stats["bal"] += 1
            elif result == "SUCCESS_ZERO":
                stats["zero"] += 1
            else:  # FAILURE
                stats["fail"] += 1

            creation_pbar.set_postfix(stats, refresh=True) # Ensure progress bar updates
            creation_pbar.update(1)

    print("\n[INFO] This workflow run has completed.")


if __name__ == "__main__":
    main()
