"""
AI Image Generation - Kategori ve Stil Yönetim Modülü
====================================================
Kullanıcının seçtiği kategoriye göre prompt zenginleştirme,
negatif prompt optimizasyonu ve en uygun model yönlendirmesi yapar.
"""

CATEGORIES = {
    "anime": {
        "name": "Anime & Manga",
        "description": "Japon anime ve manga çizim stilleri",
        "icon": "🎌",
        "styles": {
            "modern_anime": {
                "name": "Modern Anime (Shonen/Seinen)",
                "prompt_prefix": "masterpiece, best quality, modern anime aesthetic, crisp lines, vibrant colors, detailed eyes, 4k anime wallpaper",
                "negative": "lowres, bad anatomy, bad hands, cropped, worst quality, low quality, normal quality, artifacts, blurry, watermark"
            },
            "ghibli": {
                "name": "Studio Ghibli (Klasik El Çizimi)",
                "prompt_prefix": "Studio Ghibli style, Hayao Miyazaki aesthetic, hand-drawn anime, lush painted scenery, soft warm lighting, watercolor textures, nostalgic atmosphere",
                "negative": "3d render, cgi, photorealistic, harsh lighting, bad anatomy, blurry"
            },
            "cyberpunk_anime": {
                "name": "Cyberpunk Anime (Esports / Neon)",
                "prompt_prefix": "cyberpunk anime style, high-energy esports aesthetic, neon lighting, dark techwear, holographic glow, dramatic cinematic contrast, 8k wallpaper",
                "negative": "flat colors, lowres, bad anatomy, blurry, washed out"
            },
            "shinkai": {
                "name": "Makoto Shinkai (Işıltılı & Gökyüzü)",
                "prompt_prefix": "Makoto Shinkai style, Your Name aesthetic, breathtaking hyper-detailed sky, volumetric sun rays, lens flare, emotional lighting, ultra-detailed scenery",
                "negative": "dark, gloomy, bad anatomy, low quality, artifacts"
            }
        },
        "default_models": ["Animagine XL", "AMPonyXL", "Anything v5"]
    },
    "photorealistic": {
        "name": "Fotogerçekçi (Photorealistic & Portrait)",
        "description": "Gerçek stüdyo fotoğrafçılığı, portre ve sinematik çekimler",
        "icon": "📸",
        "styles": {
            "studio_portrait": {
                "name": "Stüdyo Portresi (8K RAW)",
                "prompt_prefix": "raw photo, 8k uhd, studio portrait, shot on 85mm f/1.4 lens, professional lighting, photorealistic skin texture, subsurface scattering, sharp focus, award winning photography",
                "negative": "painting, drawing, illustration, cartoon, anime, 3d render, smooth skin, airbrushed, plastic, bad eyes, bad anatomy"
            },
            "cinematic_movie": {
                "name": "Sinematik Film Sahnesi (35mm)",
                "prompt_prefix": "cinematic movie still, 35mm film photography, Kodak Portra 400, dramatic rim lighting, film grain, shallow depth of field, anamorphic lens flare, IMAX composition",
                "negative": "cartoon, 3d render, anime, amateur, low quality, overexposed, fake"
            },
            "street_photography": {
                "name": "Sokak & Belgesel Fotoğrafı",
                "prompt_prefix": "street photography, candid shot, Leica M6, natural lighting, authentic urban atmosphere, gritty textures, high dynamic range",
                "negative": "staged, plastic, painting, anime, CGI, blurry"
            }
        },
        "default_models": ["AlbedoBase XL 3.1", "CyberRealistic Pony", "DreamShaper XL"]
    },
    "cyberpunk": {
        "name": "Siberpunk & Bilim Kurgu (Sci-Fi)",
        "description": "Geleceğin neon şehirleri, mecha savaşçıları ve siber teknolojiler",
        "icon": "🌃",
        "styles": {
            "neon_city": {
                "name": "Neon Gece Şehri & Techwear",
                "prompt_prefix": "cyberpunk city, neon soaked streets, rainy reflections, dark techwear aesthetics, glowing holographic interfaces, volumetric smog, ray tracing, octane render, 8k",
                "negative": "rustic, medieval, daylight, lowres, blurry, cartoon"
            },
            "mecha": {
                "name": "Mecha & Sibernetik Robot",
                "prompt_prefix": "futuristic mecha robot, complex mechanical parts, carbon fiber and glowing alloy, battle damaged, sci-fi concept art, high precision engineering, Unreal Engine 5",
                "negative": "organic, simple, cartoon, blurry, low poly"
            },
            "space_opera": {
                "name": "Uzay Operası & Galaksi",
                "prompt_prefix": "deep space nebula, colossal starships, cosmic dust, orbital mega-structures, interstellar lighting, cinematic sci-fi wallpaper, 4k",
                "negative": "earth, ground, blurry, low resolution"
            }
        },
        "default_models": ["CyberRealistic Pony", "DreamShaper XL", "AlbedoBase XL 3.1"]
    },
    "fantasy": {
        "name": "Fantastik & RPG",
        "description": "Orta çağ şövalyeleri, büyücüler, mitolojik yaratıklar ve epik kaleler",
        "icon": "🧙‍♂️",
        "styles": {
            "dark_fantasy": {
                "name": "Dark Fantasy (Elden Ring / Souls-like)",
                "prompt_prefix": "dark fantasy concept art, Elden Ring atmosphere, towering gothic ruins, eerie ethereal fog, intricate ornate armor, dramatic moonlight, Greg Rutkowski style, highly detailed",
                "negative": "cheerful, cartoon, modern, neon, flat colors, blurry"
            },
            "high_fantasy": {
                "name": "High Fantasy & Büyü",
                "prompt_prefix": "epic high fantasy, glowing mystical magic runes, enchanted ancient forest, radiant fairy lights, ornate crystal staff, vivid magical aura, digital matte painting",
                "negative": "technology, cars, modern, blurry, bad anatomy"
            },
            "mythical_beast": {
                "name": "Mitolojik Yaratıklar & Ejderhalar",
                "prompt_prefix": "colossal ancient dragon, detailed obsidian scales, glowing fiery breath, dramatic mountain peak setting, storm clouds and lightning, epic digital illustration",
                "negative": "cute, cartoon, flat, bad anatomy"
            }
        },
        "default_models": ["DreamShaper XL", "AlbedoBase XL 3.1", "Animagine XL"]
    },
    "digital_art": {
        "name": "3D Render & Konsept Sanatı",
        "description": "Pixar 3D animasyon, Octane Render ve dijital konsept çizimler",
        "icon": "🎨",
        "styles": {
            "pixar_3d": {
                "name": "3D Animasyon (Pixar / Disney)",
                "prompt_prefix": "cute 3d character, Pixar and Disney animation style, smooth clay textures, warm soft studio lighting, adorable expressive eyes, rendered in Octane Render, 4k",
                "negative": "photorealistic, terrifying, dark, adult, rough textures, blurry"
            },
            "concept_art": {
                "name": "Oyun Konsept Sanatı (Concept Art)",
                "prompt_prefix": "trending on Artstation, professional video game concept art, dynamic composition, dramatic perspective, detailed brush strokes, Unreal Engine 5 cinematic",
                "negative": "amateur, lowres, watermark, text, signature"
            },
            "isometric_3d": {
                "name": "İzometrik 3D Minyatür",
                "prompt_prefix": "isometric 3d diorama, cute miniature environment, Blender 3d render, tilt-shift photography, soft shadows, pastel color palette, clean geometric details",
                "negative": "flat 2d, blurry, realistic human, messy"
            }
        },
        "default_models": ["DreamShaper XL", "AlbedoBase XL 3.1"]
    },
    "pixel_art": {
        "name": "Pixel Art & Retro",
        "description": "16-bit retro oyunlar, pixel art ve nostaljik synthwave",
        "icon": "👾",
        "styles": {
            "16bit_retro": {
                "name": "16-Bit Retro Oyun (SNES / Arcade)",
                "prompt_prefix": "16-bit pixel art, detailed pixel sprite, nostalgic retro arcade game aesthetic, clean pixel grid, vibrant retro color palette, masterpiece pixel artwork",
                "negative": "vector, 3d, smooth, blurry, realistic, anti-aliased"
            },
            "synthwave_80s": {
                "name": "Synthwave / Vaporwave 80s",
                "prompt_prefix": "synthwave 80s retro aesthetic, neon grid horizon, retrofuturistic wireframe sun, chrome reflections, vibrant magenta and cyan glow, vintage VHS effect",
                "negative": "modern, flat, boring, natural daylight, green"
            }
        },
        "default_models": ["Anything v5", "DreamShaper XL"]
    },
    "oil_painting": {
        "name": "Klasik Sanat & Yağlı Boya",
        "description": "Rönesans yağlı boya, suluboya ve empresyonizm",
        "icon": "🖼️",
        "styles": {
            "oil_canvas": {
                "name": "Rönesans Yağlı Boya Tablo",
                "prompt_prefix": "classical oil painting on textured canvas, Rembrandt lighting, rich impasto brush strokes, dramatic chiaroscuro, museum masterpiece, fine art",
                "negative": "digital, 3d render, photo, cartoon, anime, bright neon"
            },
            "watercolor": {
                "name": "Suluboya (Watercolor Art)",
                "prompt_prefix": "delicate watercolor painting, soft pigment bleeds on textured paper, flowing pastel colors, elegant loose brushwork, artistic splash effects",
                "negative": "dark, harsh, 3d, sharp CGI, over-saturated"
            }
        },
        "default_models": ["DreamShaper XL", "AlbedoBase XL 3.1"]
    }
}

def enhance_prompt_with_category(
    user_prompt: str,
    category: str = "anime",
    style: str = None
) -> tuple:
    """
    Kullanıcının prompt'unu seçilen kategori ve stile göre optimize eder.
    Dönüş: (zenginleştirilmiş_prompt, negatif_prompt, önerilen_modeller)
    """
    cat_data = CATEGORIES.get(category.lower(), CATEGORIES["anime"])
    styles = cat_data.get("styles", {})

    if style and style.lower() in styles:
        selected_style = styles[style.lower()]
    else:
        # İlk stili varsayılan al
        selected_style = list(styles.values())[0]

    prefix = selected_style.get("prompt_prefix", "")
    neg = selected_style.get("negative", "lowres, bad anatomy, blurry, worst quality")
    models = cat_data.get("default_models", ["Animagine XL", "DreamShaper XL"])

    # Birleştirilmiş tam prompt
    final_prompt = f"{prefix}, {user_prompt}"

    return final_prompt, neg, models

def get_all_categories_summary() -> dict:
    """API endpoint'i için tüm kategorilerin özetini döndürür."""
    summary = {}
    for cat_id, cat_info in CATEGORIES.items():
        summary[cat_id] = {
            "name": cat_info["name"],
            "description": cat_info["description"],
            "icon": cat_info["icon"],
            "styles": {
                s_id: s_info["name"] for s_id, s_info in cat_info["styles"].items()
            }
        }
    return summary
