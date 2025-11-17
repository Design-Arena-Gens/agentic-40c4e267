#!/usr/bin/env python3
import asyncio
import random
import time
import sys
from typing import List, Dict
from urllib.parse import urljoin
import subprocess
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

# Sample URLs to randomize requests (Australian real estate related)
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
    "https://www.realestate.com.au/vic/northcote-3070/",
    "https://www.realestate.com.au/vic/preston-3072/",
    "https://www.realestate.com.au/vic/footscray-3011/",
    "https://www.realestate.com.au/vic/williamstown-3016/",
    "https://www.realestate.com.au/vic/port-melbourne-3207/",
]


async def scrape_with_playwright(url: str, session_id: int, attempt: int = 1) -> Dict:
    """Scrape using Playwright with stealth mode and human-like behavior"""
    try:
        import os
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/tmp/playwright'

        from playwright.async_api import async_playwright

        print(f"[Session {session_id}] Attempt {attempt}: Using Playwright for {url}")

        async with async_playwright() as p:
            # Launch browser with extensive anti-detection
            # Using headful browser with Xvfb virtual display
            browser = await p.chromium.launch(
                headless=False,  # Headful as required by Kasada
                proxy={
                    "server": f"http://{PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}",
                    "username": PROXY_CONFIG['username'],
                    "password": PROXY_CONFIG['password']
                },
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--disable-web-security',
                    '--disable-features=BlockInsecurePrivateNetworkRequests',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certifcate-errors',
                    '--ignore-certifcate-errors-spki-list',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                ]
            )

            context = await browser.new_context(
                viewport={'width': random.randint(1366, 1920), 'height': random.randint(768, 1080)},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-AU',
                timezone_id='Australia/Melbourne',
                permissions=['geolocation'],
                geolocation={'latitude': -37.8136, 'longitude': 144.9631},  # Melbourne coordinates
                color_scheme='light',
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
                java_script_enabled=True,
            )

            # Add stealth scripts
            await context.add_init_script("""
                // Override the navigator.webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-AU', 'en-US', 'en']
                });

                // Override Chrome runtime
                window.chrome = {
                    runtime: {}
                };

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Add more realistic timing
                const originalGetTime = Date.prototype.getTime;
                Date.prototype.getTime = function() {
                    return originalGetTime.call(this) + Math.random() * 10;
                };
            """)

            page = await context.new_page()

            # Human-like behavior: random delay before navigation
            await asyncio.sleep(random.uniform(1.5, 4.0))

            # Navigate with realistic timeout
            try:
                await page.goto(url, wait_until='networkidle', timeout=60000)
            except Exception as e:
                print(f"[Session {session_id}] Navigation timeout, trying domcontentloaded...")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # Wait for page to load and execute scripts
            await asyncio.sleep(random.uniform(3.0, 6.0))

            # Random mouse movements to simulate human behavior
            for _ in range(random.randint(2, 5)):
                await page.mouse.move(
                    random.randint(100, 800),
                    random.randint(100, 600)
                )
                await asyncio.sleep(random.uniform(0.3, 0.8))

            # Scroll like a human
            for _ in range(random.randint(2, 4)):
                await page.evaluate(f"window.scrollBy(0, {random.randint(200, 500)})")
                await asyncio.sleep(random.uniform(0.5, 1.5))

            # Wait for content to be visible
            await asyncio.sleep(random.uniform(2.0, 4.0))

            # Get page content
            content = await page.content()
            title = await page.title()

            # Take screenshot for verification
            screenshot_path = f"/tmp/screenshot_session{session_id}_attempt{attempt}.png"
            await page.screenshot(path=screenshot_path, full_page=True)

            await browser.close()

            # Validate content
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
                print(f"[Session {session_id}] Content doesn't match expected (might be blocked)")
                return {"success": False, "error": "Content validation failed", "length": len(content)}

    except Exception as e:
        print(f"[Session {session_id}] Playwright error: {str(e)}")
        return {"success": False, "error": str(e)}


async def scrape_session(session_id: int, num_urls: int) -> List[Dict]:
    """Run a scraping session with random URLs and the target"""
    results = []

    print(f"\n{'='*60}")
    print(f"Starting Session {session_id} - Will scrape {num_urls} URLs")
    print(f"{'='*60}\n")

    # Select random URLs from sample list
    random_urls = random.sample(SAMPLE_URLS, min(num_urls - 1, len(SAMPLE_URLS)))

    # Insert target URL at random position
    target_position = random.randint(0, len(random_urls))
    all_urls = random_urls[:target_position] + [TARGET_URL] + random_urls[target_position:]

    for i, url in enumerate(all_urls, 1):
        is_target = url == TARGET_URL
        print(f"\n[Session {session_id}] Scraping {i}/{len(all_urls)}: {url} {'🎯 TARGET' if is_target else ''}")

        # Try multiple times for target URL
        max_attempts = 5 if is_target else 1

        for attempt in range(1, max_attempts + 1):
            result = await scrape_with_playwright(url, session_id, attempt)

            if result.get("success"):
                results.append(result)
                break
            elif is_target and attempt < max_attempts:
                wait_time = random.uniform(5, 15)
                print(f"[Session {session_id}] Target failed, waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                results.append(result)
                break

        # Random delay between URLs (human-like behavior)
        if i < len(all_urls):
            delay = random.uniform(3, 10)
            print(f"[Session {session_id}] Waiting {delay:.1f}s before next URL...")
            await asyncio.sleep(delay)

    # Summary
    successful = sum(1 for r in results if r.get("success"))
    print(f"\n[Session {session_id}] Completed: {successful}/{len(results)} successful")

    return results


async def main():
    """Main function to run concurrent sessions"""
    print("\n" + "="*80)
    print("KASADA-PROOF REAL ESTATE SCRAPER")
    print("="*80)
    print(f"\nProxy: {PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}")
    print(f"Target: {TARGET_URL}")
    print(f"Concurrent Sessions: 3")
    # Set browser path and display
    import os
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/tmp/playwright'
    os.environ['DISPLAY'] = ':99'
    print("✓ Using Playwright browsers from /tmp/playwright")
    print("✓ Using virtual display :99 for headful browser\n")

    # Generate random number of URLs for each session (5-20)
    session_configs = [
        (1, random.randint(5, 20)),
        (2, random.randint(5, 20)),
        (3, random.randint(5, 20))
    ]

    print("Session Configuration:")
    for session_id, num_urls in session_configs:
        print(f"  Session {session_id}: {num_urls} URLs")

    print("\n" + "="*80 + "\n")

    # Run sessions concurrently
    start_time = time.time()
    tasks = [scrape_session(session_id, num_urls) for session_id, num_urls in session_configs]
    all_results = await asyncio.gather(*tasks)

    # Final summary
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)

    total_scraped = sum(len(results) for results in all_results)
    total_successful = sum(sum(1 for r in results if r.get("success")) for results in all_results)
    target_successful = sum(
        sum(1 for r in results if r.get("success") and r.get("url") == TARGET_URL)
        for results in all_results
    )

    print(f"\nTotal URLs scraped: {total_scraped}")
    print(f"Successful scrapes: {total_successful}/{total_scraped}")
    print(f"Target URL success: {target_successful}/3 sessions")
    print(f"Time elapsed: {time.time() - start_time:.1f}s")

    # Show target results
    print("\n" + "="*80)
    print("TARGET URL RESULTS")
    print("="*80)

    for session_id, results in enumerate(all_results, 1):
        target_results = [r for r in results if r.get("url") == TARGET_URL]
        if target_results:
            result = target_results[0]
            if result.get("success"):
                print(f"\n✓ Session {session_id}: SUCCESS")
                print(f"  Title: {result.get('title', 'N/A')}")
                print(f"  Content length: {result.get('length', 0)} chars")
                print(f"  Screenshot: {result.get('screenshot', 'N/A')}")

                # Save content to file
                content_file = f"/tmp/scraped_content_session{session_id}.html"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('content', ''))
                print(f"  Content saved: {content_file}")

                # Show snippet of content
                content = result.get('content', '')
                if 'st kilda' in content.lower():
                    snippet_start = content.lower().find('st kilda')
                    snippet = content[max(0, snippet_start-100):snippet_start+200]
                    print(f"  Content snippet: ...{snippet}...")
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
    sys.exit(asyncio.run(main()))
