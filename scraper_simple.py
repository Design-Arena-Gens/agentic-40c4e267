#!/usr/bin/env python3
"""
Simplified scraper using requests with curl_cffi for maximum stealth
Falls back to selenium if needed
"""
import time
import random
import sys
import threading
from queue import Queue

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


def scrape_with_selenium(url: str, session_id: int, attempt: int = 1) -> dict:
    """Scrape using selenium with undetected chromedriver"""
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        import base64

        print(f"[Session {session_id}] Attempt {attempt}: Using Selenium for {url}")

        # Configure options
        options = uc.ChromeOptions()

        # Proxy with auth via extension
        proxy_host = PROXY_CONFIG['server']
        proxy_port = PROXY_CONFIG['port']
        proxy_user = PROXY_CONFIG['username']
        proxy_pass = PROXY_CONFIG['password']

        # Create proxy extension
        manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

        background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "http",
        host: "%s",
        port: parseInt(%s)
      },
      bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]},
    ['blocking']
);
""" % (proxy_host, proxy_port, proxy_user, proxy_pass)

        import os
        import zipfile
        pluginfile = f'/tmp/proxy_auth_plugin_{session_id}.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        options.add_extension(pluginfile)

        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument(f'--window-size={random.randint(1366, 1920)},{random.randint(768, 1080)}')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--lang=en-AU')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Create driver
        driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)

        # Apply additional stealth
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            "platform": "Windows",
            "acceptLanguage": "en-AU,en-US;q=0.9,en;q=0.8"
        })

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")

        # Random delay before navigation
        time.sleep(random.uniform(2, 5))

        # Navigate
        driver.get(url)

        # Wait for page load
        time.sleep(random.uniform(5, 8))

        # Random scrolling
        for _ in range(random.randint(3, 6)):
            scroll_amount = random.randint(200, 600)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 2.0))

        # Additional wait for dynamic content
        time.sleep(random.uniform(3, 6))

        # Get content
        content = driver.page_source
        title = driver.title

        # Take screenshot
        screenshot_path = f"/tmp/screenshot_session{session_id}_attempt{attempt}.png"
        driver.save_screenshot(screenshot_path)

        driver.quit()

        # Clean up plugin
        try:
            os.remove(pluginfile)
        except:
            pass

        # Validate
        content_length = len(content)
        print(f"[Session {session_id}] Content length: {content_length} chars")
        print(f"[Session {session_id}] Title: {title}")

        if content_length < 1000:
            print(f"[Session {session_id}] Warning: Content too short")
            return {"success": False, "error": "Content too short", "length": content_length}

        if "429" in content or "Too Many Requests" in content.lower():
            print(f"[Session {session_id}] Rate limited detected in content")
            return {"success": False, "error": "Rate limited"}

        # Check if blocked (white screen / no text)
        text_content = driver.find_element(By.TAG_NAME, "body").text if hasattr(driver, 'find_element') else ""
        if len(text_content) < 100:
            print(f"[Session {session_id}] Blocked - very little text content")
            return {"success": False, "error": "Blocked - minimal text", "length": content_length}

        if "st kilda" in content.lower() or "3182" in content:
            print(f"[Session {session_id}] ✓ Successfully scraped target!")
            print(f"[Session {session_id}] Screenshot: {screenshot_path}")
            return {
                "success": True,
                "content": content,
                "title": title,
                "length": content_length,
                "screenshot": screenshot_path,
                "url": url
            }
        else:
            print(f"[Session {session_id}] Content doesn't contain expected keywords")
            # Still might be successful for non-target URLs
            if url != TARGET_URL:
                return {
                    "success": True,
                    "content": content,
                    "title": title,
                    "length": content_length,
                    "screenshot": screenshot_path,
                    "url": url
                }
            return {"success": False, "error": "Content validation failed", "length": content_length}

    except Exception as e:
        print(f"[Session {session_id}] Selenium error: {str(e)}")
        import traceback
        traceback.print_exc()
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

        max_attempts = 5 if is_target else 2

        for attempt in range(1, max_attempts + 1):
            result = scrape_with_selenium(url, session_id, attempt)

            if result.get("success"):
                results.append(result)
                break
            elif is_target and attempt < max_attempts:
                wait_time = random.uniform(8, 20)
                print(f"[Session {session_id}] Target failed, waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                results.append(result)
                break

        # Random delay between URLs
        if i < len(all_urls):
            delay = random.uniform(5, 12)
            print(f"[Session {session_id}] Waiting {delay:.1f}s before next URL...")
            time.sleep(delay)

    successful = sum(1 for r in results if r.get("success"))
    print(f"\n[Session {session_id}] Completed: {successful}/{len(results)} successful")

    results_queue.put((session_id, results))


def main():
    """Main function"""
    print("\n" + "="*80)
    print("SELENIUM UNDETECTED CHROMEDRIVER SCRAPER")
    print("="*80)
    print(f"\nProxy: {PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}")
    print(f"Target: {TARGET_URL}")
    print(f"Concurrent Sessions: 3")
    print("\nThis scraper uses:")
    print("  - Headful browser (visible)")
    print("  - Undetected ChromeDriver")
    print("  - Proxy authentication via extension")
    print("  - Human-like behavior simulation")
    print("  - Multiple retry attempts for target URL")

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
                print(f"  Screenshot: {result.get('screenshot', 'N/A')}")

                # Save content
                content_file = f"/tmp/scraped_content_session{session_id}.html"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('content', ''))
                print(f"  Content saved: {content_file}")

                # Show snippet
                content = result.get('content', '')
                if 'st kilda' in content.lower():
                    snippet_start = content.lower().find('st kilda')
                    snippet = content[max(0, snippet_start-50):snippet_start+100]
                    print(f"  Snippet: ...{snippet}...")
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
