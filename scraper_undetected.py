#!/usr/bin/env python3
"""
Alternative scraper using undetected-chromedriver for maximum stealth
"""
import time
import random
import sys
from typing import List, Dict
import threading
from queue import Queue

# Proxy configuration
PROXY_CONFIG = {
    "username": "c147d949a38ca89c4c3a__cr.au,gb,us",
    "password": "b7351118825adfbd",
    "server": "gw.dataimpulse.com",
    "port": "823"
}

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


def scrape_with_undetected(url: str, session_id: int, attempt: int = 1) -> Dict:
    """Scrape using undetected-chromedriver"""
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium_stealth import stealth

        print(f"[Session {session_id}] Attempt {attempt}: Using Undetected ChromeDriver for {url}")

        # Configure options
        options = uc.ChromeOptions()

        # Add proxy with authentication
        proxy_string = f"{PROXY_CONFIG['username']}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}"
        options.add_argument(f'--proxy-server=http://{PROXY_CONFIG["server"]}:{PROXY_CONFIG["port"]}')

        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument(f'--window-size={random.randint(1366, 1920)},{random.randint(768, 1080)}')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Create driver
        driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)

        # Apply stealth
        stealth(driver,
            languages=["en-AU", "en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        # Handle proxy authentication
        import base64
        proxy_auth = f"{PROXY_CONFIG['username']}:{PROXY_CONFIG['password']}"
        proxy_auth_encoded = base64.b64encode(proxy_auth.encode()).decode()

        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
            'headers': {
                'Proxy-Authorization': f'Basic {proxy_auth_encoded}'
            }
        })

        # Random delay before navigation
        time.sleep(random.uniform(2, 4))

        # Navigate
        driver.get(url)

        # Wait and execute human-like behavior
        time.sleep(random.uniform(4, 7))

        # Random scrolling
        for _ in range(random.randint(3, 6)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)})")
            time.sleep(random.uniform(0.5, 1.5))

        # Wait for content
        time.sleep(random.uniform(3, 5))

        # Get content
        content = driver.page_source
        title = driver.title

        # Take screenshot
        screenshot_path = f"/tmp/screenshot_uc_session{session_id}_attempt{attempt}.png"
        driver.save_screenshot(screenshot_path)

        driver.quit()

        # Validate
        if len(content) < 1000:
            print(f"[Session {session_id}] Warning: Content too short ({len(content)} chars)")
            return {"success": False, "error": "Content too short", "length": len(content)}

        if "429" in content or "Too Many Requests" in content:
            print(f"[Session {session_id}] Rate limited")
            return {"success": False, "error": "Rate limited"}

        if "st kilda" in content.lower() or "3182" in content:
            print(f"[Session {session_id}] ✓ Successfully scraped! Content length: {len(content)}")
            print(f"[Session {session_id}] Title: {title}")
            print(f"[Session {session_id}] Screenshot saved: {screenshot_path}")
            return {
                "success": True,
                "content": content,
                "title": title,
                "length": len(content),
                "screenshot": screenshot_path,
                "url": url
            }
        else:
            print(f"[Session {session_id}] Content doesn't match expected")
            return {"success": False, "error": "Content validation failed", "length": len(content)}

    except Exception as e:
        print(f"[Session {session_id}] Undetected ChromeDriver error: {str(e)}")
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
            result = scrape_with_undetected(url, session_id, attempt)

            if result.get("success"):
                results.append(result)
                break
            elif is_target and attempt < max_attempts:
                wait_time = random.uniform(5, 15)
                print(f"[Session {session_id}] Target failed, waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                results.append(result)
                break

        # Random delay between URLs
        if i < len(all_urls):
            delay = random.uniform(3, 10)
            print(f"[Session {session_id}] Waiting {delay:.1f}s before next URL...")
            time.sleep(delay)

    successful = sum(1 for r in results if r.get("success"))
    print(f"\n[Session {session_id}] Completed: {successful}/{len(results)} successful")

    results_queue.put((session_id, results))


def main():
    """Main function"""
    print("\n" + "="*80)
    print("UNDETECTED CHROMEDRIVER SCRAPER")
    print("="*80)
    print(f"\nProxy: {PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}")
    print(f"Target: {TARGET_URL}")
    print(f"Concurrent Sessions: 3")

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
                print(f"  Screenshot: {result.get('screenshot', 'N/A')}")

                # Save content
                content_file = f"/tmp/scraped_content_uc_session{session_id}.html"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('content', ''))
                print(f"  Content saved: {content_file}")
            else:
                print(f"\n✗ Session {session_id}: FAILED - {result.get('error', 'Unknown error')}")

    print("\n" + "="*80 + "\n")

    if target_successful > 0:
        print(f"🎉 Successfully scraped target in {target_successful} session(s)!")
        return 0
    else:
        print("❌ Failed to scrape target in all sessions")
        return 1


if __name__ == "__main__":
    sys.exit(main())
