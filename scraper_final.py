#!/usr/bin/env python3
"""
Enhanced scraper with maximum stealth for Kasada bypass
Uses multiple anti-detection libraries and techniques
"""
import asyncio
import random
import time
import sys
import os
from typing import Dict, List

# Set environment
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/tmp/playwright'
os.environ['DISPLAY'] = ':99'

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
]


async def scrape_with_max_stealth(url: str, session_id: int, attempt: int = 1) -> Dict:
    """Scrape with maximum stealth settings"""
    try:
        from playwright.async_api import async_playwright

        print(f"[Session {session_id}] Attempt {attempt}: Max stealth mode for {url}")

        async with async_playwright() as p:
            # More realistic browser args
            browser = await p.chromium.launch(
                headless=False,
                proxy={
                    "server": f"http://{PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}",
                    "username": PROXY_CONFIG['username'],
                    "password": PROXY_CONFIG['password']
                },
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-extensions',
                    '--disable-default-apps',
                    f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                ]
            )

            # Create context with realistic settings
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='en-AU',
                timezone_id='Australia/Melbourne',
                geolocation={'latitude': -37.8670, 'longitude': 144.9805},  # St Kilda coordinates
                permissions=['geolocation'],
                color_scheme='light',
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
            )

            # Maximum stealth injection
            await context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });

                // Override the permissions API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        },
                        {
                            0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                            description: "Native Client",
                            filename: "internal-nacl-plugin",
                            length: 2,
                            name: "Native Client"
                        }
                    ]
                });

                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-AU', 'en-GB', 'en-US', 'en']
                });

                // Mock Chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };

                // Override hardwareConcurrency with realistic value
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });

                // Override platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });

                // Override vendor
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.'
                });

                // Add missing chrome properties
                Object.defineProperty(window, 'chrome', {
                    writable: true,
                    enumerable: true,
                    configurable: false,
                    value: {
                        runtime: {}
                    }
                });

                // Mock battery API
                navigator.getBattery = async () => ({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                });

                // Randomize timing attacks
                const originalGetTime = Date.prototype.getTime;
                Date.prototype.getTime = function() {
                    return originalGetTime.call(this) + Math.random();
                };

                // WebGL vendor override
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };
            """)

            page = await context.new_page()

            # Very long initial wait - let any tracking scripts initialize
            await asyncio.sleep(random.uniform(5, 8))

            try:
                # Navigate with extended timeout
                await page.goto(url, wait_until='domcontentloaded', timeout=90000)
            except Exception as e:
                print(f"[Session {session_id}] Navigation error: {e}, continuing...")

            # Critical: Wait for Kasada VM to execute
            print(f"[Session {session_id}] Waiting for Kasada VM execution...")
            await asyncio.sleep(random.uniform(12, 18))

            # Simulate very human-like behavior
            for _ in range(random.randint(5, 8)):
                # Random mouse path
                x_path = [random.randint(100, 1800) for _ in range(3)]
                y_path = [random.randint(100, 900) for _ in range(3)]

                for x, y in zip(x_path, y_path):
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                # Random click occasionally
                if random.random() > 0.7:
                    await page.mouse.click(random.randint(200, 1700), random.randint(200, 800))
                    await asyncio.sleep(random.uniform(0.5, 1.0))

            # Natural scrolling behavior
            for _ in range(random.randint(4, 7)):
                scroll_amount = random.randint(150, 400)
                await page.evaluate(f"window.scrollBy({{top: {scroll_amount}, left: 0, behavior: 'smooth'}})")
                await asyncio.sleep(random.uniform(1.0, 2.5))

            # Additional wait for dynamic content
            await asyncio.sleep(random.uniform(5, 8))

            # Get content
            content = await page.content()
            title = await page.title()

            # Screenshot
            screenshot_path = f"/tmp/screenshot_final_s{session_id}_a{attempt}.png"
            await page.screenshot(path=screenshot_path, full_page=True)

            await browser.close()

            # Validate
            content_length = len(content)
            print(f"[Session {session_id}] Content: {content_length} chars, Title: {title}")

            # Check for success indicators
            has_st_kilda = "st kilda" in content.lower() or "st-kilda" in content.lower()
            has_postcode = "3182" in content
            has_listings = "property" in content.lower() or "real estate" in content.lower()

            if content_length > 10000 and (has_st_kilda or has_postcode or has_listings):
                print(f"[Session {session_id}] ✅ SUCCESS! Found real content")

                # Save successful content
                content_file = f"/tmp/SUCCESS_session{session_id}_attempt{attempt}.html"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                return {
                    "success": True,
                    "content": content,
                    "title": title,
                    "length": content_length,
                    "screenshot": screenshot_path,
                    "file": content_file,
                    "url": url
                }
            else:
                print(f"[Session {session_id}] ⚠️  Content too short or missing keywords")
                return {"success": False, "error": "Likely blocked", "length": content_length}

    except Exception as e:
        print(f"[Session {session_id}] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def scrape_session(session_id: int, num_urls: int) -> List[Dict]:
    """Scrape session with URLs"""
    results = []

    print(f"\n{'='*60}")
    print(f"Session {session_id}: {num_urls} URLs")
    print(f"{'='*60}\n")

    # Select URLs
    random_urls = random.sample(SAMPLE_URLS, min(num_urls - 1, len(SAMPLE_URLS)))
    target_pos = random.randint(0, len(random_urls))
    all_urls = random_urls[:target_pos] + [TARGET_URL] + random_urls[target_pos:]

    for i, url in enumerate(all_urls, 1):
        is_target = url == TARGET_URL
        print(f"\n[Session {session_id}] URL {i}/{len(all_urls)}: {url} {'🎯' if is_target else ''}")

        max_attempts = 5 if is_target else 1

        for attempt in range(1, max_attempts + 1):
            result = await scrape_with_max_stealth(url, session_id, attempt)

            if result.get("success"):
                results.append(result)
                break
            elif is_target and attempt < max_attempts:
                wait_time = random.uniform(15, 30)
                print(f"[Session {session_id}] Retry in {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            else:
                results.append(result)
                break

        # Inter-URL delay
        if i < len(all_urls):
            delay = random.uniform(10, 20)
            print(f"[Session {session_id}] Next URL in {delay:.1f}s...")
            await asyncio.sleep(delay)

    return results


async def main():
    """Main execution"""
    print("\n" + "="*80)
    print("KASADA BYPASS SCRAPER - MAXIMUM STEALTH MODE")
    print("="*80)
    print(f"\nProxy: {PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}")
    print(f"Target: {TARGET_URL}")
    print(f"Sessions: 3 concurrent")
    print(f"\nTechniques:")
    print("  ✓ Headful browser on Xvfb")
    print("  ✓ Extended Kasada VM execution wait")
    print("  ✓ Advanced navigator override")
    print("  ✓ Human behavior simulation")
    print("  ✓ St Kilda geolocation")
    print("  ✓ Smooth scrolling & mouse paths")
    print("  ✓ Multiple retry attempts\n")

    # Session configs
    configs = [(1, random.randint(5, 10)), (2, random.randint(5, 10)), (3, random.randint(5, 10))]

    print("Configuration:")
    for sid, nurls in configs:
        print(f"  Session {sid}: {nurls} URLs")
    print("\n" + "="*80)

    start_time = time.time()

    # Run sessions
    tasks = [scrape_session(sid, nurls) for sid, nurls in configs]
    all_results = await asyncio.gather(*tasks)

    # Summary
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)

    total = sum(len(r) for r in all_results)
    successful = sum(sum(1 for res in r if res.get("success")) for r in all_results)
    target_success = sum(
        sum(1 for res in r if res.get("success") and res.get("url") == TARGET_URL)
        for r in all_results
    )

    print(f"\nTotal: {successful}/{total} successful")
    print(f"Target: {target_success}/3 sessions")
    print(f"Time: {time.time() - start_time:.1f}s")

    print("\n" + "="*80)
    print("TARGET RESULTS")
    print("="*80)

    for sid, results in enumerate(all_results, 1):
        target_results = [r for r in results if r.get("url") == TARGET_URL]
        if target_results:
            result = target_results[0]
            if result.get("success"):
                print(f"\n✅ Session {sid}: SUCCESS")
                print(f"   Title: {result.get('title', 'N/A')}")
                print(f"   Length: {result.get('length', 0)} chars")
                print(f"   File: {result.get('file', 'N/A')}")
                print(f"   Screenshot: {result.get('screenshot', 'N/A')}")
            else:
                print(f"\n❌ Session {sid}: FAILED - {result.get('error', 'Unknown')}")

    print("\n" + "="*80 + "\n")

    if target_success > 0:
        print(f"🎉 Successfully scraped {target_success} session(s)!")
        return 0
    else:
        print("❌ All sessions failed. Kasada protection is very strong.")
        print("\nRecommendation: Use commercial service (ScrapingBee, BrightData)")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
