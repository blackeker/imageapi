# ⚡ Multi-Category AI Image Studio & Comprehensive API Suite

Perchance, Stable Horde (SDXL) ve Pollinations motorlarını tek bir çatı altında birleştiren, kategorilere ve stillere ayrılmış, REST API ve Cyberpunk Web Dashboard destekli tam teşekküllü görsel üretim paketi.

---

## 🌟 Desteklenen Kategoriler ve Stiller

Sistem yalnızca anime ile sınırlı olmayıp, otomatik optimize edilen prompt ve negatif prompt motoruyla 7 ana kategoriyi ve onlarca alt stili destekler:

1. **`anime`** (Anime & Manga): Modern Anime, Ghibli, Cyberpunk Anime, Makoto Shinkai
2. **`photorealistic`** (Fotogerçekçi / Portre): Stüdyo Portresi, Sinematik Film Karesi, Sokak Fotoğrafçılığı
3. **`cyberpunk`** (Siberpunk & Bilim Kurgu): Neon Gece Şehri, Mecha Savaşçısı, Space Opera
4. **`fantasy`** (Fantastik & RPG): Dark Fantasy, High Fantasy, Mitolojik Yaratıklar
5. **`digital_art`** (3D Render & Konsept Sanatı): Pixar 3D, Dijital Konsept Çizim, İzometrik 3D
6. **`pixel_art`** (Pixel Art & Retro): 16-Bit Retro Oyun, 80'ler Synthwave
7. **`oil_painting`** (Klasik Sanat & Yağlı Boya): Rönesans Yağlı Boya, Suluboya

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum:
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Web Kontrol Panelini ve API Sunucusunu Başlatma:
```bash
python app.py
```
* Tarayıcınızdan **`http://localhost:5000`** adresine giderek kategori seçicili canlı görsel üretim panelini kullanabilirsiniz.

---

## 🌐 REST API Kullanımı

Sunucu çalışırken (`python app.py`) aşağıdaki REST API v1 endpoint'lerini kullanabilirsiniz:

### 1. Kategorileri ve Stilleri Listeleme (`GET /api/v1/categories`)
```bash
curl http://localhost:5000/api/v1/categories
```

### 2. Görsel Üretimi (`POST /api/v1/generate`)
```bash
curl -X POST http://localhost:5000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "futuristic cyber sports car in rainy street",
    "category": "cyberpunk",
    "style": "neon_city",
    "provider": "horde",
    "shape": "landscape"
  }'
```

**Yanıt (JSON):**
```json
{
  "success": true,
  "provider": "horde",
  "category": "cyberpunk",
  "style": "neon_city",
  "filename": "horde_1790768000_123.png",
  "url": "/api/v1/gallery/horde_1790768000_123.png",
  "size_kb": 245.8
}
```

### 3. Galeri ve Görsel Alma (`GET /api/v1/gallery`)
```bash
curl http://localhost:5000/api/v1/gallery
```

---

## 🐍 Python SDK ile Kullanım

```python
from sdk import ImageClient

client = ImageClient(base_url="http://localhost:5000")

# 1. Kategorileri Al
categories = client.get_categories()

# 2. Cyberpunk veya Anime Görseli Üret
image = client.generate(
    prompt="cyber samurai standing in neon alley",
    category="cyberpunk",
    style="neon_city",
    provider="horde",
    shape="landscape"
)

# 3. Dosyayı Kaydet
image.save("cyber_samurai.png")
print(f"Görsel kaydedildi: {image.url} ({image.size_kb} KB)")
```

---

## 💻 Komut Satırı (CLI) Kullanımı

```bash
# Kategorileri listele:
python cli.py --categories

# Belirli bir kategori ve stille görsel üret:
python cli.py --prompt "neon mecha warrior" --category cyberpunk --style mecha --provider horde

# Perchance ile üret:
python cli.py --prompt "anime rogue girl with neon hair" --category anime --provider perchance

# Galerideki görselleri listele:
python cli.py --gallery
```

---

## 📁 Proje Dizin Yapısı

```
apitest/
├── app.py                # Flask REST API Sunucusu + Çok Kategorili Web Dashboard
├── categories.py         # Kategori ve stil taksonomisi & akıllı prompt motoru
├── core_engine.py        # Perchance, Horde & Pollinations çoklu motor yöneticisi
├── sdk.py                # Python Client SDK kütüphanesi
├── cli.py                # Terminal CLI aracı
├── perchance_service.py  # Bağımsız Perchance API servisi
├── horde_api.py          # Bağımsız Stable Horde API servisi
├── pollinations_api.py   # Bağımsız Pollinations API servisi
├── gallery/              # Üretilen görsellerin saklandığı galeri dizini
├── requirements.txt      # Gerekli kütüphaneler
└── README.md             # Dokümantasyon
```
