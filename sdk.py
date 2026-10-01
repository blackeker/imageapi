"""
Multi-Category AI Image Studio - Python Client SDK
==================================================
Tüm kategorilerde (Anime, Fotogerçekçi, Cyberpunk, Fantastik, 3D, Pixel vb.)
görsel üretmek için Python kütüphanesi.

Kullanım:
  from sdk import ImageClient

  client = ImageClient()

  # 1. Fotogerçekçi Portre
  img = client.generate("young female warrior with amber eyes", category="photorealistic", style="studio_portrait")
  img.save("portrait.png")

  # 2. Cyberpunk Şehir
  img2 = client.generate("flying cars in rainy neon metropolis", category="cyberpunk", style="neon_city")
  img2.save("cyberpunk.png")

  # 3. Anime Duvar Kağıdı
  img3 = client.generate("anime rogue with neon-lime hair, KEKE parka", category="anime", style="cyberpunk_anime")
  img3.save("anime.png")
"""

import os
import requests

class GeneratedImage:
    def __init__(self, data: dict, base_url: str = "http://localhost:5000"):
        self.success = data.get("success", False)
        self.provider = data.get("provider")
        self.filename = data.get("filename")
        self.filepath = data.get("filepath")
        self.url = f"{base_url}{data.get('url')}" if data.get('url') else None
        self.elapsed_seconds = data.get("elapsed_seconds")
        self.size_kb = data.get("size_kb")

    def save(self, destination: str):
        """Görseli yerel diske kaydeder."""
        if self.filepath and os.path.exists(self.filepath):
            with open(self.filepath, "rb") as src, open(destination, "wb") as dst:
                dst.write(src.read())
        elif self.url:
            r = requests.get(self.url)
            if r.status_code == 200:
                with open(destination, "wb") as dst:
                    dst.write(r.content)
        print(f"✅ Görsel kaydedildi: {destination}")

    def __repr__(self):
        return f"<GeneratedImage provider={self.provider} size={self.size_kb}KB elapsed={self.elapsed_seconds}s>"

class ImageClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        prompt: str,
        category: str = "anime",       # 'anime', 'photorealistic', 'cyberpunk', 'fantasy', 'digital_art', 'pixel_art', 'oil_painting'
        style: str = None,             # Alt stil (örn: 'studio_portrait', 'ghibli', 'dark_fantasy')
        provider: str = "auto",        # 'auto', 'perchance', 'horde', 'pollinations'
        shape: str = "landscape"       # 'landscape', 'square', 'portrait'
    ) -> GeneratedImage:
        """
        Kategori ve stil destekli görsel üretim isteği gönderir.
        """
        payload = {
            "prompt": prompt,
            "category": category,
            "style": style,
            "provider": provider,
            "shape": shape
        }
        res = requests.post(f"{self.base_url}/api/v1/generate", json=payload, timeout=180)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                return GeneratedImage(data, base_url=self.base_url)
            else:
                raise Exception(f"Üretim Hatası: {data.get('error')}")
        else:
            raise Exception(f"HTTP {res.status_code}: {res.text}")

    def get_categories(self) -> dict:
        """Tüm mevcut kategorileri ve stilleri döner."""
        res = requests.get(f"{self.base_url}/api/v1/categories")
        return res.json() if res.status_code == 200 else {}

    def get_gallery(self) -> list:
        """Galerideki son üretilen görselleri listeler."""
        res = requests.get(f"{self.base_url}/api/v1/gallery")
        return res.json().get("images", []) if res.status_code == 200 else []
