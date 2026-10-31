"""
Streamlit Community Cloud Keep-Alive & Auto Wake-Up Script
Gercek Headless Chromium (Playwright) tarayicisi ile Streamlit uygulamasina baglanir.
Uygulama uykudaysa ('This app has gone to sleep') 'Yes, get this app back up!' butonuna tiklar.
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

APP_URL = os.getenv("STREAMLIT_APP_URL", "https://scraper-mdqs3o4yvabvquqjrpozzf.streamlit.app")

async def main():
    print("🚀 [Streamlit Keep-Alive] Baslatiliyor...")
    print(f"📡 Hedef Uygulama: {APP_URL}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        try:
            print("🌐 Sayfaya gidiliyor...")
            response = await page.goto(APP_URL, wait_until="domcontentloaded", timeout=60000)
            status_code = response.status if response else 0
            print(f"📡 HTTP Durum Kodu: {status_code}")
            
            print("⏳ JavaScript ve WebSocket yuklenmesi bekleniyor (8s)...")
            await page.wait_for_timeout(8000)
            
            content = await page.content()
            title = await page.title()
            print(f"📄 Sayfa Basligi: '{title}'")
            
            is_sleeping = any(marker in content.lower() for marker in [
                "gone to sleep", "wake it back up", "zzzz", "would you like to wake"
            ])
            
            if is_sleeping:
                print("⚠️ UYKU MODU TESPIT EDILDI: 'This app has gone to sleep due to inactivity'")
                selectors = [
                    'button:has-text("Yes, get this app back up!")',
                    'button:has-text("get this app back up")',
                    'button:has-text("wake")',
                    'button:has-text("Yes")',
                    'button'
                ]
                
                clicked = False
                for sel in selectors:
                    locator = page.locator(sel)
                    cnt = await locator.count()
                    if cnt > 0:
                        for idx in range(cnt):
                            btn = locator.nth(idx)
                            txt = (await btn.inner_text()).strip()
                            if any(w in txt.lower() for w in ["yes", "wake", "back up", "get this app"]):
                                print(f"👉 Uyandirma Butonu Bulundu: '{txt}' -> Tiklaniyor...")
                                await btn.click()
                                clicked = True
                                break
                    if clicked:
                        break
                
                if clicked:
                    print("✓ Butona tiklandi! Uygulamanin acilmasi bekleniyor (30s)...")
                    await page.wait_for_timeout(30000)
                    post_content = await page.content()
                    if "gone to sleep" not in post_content.lower():
                        print("🎉 BASARILI: Streamlit uygulamasi uyandirildi ve canliya alindi!")
                    else:
                        print("⏳ Uygulama container'i baslatilma asamasinda.")
                else:
                    print("⚠️ Buton bulunamadi, ancak sayfa ziyaret edildi.")
            else:
                print("✅ HARIKA: Uygulama zaten uyanik ve aktif!")
                await page.wait_for_timeout(5000)
            
            await page.screenshot(path="keep_alive_status.png", full_page=False)
            print("📸 Durum ekran goruntusu kaydedildi: keep_alive_status.png")
            
        except Exception as e:
            print(f"❌ Islem hatasi: {e}")
            try:
                await page.screenshot(path="keep_alive_status.png", full_page=False)
            except Exception:
                pass
            sys.exit(1)
        finally:
            await browser.close()
            print("🏁 Tarayici kapatildi.")

if __name__ == "__main__":
    asyncio.run(main())
