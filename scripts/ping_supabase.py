"""
Multi-Project Supabase Keep-Alive Ping Script
Ortam degiskenlerinde tanimli tum Supabase projelerini otomatik tespit eder ve
PostgREST / Auth health endpoint'lerine canlilik sorgusu gondererek 7 gunluk hareketsizlik
nedeniyle duraklatilmalarini (auto-pause) engeller.
"""
import os
import sys
import urllib.request
import urllib.error

def mask_url(url: str) -> str:
    if not url:
        return "N/A"
    try:
        parts = url.split("://")
        proto = parts[0]
        host = parts[1].split("/")[0]
        if "." in host:
            sub = host.split(".")[0]
            masked_sub = sub[:4] + "***" if len(sub) > 4 else "***"
            domain = ".".join(host.split(".")[1:])
            return f"{proto}://{masked_sub}.{domain}"
        return f"{proto}://***"
    except Exception:
        return "***"

def ping_target(name: str, url: str, key: str) -> bool:
    print(f"\n🔍 [Supabase Ping] Proje: {name}")
    print(f"   Hedef Host: {mask_url(url)}")
    
    if not url or not key:
        print("   ⚠️ URL veya API Key eksik, atlaniyor.")
        return False

    base_url = url.rstrip('/')
    # PostgREST ve Auth endpoint'leri
    endpoints = [
        f"{base_url}/rest/v1/",
        f"{base_url}/auth/v1/health"
    ]
    
    success = False
    for ep in endpoints:
        req = urllib.request.Request(
            ep,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "User-Agent": "KeepAliveSentinel/1.0"
            },
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.status
                print(f"   📡 Endpoint '{ep.split('/')[-1]}' -> HTTP {code} OK")
                success = True
                break
        except urllib.error.HTTPError as e:
            # 200 disinda 401/404 vb. gelse bile veritabani / sunucu istegi islemis olur
            print(f"   📡 Endpoint yanıtı: HTTP {e.code}")
            if e.code < 500:
                success = True
                break
        except Exception as err:
            print(f"   ⚠️ Baglanti uyarisi: {err}")

    return success

def main():
    print("========================================")
    print("🚀 Supabase Coklu Proje Canlilik Denetimi")
    print("========================================")
    
    # SUPABASE_URL_* ile baslayan tum ortam degiskenlerini bul
    targets = {}
    for k, v in os.environ.items():
        if k.startswith("SUPABASE_URL_"):
            proj_name = k[len("SUPABASE_URL_"):]
            key_var = f"SUPABASE_KEY_{proj_name}"
            api_key = os.environ.get(key_var, "")
            targets[proj_name] = (v, api_key)
            
    if not targets:
        print("⚠️ Hicbir SUPABASE_URL_* ortam degiskeni bulunamadi.")
        return

    print(f"📋 Tespit Edilen Proje Sayisi: {len(targets)}")
    
    results = {}
    for name, (url, key) in targets.items():
        results[name] = ping_target(name, url, key)
        
    print("\n================ Ozet ================")
    all_ok = True
    for name, ok in results.items():
        status_text = "✅ AKTIF" if ok else "❌ ULASILAMADI"
        print(f" - {name}: {status_text}")
        if not ok:
            all_ok = False
            
    if not all_ok:
        print("\n⚠️ Bazi projelere erisilemedi, detaylar yukarida.")
    else:
        print("\n🎉 Tum Supabase projeleri basariyla yoklandi!")

if __name__ == "__main__":
    main()
