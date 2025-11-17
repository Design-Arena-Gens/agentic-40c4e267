#!/usr/bin/env python3
"""
HTTP-based scraper using curl_cffi for Chrome impersonation
This approach avoids browser installation issues
"""
import time
import random
import sys
import threading
from queue import Queue
import json

# Proxy configuration
PROXY_CONFIG = {
    "username": "c147d949a38ca89c4c3a__cr.au,gb,us",
    "password": "b7351118825adfbd",
    "server": "gw.dataimpulse.com",
    "port": "823"
}

PROXY_URL = f"http://{PROXY_CONFIG['username']}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}"
TARGET_URL = "https://www.realestate.com.au/vic/st-kilda-3182/"

SAMPLE_URLS = [
    "https://www.realestate.com.au/",
    "https://www.realestate.com.au/buy",
    "https://www.realestate.com.au/rent",
    "https://www.realestate.com.au/vic/melbourne-3000/",
    "https://www.realestate.com.au/vic/richmond-3121/",
    "https://www.realestate.com.au/vic/south-yarra-3141/",
    "https://www.realestate.com.au/vic/prahran-3181/",
    "https://www.realestate.com.au/vic/fitzroy-3065/",
    "https://www.realestate.com.au/vic/carlton-3053/",
    "https://www.realestate.com.au/vic/collingwood-3066/",
    "https://www.realestate.com.au/nsw/sydney-2000/",
    "https://www.realestate.com.au/qld/brisbane-4000/",
    "https://www.realestate.com.au/wa/perth-6000/",
    "https://www.realestate.com.au/sa/adelaide-5000/",
    "https://www.realestate.com.au/vic/brunswick-3056/",
]


def scrape_with_curl_cffi(url: str, session_id: int, attempt: int = 1) -> dict:
    """Scrape using curl_cffi for Chrome impersonation"""
    try:
        from curl_cffi import requests as curl_requests

        print(f"[Session {session_id}] Attempt {attempt}: Using curl_cffi for {url}")

        # Create session with Chrome impersonation
        session = curl_requests.Session()

        # Random Chrome version for impersonation
        impersonate_versions = ['chrome110', 'chrome116', 'chrome120']
        impersonate = random.choice(impersonate_versions)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-AU,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        # Random delay to simulate human behavior
        time.sleep(random.uniform(2, 5))

        # Make request with Chrome impersonation
        response = session.get(
            url,
            proxies={'http': PROXY_URL, 'https': PROXY_URL},
            headers=headers,
            impersonate=impersonate,
            timeout=60,
            allow_redirects=True,
            verify=False
        )

        print(f"[Session {session_id}] Status code: {response.status_code}")
        print(f"[Session {session_id}] Content length: {len(response.text)} chars")

        # Check response
        if response.status_code == 429:
            print(f"[Session {session_id}] Rate limited (429)")
            return {"success": False, "error": "Rate limited (429)", "status": 429}

        if response.status_code != 200:
            print(f"[Session {session_id}] Non-200 status: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}", "status": response.status_code}

        content = response.text
        content_length = len(content)

        # Validate content
        if content_length < 1000:
            print(f"[Session {session_id}] Warning: Content too short")
            return {"success": False, "error": "Content too short", "length": content_length}

        if "429" in content or "Too Many Requests" in content.lower():
            print(f"[Session {session_id}] Rate limited in content")
            return {"success": False, "error": "Rate limited in content"}

        # Check for blocking indicators
        if "access denied" in content.lower() or "blocked" in content.lower():
            print(f"[Session {session_id}] Access denied/blocked")
            return {"success": False, "error": "Access denied", "length": content_length}

        # Extract title
        title = ""
        if "<title>" in content:
            title_start = content.find("<title>") + 7
            title_end = content.find("</title>", title_start)
            if title_end > title_start:
                title = content[title_start:title_end]

        print(f"[Session {session_id}] Title: {title}")

        # Validate target URL content
        if url == TARGET_URL:
            if "st kilda" in content.lower() or "3182" in content:
                print(f"[Session {session_id}] ✓ Successfully scraped target!")

                # Save content
                content_file = f"/tmp/scraped_content_cffi_session{session_id}_attempt{attempt}.html"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[Session {session_id}] Content saved: {content_file}")

                # Show snippet
                if 'st kilda' in content.lower():
                    snippet_start = content.lower().find('st kilda')
                    snippet = content[max(0, snippet_start-50):snippet_start+100]
                    print(f"[Session {session_id}] Snippet: ...{snippet}...")

                return {
                    "success": True,
                    "content": content,
                    "title": title,
                    "length": content_length,
                    "url": url,
                    "file": content_file
                }
            else:
                print(f"[Session {session_id}] Target content validation failed - no expected keywords")
                # Save for inspection
                content_file = f"/tmp/scraped_failed_session{session_id}_attempt{attempt}.html"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[Session {session_id}] Failed content saved for inspection: {content_file}")
                return {"success": False, "error": "Content validation failed", "length": content_length, "file": content_file}
        else:
            # Non-target URLs - less strict validation
            return {
                "success": True,
                "content": content,
                "title": title,
                "length": content_length,
                "url": url
            }

    except Exception as e:
        print(f"[Session {session_id}] curl_cffi error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def scrape_with_httpx(url: str, session_id: int, attempt: int = 1) -> dict:
    """Fallback scraper using httpx"""
    try:
        import httpx

        print(f"[Session {session_id}] Attempt {attempt}: Using httpx for {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-AU,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        time.sleep(random.uniform(2, 5))

        with httpx.Client(proxies=PROXY_URL, timeout=60, verify=False) as client:
            response = client.get(url, headers=headers, follow_redirects=True)

            print(f"[Session {session_id}] Status code: {response.status_code}")
            print(f"[Session {session_id}] Content length: {len(response.text)} chars")

            if response.status_code == 429:
                return {"success": False, "error": "Rate limited (429)"}

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}"}

            content = response.text
            content_length = len(content)

            if content_length < 1000:
                return {"success": False, "error": "Content too short", "length": content_length}

            # Extract title
            title = ""
            if "<title>" in content:
                title_start = content.find("<title>") + 7
                title_end = content.find("</title>", title_start)
                if title_end > title_start:
                    title = content[title_start:title_end]

            if url == TARGET_URL and ("st kilda" in content.lower() or "3182" in content):
                print(f"[Session {session_id}] ✓ Successfully scraped target!")
                return {
                    "success": True,
                    "content": content,
                    "title": title,
                    "length": content_length,
                    "url": url
                }
            elif url != TARGET_URL:
                return {
                    "success": True,
                    "content": content,
                    "title": title,
                    "length": content_length,
                    "url": url
                }
            else:
                return {"success": False, "error": "Content validation failed"}

    except Exception as e:
        print(f"[Session {session_id}] httpx error: {str(e)}")
        return {"success": False, "error": str(e)}


def scrape_session_thread(session_id: int, num_urls: int, results_queue: Queue):
    """Thread function for scraping session"""
    results = []

    print(f"\n{'='*60}")
    print(f"Starting Session {session_id} - Will scrape {num_urls} URLs")
    print(f"{'='*60}\n")

    # Select random URLs
    random_urls = random.sample(SAMPLE_URLS, min(num_urls - 1, len(SAMPLE_URLS)))

    # Insert target URL at random position
    target_position = random.randint(0, len(random_urls))
    all_urls = random_urls[:target_position] + [TARGET_URL] + random_urls[target_position:]

    for i, url in enumerate(all_urls, 1):
        is_target = url == TARGET_URL
        print(f"\n[Session {session_id}] Scraping {i}/{len(all_urls)}: {url} {'🎯 TARGET' if is_target else ''}")

        max_attempts = 5 if is_target else 1

        for attempt in range(1, max_attempts + 1):
            # Try curl_cffi first, fallback to httpx
            result = scrape_with_curl_cffi(url, session_id, attempt)

            if not result.get("success") and is_target and attempt > 2:
                print(f"[Session {session_id}] Trying fallback method (httpx)...")
                result = scrape_with_httpx(url, session_id, attempt)

            if result.get("success"):
                results.append(result)
                break
            elif is_target and attempt < max_attempts:
                wait_time = random.uniform(10, 25)
                print(f"[Session {session_id}] Target failed, waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                results.append(result)
                break

        # Random delay between URLs
        if i < len(all_urls):
            delay = random.uniform(5, 15)
            print(f"[Session {session_id}] Waiting {delay:.1f}s before next URL...")
            time.sleep(delay)

    successful = sum(1 for r in results if r.get("success"))
    print(f"\n[Session {session_id}] Completed: {successful}/{len(results)} successful")

    results_queue.put((session_id, results))


def main():
    """Main function"""
    print("\n" + "="*80)
    print("HTTP-BASED SCRAPER WITH CHROME IMPERSONATION")
    print("="*80)
    print(f"\nProxy: {PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}")
    print(f"Target: {TARGET_URL}")
    print(f"Concurrent Sessions: 3")
    print("\nThis scraper uses:")
    print("  - curl_cffi for Chrome impersonation")
    print("  - HTTP/2 support with realistic headers")
    print("  - Proxy authentication")
    print("  - httpx fallback")
    print("  - Multiple retry attempts")

    # Generate random configs
    session_configs = [
        (1, random.randint(5, 20)),
        (2, random.randint(5, 20)),
        (3, random.randint(5, 20))
    ]

    print("\nSession Configuration:")
    for session_id, num_urls in session_configs:
        print(f"  Session {session_id}: {num_urls} URLs")

    print("\n" + "="*80 + "\n")

    # Run sessions in threads
    start_time = time.time()
    results_queue = Queue()
    threads = []

    for session_id, num_urls in session_configs:
        thread = threading.Thread(target=scrape_session_thread, args=(session_id, num_urls, results_queue))
        thread.start()
        threads.append(thread)
        # Stagger thread starts
        time.sleep(2)

    # Wait for completion
    for thread in threads:
        thread.join()

    # Collect results
    all_results = {}
    while not results_queue.empty():
        session_id, results = results_queue.get()
        all_results[session_id] = results

    # Summary
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)

    total_scraped = sum(len(results) for results in all_results.values())
    total_successful = sum(sum(1 for r in results if r.get("success")) for results in all_results.values())
    target_successful = sum(
        sum(1 for r in results if r.get("success") and r.get("url") == TARGET_URL)
        for results in all_results.values()
    )

    print(f"\nTotal URLs scraped: {total_scraped}")
    print(f"Successful scrapes: {total_successful}/{total_scraped}")
    print(f"Target URL success: {target_successful}/3 sessions")
    print(f"Time elapsed: {time.time() - start_time:.1f}s")

    # Show target results
    print("\n" + "="*80)
    print("TARGET URL RESULTS")
    print("="*80)

    for session_id in sorted(all_results.keys()):
        results = all_results[session_id]
        target_results = [r for r in results if r.get("url") == TARGET_URL]
        if target_results:
            result = target_results[0]
            if result.get("success"):
                print(f"\n✓ Session {session_id}: SUCCESS")
                print(f"  Title: {result.get('title', 'N/A')}")
                print(f"  Content length: {result.get('length', 0)} chars")
                print(f"  Content file: {result.get('file', 'N/A')}")
            else:
                print(f"\n✗ Session {session_id}: FAILED - {result.get('error', 'Unknown error')}")
                if 'file' in result:
                    print(f"  Failed content file: {result.get('file')}")

    print("\n" + "="*80 + "\n")

    if target_successful > 0:
        print(f"🎉 Successfully scraped target in {target_successful} session(s)!")
        return 0
    else:
        print("❌ Failed to scrape target in all sessions")
        print("\nNote: This site uses Kasada anti-bot protection.")
        print("HTTP-only approaches may not work. A headful browser with full JS execution is required.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
