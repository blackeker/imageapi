"""
Tam Kapsamlı Çoklu Kategori AI Image Studio & REST API Sunucusu
==============================================================
Kategoriler: Anime, Fotogerçekçi (Portre), Cyberpunk, Fantastik, 3D Render, Pixel Art, Yağlı Boya
Motorlar: Perchance, Stable Horde, Pollinations
Port: 5000
"""

import os
import sys
import io
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string, send_from_directory

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from core_engine import generate, OUTPUT_DIR
from categories import CATEGORIES, get_all_categories_summary

app = Flask(__name__)

# -------------------------------------------------------------
# DİNAMİK ÇOKLU KATEGORİ WEB DASHBOARD (HTML / CSS / JS)
# -------------------------------------------------------------
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚡ Multi-Category AI Image Studio & API</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0e14;
      --card-bg: rgba(18, 24, 38, 0.85);
      --primary: #00ff88;
      --primary-glow: rgba(0, 255, 136, 0.35);
      --accent: #ff0055;
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --border: rgba(255, 255, 255, 0.1);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: radial-gradient(circle at top, #131b2e 0%, var(--bg) 100%);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      padding: 30px 20px;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 30px; }
    h1 {
      font-family: 'Orbitron', sans-serif;
      font-size: 2.2rem;
      color: #fff;
      text-shadow: 0 0 20px var(--primary-glow);
      letter-spacing: 2px;
      margin-bottom: 8px;
    }
    h1 span { color: var(--primary); }
    .subtitle { color: var(--text-muted); font-size: 0.95rem; }
    
    .grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 25px; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
    
    .card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .card-title {
      font-family: 'Orbitron', sans-serif;
      font-size: 1.1rem;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--primary);
    }
    
    .category-tabs {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 8px;
      margin-bottom: 20px;
    }
    .cat-btn {
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 10px 8px;
      border-radius: 8px;
      font-size: 0.85rem;
      cursor: pointer;
      text-align: center;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }
    .cat-btn span { font-size: 1.2rem; }
    .cat-btn:hover { background: rgba(0,255,136,0.1); color: #fff; border-color: var(--primary); }
    .cat-btn.active {
      background: var(--primary);
      color: #000;
      font-weight: 700;
      border-color: var(--primary);
      box-shadow: 0 0 15px var(--primary-glow);
    }
    
    label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
    textarea, select, input {
      width: 100%;
      background: rgba(10, 14, 23, 0.8);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      color: #fff;
      font-size: 0.95rem;
      font-family: inherit;
      margin-bottom: 16px;
      transition: all 0.2s;
    }
    textarea:focus, select:focus, input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 12px var(--primary-glow);
    }
    textarea { resize: vertical; min-height: 110px; }
    
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    
    .btn-generate {
      width: 100%;
      background: linear-gradient(135deg, var(--primary) 0%, #00cc6a 100%);
      color: #000;
      font-family: 'Orbitron', sans-serif;
      font-weight: 700;
      font-size: 1rem;
      padding: 15px;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 4px 15px var(--primary-glow);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }
    .btn-generate:hover { transform: translateY(-2px); box-shadow: 0 6px 25px var(--primary-glow); }
    .btn-generate:disabled { background: #334155; color: #64748b; cursor: not-allowed; box-shadow: none; }
    
    .preview-box {
      width: 100%;
      min-height: 420px;
      background: rgba(0, 0, 0, 0.4);
      border: 2px dashed var(--border);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      position: relative;
    }
    .preview-box img { width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }
    .spinner {
      display: none;
      width: 48px;
      height: 48px;
      border: 4px solid rgba(0, 255, 136, 0.2);
      border-left-color: var(--primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 12px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 15px;
      margin-top: 15px;
    }
    .gallery-item {
      position: relative;
      border-radius: 8px;
      overflow: hidden;
      aspect-ratio: 16/9;
      border: 1px solid var(--border);
    }
    .gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s; }
    .gallery-item:hover img { transform: scale(1.05); }
    
    .api-badge {
      display: inline-block;
      background: rgba(0,255,136,0.15);
      color: var(--primary);
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-family: monospace;
      margin-right: 8px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>⚡ <span>MULTI-CATEGORY</span> AI STUDIO</h1>
      <p class="subtitle">Anime, Fotogerçekçi, Cyberpunk, Fantastik, 3D Render & Yağlı Boya API</p>
    </header>

    <div class="grid">
      <!-- SOL: GİRİŞ PANELİ -->
      <div class="card">
        <div class="card-title">🎭 Kategori Seçimi</div>
        
        <div class="category-tabs" id="catTabs">
          <!-- JS ile doldurulacak -->
        </div>

        <div class="row">
          <div>
            <label for="styleSelect">Alt Stil / Tarz</label>
            <select id="styleSelect" onchange="onStyleChanged()"></select>
          </div>
          <div>
            <label for="providerSelect">AI Motoru</label>
            <select id="providerSelect">
              <option value="auto">✨ Otomatik (Kategoriye En Uygun)</option>
              <option value="perchance">Perchance (Ultra Keskin Anime)</option>
              <option value="horde">Stable Horde (SDXL / Pony)</option>
              <option value="pollinations">Pollinations (Hızlı Test)</option>
            </select>
          </div>
        </div>

        <label for="prompt">Prompt (Açıklama)</label>
        <textarea id="prompt" placeholder="Görsel tarifinizi buraya yazın..."></textarea>

        <div class="row">
          <div>
            <label for="shape">Görsel Formatı</label>
            <select id="shape">
              <option value="landscape">16:9 Landscape (Geniş Ekran)</option>
              <option value="square">1:1 Square (Kare Profil)</option>
              <option value="portrait">9:16 Portrait (Dikey Telefon)</option>
            </select>
          </div>
          <div style="display:flex; align-items:flex-end;">
            <button id="genBtn" class="btn-generate" onclick="startGeneration()">
              <span>✨ GÖRSELİ ÜRET</span>
            </button>
          </div>
        </div>
      </div>

      <!-- SAĞ: ÖNİZLEME PANELİ -->
      <div class="card">
        <div class="card-title">🖼️ Canlı Önizleme & Çıktı</div>
        <div class="preview-box" id="previewBox">
          <div class="spinner" id="spinner"></div>
          <p id="placeholderText" style="color:var(--text-muted); font-size:0.9rem;">Henüz bir görsel üretilmedi.</p>
          <img id="resultImg" style="display:none;" alt="Generated Result">
        </div>
        
        <div id="metaInfo" style="margin-top:15px; font-size:0.85rem; color:var(--text-muted); display:none;">
          <span class="api-badge" id="modelBadge">Sağlayıcı: Auto</span>
          <span id="elapsedBadge">Süre: --s</span>
          <a id="downloadLink" href="#" download="generated_image.png" style="float:right; color:var(--primary); text-decoration:none; font-weight:600;">⬇️ İndir</a>
        </div>
      </div>
    </div>

    <!-- ALT: GALERİ -->
    <div class="card" style="margin-top:25px;">
      <div class="card-title">📚 Üretilenler Galerisi</div>
      <div class="gallery-grid" id="galleryGrid"></div>
    </div>
  </div>

  <script>
    let CATEGORIES_DATA = {};
    let currentCategory = "anime";

    const PROMPT_DEFAULTS = {
      anime: '16:9 dynamic anime rogue, spiky neon-lime hair highlights, amber eyes, cyber visor, dark charcoal techwear parka with bold "KEKE" print, green plasma blade held reverse-grip, pitch black background, 4k wallpaper',
      photorealistic: 'portrait of a young warrior woman, intense amber eyes, studio cinematic rim lighting, 85mm lens, high detailed skin texture, raw photo, 8k',
      cyberpunk: 'futuristic cyberpunk city at rainy night, flying vehicles, neon reflections on asphalt, massive holographic billboards, octane render, 8k wallpaper',
      fantasy: 'epic armored paladin knight holding a glowing broadsword, standing in front of gothic castle ruins, volumetric lightning, dark fantasy concept art',
      digital_art: 'cute 3d robot explorer holding a glowing crystal, Pixar and Disney 3D style, warm soft lighting, vibrant colors, rendered in Octane Render',
      pixel_art: '16-bit pixel art of a cyberpunk samurai warrior on a rainy neon rooftop, retro arcade game aesthetic',
      oil_painting: 'dramatic classical oil painting of a medieval warrior, Rembrandt lighting, rich canvas texture, museum fine art'
    };

    async function init() {
      const res = await fetch('/api/v1/categories');
      CATEGORIES_DATA = await res.json();
      
      const tabsEl = document.getElementById('catTabs');
      tabsEl.innerHTML = '';
      
      Object.keys(CATEGORIES_DATA).forEach((catKey, idx) => {
        const cat = CATEGORIES_DATA[catKey];
        const btn = document.createElement('div');
        btn.className = 'cat-btn' + (idx === 0 ? ' active' : '');
        btn.innerHTML = `<span>${cat.icon}</span>${cat.name.split(' ')[0]}`;
        btn.onclick = () => selectCategory(catKey, btn);
        tabsEl.appendChild(btn);
      });

      selectCategory('anime', document.querySelector('.cat-btn'));
      loadGallery();
    }

    function selectCategory(catKey, btnEl) {
      currentCategory = catKey;
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');

      const styleSel = document.getElementById('styleSelect');
      styleSel.innerHTML = '';
      const styles = CATEGORIES_DATA[catKey].styles || {};
      Object.keys(styles).forEach(sKey => {
        const opt = document.createElement('option');
        opt.value = sKey;
        opt.innerText = styles[sKey];
        styleSel.appendChild(opt);
      });

      document.getElementById('prompt').value = PROMPT_DEFAULTS[catKey] || '';
    }

    function onStyleChanged() {}

    async function loadGallery() {
      try {
        const res = await fetch('/api/v1/gallery');
        const data = await res.json();
        const grid = document.getElementById('galleryGrid');
        grid.innerHTML = '';
        (data.images || []).forEach(img => {
          const item = document.createElement('div');
          item.className = 'gallery-item';
          item.innerHTML = `<a href="${img.url}" target="_blank"><img src="${img.url}" alt="${img.filename}"></a>`;
          grid.appendChild(item);
        });
      } catch(e) {}
    }

    async function startGeneration() {
      const prompt = document.getElementById('prompt').value.trim();
      if (!prompt) return alert('Lütfen bir prompt girin.');

      const style = document.getElementById('styleSelect').value;
      const provider = document.getElementById('providerSelect').value;
      const shape = document.getElementById('shape').value;
      const btn = document.getElementById('genBtn');
      const spinner = document.getElementById('spinner');
      const placeholder = document.getElementById('placeholderText');
      const resultImg = document.getElementById('resultImg');
      const metaInfo = document.getElementById('metaInfo');

      btn.disabled = true;
      btn.innerHTML = '<span>⏳ ÜRETİLİYOR...</span>';
      spinner.style.display = 'block';
      placeholder.style.display = 'block';
      placeholder.innerText = `${currentCategory.toUpperCase()} kategorisinde görsel üretiliyor...`;
      resultImg.style.display = 'none';
      metaInfo.style.display = 'none';

      try {
        const res = await fetch('/api/v1/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt, category: currentCategory, style, provider, shape })
        });

        const data = await res.json();
        if (data.success) {
          resultImg.src = data.url;
          resultImg.style.display = 'block';
          placeholder.style.display = 'none';
          spinner.style.display = 'none';

          metaInfo.style.display = 'block';
          document.getElementById('modelBadge').innerText = `Motor: ${data.provider.toUpperCase()} ${data.model || ''}`;
          document.getElementById('elapsedBadge').innerText = `Süre: ${data.elapsed_seconds}s (${data.size_kb} KB)`;
          document.getElementById('downloadLink').href = data.url;

          loadGallery();
        } else {
          alert('Hata: ' + (data.error || 'Bilinmeyen hata'));
          spinner.style.display = 'none';
          placeholder.innerText = 'Üretim başarısız oldu.';
        }
      } catch(e) {
        alert('Bağlantı hatası: ' + e.message);
        spinner.style.display = 'none';
        placeholder.innerText = 'Hata oluştu.';
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>✨ GÖRSELİ ÜRET</span>';
      }
    }

    window.onload = init;
  </script>
</body>
</html>
"""

# -------------------------------------------------------------
# REST API v1 ENDPOINTS
# -------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/v1/generate", methods=["POST"])
def api_v1_generate():
    data = request.get_json() or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"success": False, "error": "prompt alanı zorunludur"}), 400

    category = data.get("category", "anime")
    style = data.get("style")
    provider = data.get("provider", "auto")
    shape = data.get("shape", "landscape")

    try:
        res = generate(
            prompt=prompt,
            category=category,
            style=style,
            provider=provider,
            shape=shape
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/v1/categories", methods=["GET"])
def api_v1_categories():
    return jsonify(get_all_categories_summary())

@app.route("/api/v1/gallery", methods=["GET"])
def api_v1_gallery():
    files = list(OUTPUT_DIR.glob("*.png"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    items = []
    for f in files[:30]:
        items.append({
            "filename": f.name,
            "url": f"/api/gallery/{f.name}",
            "size_kb": round(f.stat().st_size / 1024, 1)
        })
    return jsonify({"images": items, "count": len(items)})

@app.route("/api/gallery/<filename>", methods=["GET"])
def serve_gallery_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/api/v1/health", methods=["GET"])
def api_v1_health():
    return jsonify({"status": "ok", "service": "Multi-Category AI Image Studio API", "version": "1.0.0"})

if __name__ == "__main__":
    print("=" * 65)
    print("🚀 MULTI-CATEGORY AI IMAGE STUDIO & API SERVER")
    print("=" * 65)
    print("🌐 Web Dashboard:  http://localhost:5000")
    print("⚡ REST API:        POST http://localhost:5000/api/v1/generate")
    print("📚 Kategori API:   GET  http://localhost:5000/api/v1/categories")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5000, debug=False)
