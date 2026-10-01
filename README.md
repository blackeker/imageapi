# ⚡ OmniArt AI - Multi-Engine Image Generation API & Web Studio

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/API-Flask%20REST%20v1-green.svg)](https://flask.palletsprojects.com/)
[![Playwright](https://img.shields.io/badge/Browser-Playwright%20Stealth-orange.svg)](https://playwright.dev/)
[![Engines](https://img.shields.io/badge/Engines-Perchance%20%7C%20SDXL%20%7C%20Pollinations-purple.svg)](#-yapay-zeka-motorlar%C4%B1)
[![Styles](https://img.shields.io/badge/Styles-100%2B%20Art%20Styles-red.svg)](#-desteklenen-100-sanat-stili)

**OmniArt AI**, Perchance AI, Stable Horde (SDXL / Animagine) ve Pollinations motorlarını tek bir çatı altında birleştiren, anti-bot/Cloudflare korumalarını aşabilen, 100'den fazla sanat stilini ve 3 ana en-boy oranını destekleyen tam teşekküllü **REST API, Web Stüdyosu, Python SDK ve CLI** paketidir.

---

## 🚀 Öne Çıkan Özellikler

- 🎨 **100+ Sanat Stili:** Painted Anime Plus, Studio Ghibli, 3D Pixar, Stüdyo Portresi, Cyberpunk, Yağlı Boya, Pixel Art ve onlarca özel stil.
- 📐 **Birebir Çözünürlük Desteği:** `768x512` (Landscape), `512x512` (Square), `512x768` (Portrait).
- 🛡️ **Gelişmiş Bot Koruması Aşma (Stealth Engine):** Perchance Cloudflare Turnstile korumasını hem masaüstü hem de sunucu (Xvfb / Headless) ortamında aşar.
- ⚡ **Akıllı Dağıtık Motorlar:**
  - **`Perchance`**: Ultra keskin, sanatsal anime, illüstrasyon ve yaratıcı çizimler.
  - **`Stable Horde`**: SDXL, Animagine XL, Pony Diffusion modelleriyle ücretsiz ve filigransız üretim.
  - **`Pollinations`**: Anlık ve hızlı prototipleme için yedek motor.
- 🌐 **Modern & Minimalist Web Arayüzü:** Kategori hapları, canlı önizleme, anlık indirme ve galeri paneli.
- 🔌 **REST API v1:** Her dilden (Python, Node.js, PHP, Go, cURL) çağrılabilir standart JSON endpoint'leri.
- 🐍 **Python SDK & CLI:** Terminalden tek komutla veya Python kodunuzdan 2 satırda görsel üretimi.

---

## 📦 Kurulum

### 1. Gereksinimleri Yükleyin:
```bash
git clone https://github.com/blackeker/imageapi.git
cd imageapi
pip install -r requirements.txt
playwright install chromium
```

### 2. Linux / VPS Sunucularda Sanal Ekran (Xvfb) Kurulumu (Önerilen):
Perchance'in Cloudflare korumasını sunucularda en yüksek başarı oranıyla aşmak için sanal ekran önerilir:
```bash
# Ubuntu / Debian:
sudo apt-get update && sudo apt-get install -y xvfb

# Sunucuyu sanal ekranla başlatma:
xvfb-run -a python app.py
```
*(Not: `Xvfb` olmadan doğrudan `python app.py` çalıştırdığınızda sistem otomatik olarak Linux ortamını tespit edip Headless moda geçer.)*

### 3. Windows / macOS Ortamında Başlatma:
```bash
python app.py
```
* Tarayıcınızdan **`http://localhost:5000`** adresine giderek stüdyo panelini kullanabilirsiniz.

---

## 🌐 REST API Dokümantasyonu (v1)

### 1. Görsel Üretimi (`POST /api/v1/generate`)

Belirtilen prompt, stil, motor ve boyutla görsel üretir.

**İstek (cURL):**
```bash
curl -X POST http://localhost:5000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk rogue samurai with neon plasma katana in rainy alley",
    "provider": "perchance",
    "style": "Painted Anime Plus",
    "shape": "768x512"
  }'
```

**İstek Gövdesi Parametreleri:**
| Parametre | Tip | Varsayılan | Açıklama |
| :--- | :--- | :--- | :--- |
| `prompt` | `string` | *(Zorunlu)* | Üretilmek istenen görselin açıklaması. |
| `category` | `string` | `"anime"` | `anime`, `photorealistic`, `cyberpunk`, `fantasy`, `digital_art`, `pixel_art`, `oil_painting` |
| `style` | `string` | `"Painted Anime Plus"` | 100+ stilden herhangi biri (örn: `Studio Ghibli`, `Cinematic`, `Pixel Art`) |
| `provider` | `string` | `"auto"` | `auto`, `perchance`, `horde`, `pollinations` |
| `shape` | `string` | `"768x512"` | `768x512` (Landscape), `512x512` (Square), `512x768` (Portrait) |

**Başarılı Yanıt (JSON - `200 OK`):**
```json
{
  "success": true,
  "provider": "perchance",
  "category": "anime",
  "style": "Painted Anime Plus",
  "shape": "768x512",
  "filename": "perchance_1790768000_123.png",
  "url": "/api/gallery/perchance_1790768000_123.png",
  "elapsed_seconds": 28.4,
  "size_kb": 142.6
}
```

---

### 2. Kategorileri ve Stilleri Listeleme (`GET /api/v1/categories`)

```bash
curl http://localhost:5000/api/v1/categories
```

---

### 3. Galeri Listesini Alma (`GET /api/v1/gallery`)

```bash
curl http://localhost:5000/api/v1/gallery
```

---

### 4. Sağlık Kontrolü (`GET /api/v1/health`)

```bash
curl http://localhost:5000/api/v1/health
```

---

## 🎨 Desteklenen 100+ Sanat Stili

| Kategori | Stiller |
| :--- | :--- |
| 🌸 **Anime & Manga** | `Painted Anime Plus`, `Painted Anime`, `Studio Ghibli`, `Neon Vintage Anime`, `Vintage Anime`, `Cute Anime`, `Soft Anime`, `Drawn Anime`, `Manga`, `Waifu`, `Dragonball`, `YuGiOh Art`, `Neko (Catgirl)`, `50s Infomercial Anime`, `3D/2D Pokemon` |
| 📸 **Fotogerçekçi & Portre** | `Professional Photo`, `Cinematic`, `Casual Photo`, `Realistic humans`, `Realistic images`, `1990s Photo` ... `1920s Photo`, `Realistic Human Generator`, `Cursed Photo` |
| 🌃 **Siberpunk & Sci-Fi** | `Neon Vintage Anime`, `Star Wars Character`, `Star Wars Battle`, `Webcore`, `Futuristic Mecha` |
| 🧙‍♂️ **Fantastik & RPG** | `League of Legends`, `Fantasy Painting`, `Fantasy Landscape`, `Fantasy Portrait`, `Medieval`, `MTG Card`, `Final Fantasy`, `Fantasy World Map`, `Fantasy City Map` |
| 🎨 **3D & Çizgi Dizi** | `3D Disney Character`, `2D Disney Character`, `Disney Sketch`, `3D Emoji`, `Cute Figurine`, `Claymation`, `3D Isometric Icon`, `Lego`, `Cartoon` |
| 👾 **Pixel & Retro** | `Pixel Art (16-bit)`, `Terraria`, `Undertale?`, `50s Enamel Sign`, `Vintage Comic`, `90s Comic` |
| 🖼️ **Klasik Sanat & Yağlı Boya** | `Oil Painting`, `Oil Painting - Realism`, `Oil Painting - Old`, `Painterly`, `Watercolor`, `Traditional Japanese (Ukiyo-e)`, `Nihonga Painting`, `Crayon Drawing`, `Pencil` |

---

## 🐍 Python SDK ile Kullanım

[`sdk.py`](file:///c:/Users/keke/Desktop/projeler/apitest/sdk.py) dosyasını projelerinize dahil ederek 2 satırda görsel üretebilirsiniz:

```python
from sdk import ImageClient

client = ImageClient(base_url="http://localhost:5000")

# 1. Görsel Üret
image = client.generate(
    prompt="cyberpunk rogue samurai with neon plasma katana",
    style="Painted Anime Plus",
    shape="768x512",
    provider="perchance"
)

# 2. Kaydet
image.save("samurai.png")
print(f"Görsel URL: {image.url} ({image.size_kb} KB)")
```

---

## 💻 Komut Satırı (CLI) Kullanımı

```bash
# 1. Desteklenen tüm stilleri ve kategorileri listele:
python cli.py --categories

# 2. Perchance ile 16:9 geniş formatta anime üret:
python cli.py --prompt "anime rogue with neon green hair" --style "Painted Anime Plus" --shape 768x512 --provider perchance

# 3. Stable Horde SDXL ile fotogerçekçi portre üret:
python cli.py --prompt "studio portrait of a cyberpunk hacker" --category photorealistic --provider horde

# 4. Galerideki görselleri listele:
python cli.py --gallery
```

---

## 📁 Proje Dosya Yapısı

```
imageapi/
├── app.py                # Flask REST API Sunucusu + Minimalist Web Studio
├── categories.py         # 100+ Perchance stili, kategori taksonomisi & prompt motoru
├── core_engine.py        # Perchance, Stable Horde ve Pollinations birleşik motoru
├── sdk.py                # Python Client SDK kütüphanesi
├── cli.py                # Komut satırı (Terminal) aracı
├── perchance_service.py  # Bağımsız Perchance stealth API servisi
├── horde_api.py          # Bağımsız Stable Horde SDXL servisi
├── pollinations_api.py   # Bağımsız Pollinations servisi
├── gallery/              # Üretilen görsellerin kaydedildiği galeri dizini
├── requirements.txt      # Python bağımlılıkları
├── .gitignore            # Git filtre kuralları
└── README.md             # Kapsamlı dokümantasyon
```

---

## 📄 Lisans
Bu proje MIT lisansı altında geliştirilmiştir.
