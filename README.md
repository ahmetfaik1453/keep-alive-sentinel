# Cloud Keep-Alive Sentinel

Bu repo, harici bulut servislerini (Hugging Face Space, Streamlit Community Cloud ve Supabase veritabanları) uyku moduna geçmekten korumak ve canlı tutmak için tasarlanmış merkezi otomasyon deposudur.

## Güvenlik İlkeleri (Zero-Leakage Security)
- Bu depodaki hiçbir kaynak kodunda (`.py`, `.yml`, `.md`) gizli anahtar, token veya veritabanı şifresi yer almaz.
- Tüm hassas kimlik bilgileri GitHub Actions Encrypted Secrets (`${{ secrets.* }}`) üzerinden çalışma anında sanal makine belleğine aktarılır.
- Depo yalnızca zamanlanmış görevlerle (`schedule`) ve manuel yetkili tetiklemelerle (`workflow_dispatch`) çalışır.

## Görevler
1. **Hugging Face Private Space Wake-Up:** Belirli aralıklarla REST ping göndererek container'ın uykuya geçmesini engeller.
2. **Streamlit Keep-Alive:** Playwright tarayıcısı ile Streamlit uygulamasını denetler, uyku ekranı tespiti durumunda otomatik uyandırma butonuna tıklar.
3. **Supabase Multi-Project Keep-Alive:** Supabase ücretsiz planındaki veritabanlarının 7 gün hareketsizlik sebebiyle duraklatılmasını (auto-pause) engellemek için günlük canlılık sorguları atar.
