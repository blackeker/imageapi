"""
AI Image Generation - Kategori, Stil ve Boyut Yönetim Modülü
============================================================
Kullanıcının seçtiği kategoriye, Perchance stiline ve boyutuna göre
prompt optimizasyonu ve yönlendirme yapar.
"""

# -------------------------------------------------------------
# PERCHANCE TAM STİL LİSTESİ (100+ Stil)
# -------------------------------------------------------------
PERCHANCE_ALL_STYLES = [
    {"key": "Painted Anime Plus", "name": "Painted Anime Plus", "category": "anime"},
    {"key": "Painted Anime", "name": "Painted Anime", "category": "anime"},
    {"key": "Casual Photo", "name": "Casual Photo", "category": "photorealistic"},
    {"key": "Cinematic", "name": "Cinematic", "category": "photorealistic"},
    {"key": "Digital Painting", "name": "Digital Painting", "category": "digital_art"},
    {"key": "Realistic images", "name": "Realistic images", "category": "photorealistic"},
    {"key": "Realistic humans", "name": "Realistic humans", "category": "photorealistic"},
    {"key": "No style", "name": "No style (Raw Prompt)", "category": "anime"},
    {"key": "Anti-NSFW", "name": "Anti-NSFW", "category": "anime"},
    {"key": "League of Legends", "name": "League of Legends Art", "category": "fantasy"},
    {"key": "Concept Art", "name": "Concept Art", "category": "digital_art"},
    {"key": "3D Disney Character", "name": "3D Disney Character", "category": "digital_art"},
    {"key": "2D Disney Character", "name": "2D Disney Character", "category": "digital_art"},
    {"key": "Disney Sketch", "name": "Disney Sketch", "category": "digital_art"},
    {"key": "Concept Sketch", "name": "Concept Sketch", "category": "digital_art"},
    {"key": "Painterly", "name": "Painterly", "category": "oil_painting"},
    {"key": "Oil Painting", "name": "Oil Painting", "category": "oil_painting"},
    {"key": "Oil Painting - Realism", "name": "Oil Painting - Realism", "category": "oil_painting"},
    {"key": "Oil Painting - Old", "name": "Oil Painting - Old Classical", "category": "oil_painting"},
    {"key": "Professional Photo", "name": "Professional Photo (Studio)", "category": "photorealistic"},
    {"key": "Anime", "name": "Anime (Classic)", "category": "anime"},
    {"key": "Drawn Anime", "name": "Drawn Anime", "category": "anime"},
    {"key": "Cute Anime", "name": "Cute Anime (Moe)", "category": "anime"},
    {"key": "Soft Anime", "name": "Soft Anime", "category": "anime"},
    {"key": "Mix Anime", "name": "Mix Anime", "category": "anime"},
    {"key": "Fantasy Painting", "name": "Fantasy Painting", "category": "fantasy"},
    {"key": "Fantasy Landscape", "name": "Fantasy Landscape", "category": "fantasy"},
    {"key": "Fantasy Portrait", "name": "Fantasy Portrait", "category": "fantasy"},
    {"key": "Studio Ghibli", "name": "Studio Ghibli", "category": "anime"},
    {"key": "50s Enamel Sign", "name": "50s Enamel Sign", "category": "pixel_art"},
    {"key": "Vintage Comic", "name": "Vintage Comic", "category": "digital_art"},
    {"key": "Franco-Belgian Comic", "name": "Franco-Belgian Comic", "category": "digital_art"},
    {"key": "Tintin Comic", "name": "Tintin Comic", "category": "digital_art"},
    {"key": "90s Comic", "name": "90s Comic", "category": "digital_art"},
    {"key": "90s Superhero", "name": "90s Superhero", "category": "digital_art"},
    {"key": "Medieval", "name": "Medieval Art", "category": "fantasy"},
    {"key": "Pixel Art", "name": "Pixel Art (16-bit)", "category": "pixel_art"},
    {"key": "Cute Figurine", "name": "Cute Figurine (Nendoroid/Clay)", "category": "digital_art"},
    {"key": "3D Emoji", "name": "3D Emoji", "category": "digital_art"},
    {"key": "Illustration", "name": "Illustration", "category": "digital_art"},
    {"key": "Flat Illustration", "name": "Flat Illustration", "category": "digital_art"},
    {"key": "Watercolor", "name": "Watercolor (Suluboya)", "category": "oil_painting"},
    {"key": "1990s Photo", "name": "1990s Vintage Photo", "category": "photorealistic"},
    {"key": "1980s Photo", "name": "1980s Vintage Photo", "category": "photorealistic"},
    {"key": "1970s Photo", "name": "1970s Vintage Photo", "category": "photorealistic"},
    {"key": "1960s Photo", "name": "1960s Vintage Photo", "category": "photorealistic"},
    {"key": "1950s Photo", "name": "1950s Vintage Photo", "category": "photorealistic"},
    {"key": "1940s Photo", "name": "1940s Vintage Photo", "category": "photorealistic"},
    {"key": "1930s Photo", "name": "1930s Vintage Photo", "category": "photorealistic"},
    {"key": "1920s Photo", "name": "1920s Vintage Photo", "category": "photorealistic"},
    {"key": "Vintage Pulp Art", "name": "Vintage Pulp Art", "category": "digital_art"},
    {"key": "50s Infomercial Anime", "name": "50s Infomercial Anime", "category": "anime"},
    {"key": "3D Pokemon", "name": "3D Pokemon Style", "category": "digital_art"},
    {"key": "Painted Pokemon", "name": "Painted Pokemon Style", "category": "anime"},
    {"key": "2D Pokemon", "name": "2D Pokemon Style", "category": "anime"},
    {"key": "Vintage Anime", "name": "Vintage Anime (80s/90s Cel)", "category": "anime"},
    {"key": "Neon Vintage Anime", "name": "Neon Vintage Anime (Cyberpunk)", "category": "cyberpunk"},
    {"key": "Manga", "name": "Manga (B&W Ink)", "category": "anime"},
    {"key": "Fantasy World Map", "name": "Fantasy World Map", "category": "fantasy"},
    {"key": "Fantasy City Map", "name": "Fantasy City Map", "category": "fantasy"},
    {"key": "Old World Map", "name": "Old World Map", "category": "fantasy"},
    {"key": "3D Isometric Icon", "name": "3D Isometric Icon", "category": "digital_art"},
    {"key": "Flat Style Icon", "name": "Flat Style Icon", "category": "digital_art"},
    {"key": "Flat Style Logo", "name": "Flat Style Logo", "category": "digital_art"},
    {"key": "Game Art Icon", "name": "Game Art Icon", "category": "digital_art"},
    {"key": "Digital Painting Icon", "name": "Digital Painting Icon", "category": "digital_art"},
    {"key": "Concept Art Icon", "name": "Concept Art Icon", "category": "digital_art"},
    {"key": "Cute 3D Icon", "name": "Cute 3D Icon", "category": "digital_art"},
    {"key": "Cute 3D Icon Set", "name": "Cute 3D Icon Set", "category": "digital_art"},
    {"key": "Crayon Drawing", "name": "Crayon Drawing", "category": "oil_painting"},
    {"key": "Pencil", "name": "Pencil Sketch", "category": "digital_art"},
    {"key": "Tattoo Design", "name": "Tattoo Design", "category": "digital_art"},
    {"key": "Waifu", "name": "Waifu Aesthetic", "category": "anime"},
    {"key": "YuGiOh Art", "name": "YuGiOh Art", "category": "anime"},
    {"key": "Traditional Japanese", "name": "Traditional Japanese (Ukiyo-e)", "category": "oil_painting"},
    {"key": "Nihonga Painting", "name": "Nihonga Painting", "category": "oil_painting"},
    {"key": "Claymation", "name": "Claymation", "category": "digital_art"},
    {"key": "Furry - Painted", "name": "Furry - Painted", "category": "digital_art"},
    {"key": "Furry - Drawn", "name": "Furry - Drawn", "category": "digital_art"},
    {"key": "Furry - Cinematic", "name": "Furry - Cinematic", "category": "photorealistic"},
    {"key": "Cartoon", "name": "Cartoon", "category": "digital_art"},
    {"key": "Cursed Photo", "name": "Cursed Photo", "category": "photorealistic"},
    {"key": "Developed by 9gin", "name": "Developed by 9gin", "category": "anime"},
    {"key": "MTG Card", "name": "MTG Card Art", "category": "fantasy"},
    {"key": "Jester", "name": "Jester", "category": "fantasy"},
    {"key": "Ninja", "name": "Ninja", "category": "anime"},
    {"key": "Random Girl 1", "name": "Random Girl 1", "category": "anime"},
    {"key": "Random Girl 2", "name": "Random Girl 2", "category": "anime"},
    {"key": "Lego", "name": "Lego Bricks Style", "category": "digital_art"},
    {"key": "Skittles", "name": "Skittles", "category": "digital_art"},
    {"key": "Webcore", "name": "Webcore", "category": "cyberpunk"},
    {"key": "Terraria", "name": "Terraria (2D Pixel)", "category": "pixel_art"},
    {"key": "Final Fantasy", "name": "Final Fantasy", "category": "fantasy"},
    {"key": "Star Wars Character", "name": "Star Wars Character", "category": "cyberpunk"},
    {"key": "Star Wars Battle", "name": "Star Wars Battle", "category": "cyberpunk"},
    {"key": "Dragonball", "name": "Dragonball", "category": "anime"},
    {"key": "Undertale?", "name": "Undertale?", "category": "pixel_art"},
    {"key": "ENA", "name": "ENA", "category": "digital_art"},
    {"key": "Neko (Catgirl)", "name": "Neko (Catgirl)", "category": "anime"},
    {"key": "American Girl", "name": "American Girl", "category": "photorealistic"},
    {"key": "NSFW - Realistic", "name": "NSFW - Realistic", "category": "photorealistic"},
    {"key": "NSFW - Anime", "name": "NSFW - Anime", "category": "anime"},
    {"key": "NSFW - Realistic (Stronger)", "name": "NSFW - Realistic (Stronger)", "category": "photorealistic"},
    {"key": "NSFW - Anime (Stronger)", "name": "NSFW - Anime (Stronger)", "category": "anime"},
    {"key": "NSFW Painted Anime", "name": "NSFW Painted Anime", "category": "anime"},
    {"key": "Realistic Human Generator", "name": "Realistic Human Generator", "category": "photorealistic"}
]

# -------------------------------------------------------------
# SHAPES / BOYUTLAR
# -------------------------------------------------------------
SHAPES = {
    "768x512": {"value": "768x512", "label": "Landscape (768x512px)", "ratio": "16:9", "width": 768, "height": 512},
    "512x512": {"value": "512x512", "label": "Square (512x512px)", "ratio": "1:1", "width": 512, "height": 512},
    "512x768": {"value": "512x768", "label": "Portrait (512x768px)", "ratio": "9:16", "width": 512, "height": 768}
}

# -------------------------------------------------------------
# KATEGORİ TAKSONOMİSİ
# -------------------------------------------------------------
CATEGORIES = {
    "anime": {
        "name": "Anime & Manga",
        "icon": "🎌",
        "styles": {
            "Painted Anime Plus": {"name": "Painted Anime Plus", "prefix": "masterpiece, best quality, ultra detailed painted anime, crisp lines, vibrant vivid colors, 4k wallpaper"},
            "Painted Anime": {"name": "Painted Anime", "prefix": "painted anime style, artistic brushwork, beautiful anime illustration, high quality"},
            "Studio Ghibli": {"name": "Studio Ghibli", "prefix": "Studio Ghibli style, Hayao Miyazaki aesthetic, hand-drawn anime scenery, soft warm lighting"},
            "Neon Vintage Anime": {"name": "Neon Vintage Anime", "prefix": "neon vintage 90s anime aesthetic, retro cyberpunk anime, glowing neon colors, cel shaded"},
            "Manga": {"name": "Manga (B&W)", "prefix": "black and white manga drawing, highly detailed ink illustration, screentone shading, dynamic action"},
            "Vintage Anime": {"name": "Vintage Anime (80s/90s)", "prefix": "classic 80s 90s retro anime, vintage cel animation style, nostalgic anime aesthetic"},
            "Cute Anime": {"name": "Cute Anime (Moe)", "prefix": "cute moe anime style, soft pastel colors, big expressive sparkly eyes, adorable aesthetic"},
            "Waifu": {"name": "Waifu Aesthetic", "prefix": "gorgeous waifu, high detailed anime character portrait, stunning beauty, clean lines, 8k wallpaper"}
        },
        "default_models": ["Animagine XL", "AMPonyXL", "Anything v5"]
    },
    "photorealistic": {
        "name": "Fotogerçekçi & Portre",
        "icon": "📸",
        "styles": {
            "Professional Photo": {"name": "Professional Photo (Studio)", "prefix": "raw photo, 8k uhd, studio portrait, shot on 85mm lens, sharp focus, subsurface scattering, award winning photography"},
            "Cinematic": {"name": "Cinematic Film (35mm)", "prefix": "cinematic movie still, 35mm film photography, Kodak Portra 400, dramatic rim lighting, shallow depth of field, IMAX"},
            "Casual Photo": {"name": "Casual Photo (Candid)", "prefix": "candid natural photo, authentic daily atmosphere, realistic human skin texture, unedited raw snapshot"},
            "Realistic humans": {"name": "Realistic humans", "prefix": "photorealistic human portrait, ultra realistic detailed facial features, realistic skin pores, natural light"},
            "1990s Photo": {"name": "1990s Vintage Photo", "prefix": "1990s vintage film photography, 90s aesthetic color grading, subtle film grain, nostalgic"}
        },
        "default_models": ["AlbedoBase XL 3.1", "CyberRealistic Pony", "DreamShaper XL"]
    },
    "cyberpunk": {
        "name": "Siberpunk & Sci-Fi",
        "icon": "🌃",
        "styles": {
            "Neon Vintage Anime": {"name": "Cyberpunk Neon", "prefix": "cyberpunk city, neon soaked streets, rainy reflections, dark techwear aesthetics, glowing holographic interfaces, octane render"},
            "Star Wars Character": {"name": "Sci-Fi Character", "prefix": "futuristic sci-fi warrior, high-tech carbon fiber armor, glowing energy weapons, sci-fi concept art"},
            "Star Wars Battle": {"name": "Epic Space Battle", "prefix": "deep space interstellar starship fleet battle, glowing plasma lasers, colossal dreadnoughts, nebula explosion"}
        },
        "default_models": ["CyberRealistic Pony", "DreamShaper XL", "AlbedoBase XL 3.1"]
    },
    "fantasy": {
        "name": "Fantastik & RPG",
        "icon": "🧙‍♂️",
        "styles": {
            "Fantasy Painting": {"name": "Fantasy Painting", "prefix": "epic high fantasy painting, glowing magical aura, mystical atmosphere, Greg Rutkowski style, highly detailed"},
            "Fantasy Landscape": {"name": "Fantasy Landscape", "prefix": "breathtaking fantasy landscape, ancient gothic castle ruins, colossal floating islands, magical sky"},
            "League of Legends": {"name": "League of Legends Art", "prefix": "League of Legends champion splash art style, dynamic pose, explosive magical VFX, masterpiece"},
            "Medieval": {"name": "Medieval Art", "prefix": "medieval fantasy knight, intricate engraved plate armor, weathered steel, gothic cathedral lighting"}
        },
        "default_models": ["DreamShaper XL", "AlbedoBase XL 3.1", "Animagine XL"]
    },
    "digital_art": {
        "name": "3D Render & Konsept",
        "icon": "🎨",
        "styles": {
            "3D Disney Character": {"name": "3D Pixar / Disney", "prefix": "cute 3d character, Pixar and Disney 3D animation style, smooth clay textures, warm soft studio lighting, Octane Render"},
            "Concept Art": {"name": "Concept Art", "prefix": "trending on Artstation, professional video game concept art, dynamic composition, Unreal Engine 5 cinematic"},
            "3D Isometric Icon": {"name": "3D Isometric Icon", "prefix": "cute 3d isometric icon, miniature diorama, Blender 3d render, soft shadows, vibrant pastel colors"}
        },
        "default_models": ["DreamShaper XL", "AlbedoBase XL 3.1"]
    },
    "pixel_art": {
        "name": "Pixel Art & Retro",
        "icon": "👾",
        "styles": {
            "Pixel Art": {"name": "Pixel Art (16-bit)", "prefix": "16-bit pixel art, detailed pixel sprite, nostalgic retro arcade game aesthetic, clean pixel grid, masterpiece"},
            "Terraria": {"name": "Terraria 2D Pixel", "prefix": "Terraria 2d pixel game style, fantasy retro pixel landscape, vibrant retro sprites"}
        },
        "default_models": ["Anything v5", "DreamShaper XL"]
    },
    "oil_painting": {
        "name": "Yağlı Boya & Sanat",
        "icon": "🖼️",
        "styles": {
            "Oil Painting": {"name": "Oil Painting", "prefix": "classical oil painting on textured canvas, Rembrandt lighting, rich impasto brush strokes, museum fine art"},
            "Watercolor": {"name": "Watercolor (Suluboya)", "prefix": "delicate watercolor painting, soft pigment bleeds on textured paper, flowing pastel colors, elegant loose brushwork"},
            "Traditional Japanese": {"name": "Traditional Japanese (Ukiyo-e)", "prefix": "traditional Japanese Ukiyo-e woodblock print style, Hokusai aesthetic, elegant linework, gold foil textures"}
        },
        "default_models": ["DreamShaper XL", "AlbedoBase XL 3.1"]
    }
}

import urllib.parse
import json
import re
import requests

def translate_to_english(text: str) -> str:
    """Türkçe veya diğer dillerdeki promptları ücretsiz olarak İngilizceye çevirir."""
    if not text or not isinstance(text, str):
        return text
    
    clean_text = text.strip()
    if not clean_text:
        return clean_text
        
    # 1. MyMemory Çeviri Servisi
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(clean_text)}&langpair=tr|en"
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            translated = res.json().get("responseData", {}).get("translatedText")
            if translated and "quota exceeded" not in translated.lower() and "invalid" not in translated.lower():
                return translated.strip()
    except Exception:
        pass

    # 2. Google Translate Web Motoru
    try:
        url = f"https://translate.google.com/m?sl=auto&tl=en&q={urllib.parse.quote(clean_text)}"
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"})
        if res.status_code == 200:
            m = re.search(r'<div class="result-container">([^<]+)</div>', res.text)
            if m:
                return m.group(1).replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'").strip()
    except Exception:
        pass

    return clean_text

def enhance_prompt_with_category(
    user_prompt: str,
    category: str = "anime",
    style: str = None
) -> tuple:
    """
    Kullanıcının prompt'unu otomatik İngilizceye çevirir ve seçilen kategori/stile göre optimize eder.
    Dönüş: (zenginleştirilmiş_prompt, negatif_prompt, önerilen_modeller)
    """
    # Otomatik Çeviri
    en_prompt = translate_to_english(user_prompt)

    cat_data = CATEGORIES.get(category.lower(), CATEGORIES["anime"])
    styles = cat_data.get("styles", {})

    prefix = ""
    if style:
        # Önce kategorideki stillere bak
        if style in styles:
            prefix = styles[style].get("prefix", "")
        else:
            # Genel Perchance stillerinden ara
            matched = next((s for s in PERCHANCE_ALL_STYLES if s["key"].lower() == style.lower() or s["name"].lower() == style.lower()), None)
            if matched:
                prefix = f"{matched['key']} style, high quality"

    if not prefix and styles:
        first_style = list(styles.values())[0]
        prefix = first_style.get("prefix", "")

    neg = "lowres, bad anatomy, bad hands, blurry, low quality, artifacts, watermark"
    models = cat_data.get("default_models", ["Animagine XL", "DreamShaper XL"])

    final_prompt = f"{prefix}, {en_prompt}" if prefix else en_prompt
    return final_prompt, neg, models

def get_all_categories_summary() -> dict:
    """API endpoint'i için kategorileri, stilleri ve Perchance stillerini döndürür."""
    summary = {
        "categories": {},
        "perchance_all_styles": [s["key"] for s in PERCHANCE_ALL_STYLES],
        "shapes": SHAPES
    }
    for cat_id, cat_info in CATEGORIES.items():
        summary["categories"][cat_id] = {
            "name": cat_info["name"],
            "icon": cat_info["icon"],
            "styles": {
                s_id: (s_info["name"] if isinstance(s_info, dict) else s_info)
                for s_id, s_info in cat_info["styles"].items()
            }
        }
    return summary
