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
  <title>OmniArt AI Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090a0f;
      --card-bg: rgba(16, 18, 27, 0.75);
      --input-bg: rgba(24, 28, 42, 0.6);
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --primary-glow: rgba(99, 102, 241, 0.25);
      --accent: #22d3ee;
      --text: #f8fafc;
      --text-muted: #64748b;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(99, 102, 241, 0.5);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: radial-gradient(circle at 50% 0%, #151828 0%, var(--bg) 80%);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding: 24px 16px;
      -webkit-font-smoothing: antialiased;
    }
    .container { max-width: 1140px; margin: 0 auto; }
    
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 20px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.5px;
      color: #fff;
    }
    .brand-badge {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 20px;
      background: rgba(99, 102, 241, 0.15);
      color: var(--accent);
      border: 1px solid rgba(34, 211, 238, 0.2);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 8px #10b981;
      display: inline-block;
      margin-right: 6px;
    }
    .status-text { font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; }

    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    @media (max-width: 880px) { .grid { grid-template-columns: 1fr; } }

    .card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }

    /* Kategori Hapları */
    .category-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 18px;
    }
    .chip {
      background: var(--input-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 7px 12px;
      border-radius: 10px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 6px;
      user-select: none;
    }
    .chip:hover { color: #fff; border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.05); }
    .chip.active {
      background: var(--primary);
      color: #fff;
      font-weight: 600;
      border-color: var(--primary);
      box-shadow: 0 0 12px var(--primary-glow);
    }

    .form-group { margin-bottom: 14px; }
    label {
      display: block;
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    
    textarea, select {
      width: 100%;
      background: var(--input-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      color: #fff;
      font-size: 0.9rem;
      font-family: inherit;
      transition: all 0.15s ease;
    }
    textarea:focus, select:focus {
      outline: none;
      border-color: var(--border-focus);
      background: rgba(24, 28, 42, 0.9);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    textarea { resize: vertical; min-height: 105px; line-height: 1.45; }
    
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

    .btn-generate {
      width: 100%;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
      color: #fff;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 12px;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 4px 16px var(--primary-glow);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-top: 14px;
    }
    .btn-generate:hover { transform: translateY(-1px); box-shadow: 0 6px 20px var(--primary-glow); }
    .btn-generate:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

    /* Önizleme */
    .preview-box {
      width: 100%;
      min-height: 380px;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--border);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      position: relative;
    }
    .preview-box img { width: 100%; height: 100%; object-fit: contain; border-radius: 10px; }
    .spinner {
      display: none;
      width: 36px;
      height: 36px;
      border: 3px solid rgba(255, 255, 255, 0.1);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .preview-meta {
      display: none;
      align-items: center;
      justify-content: space-between;
      margin-top: 12px;
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    .download-btn {
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .download-btn:hover { text-decoration: underline; }

    /* Galeri */
    .section-title {
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }
    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 12px;
    }
    .gallery-item {
      border-radius: 8px;
      overflow: hidden;
      aspect-ratio: 16/9;
      border: 1px solid var(--border);
      background: #000;
    }
    .gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s; }
    .gallery-item:hover img { transform: scale(1.04); }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <span>⚡ OmniArt AI</span>
        <span class="brand-badge">v1.0</span>
      </div>
      <div class="status-text">
        <span class="status-dot"></span> API Hazır
      </div>
    </header>

    <div class="grid">
      <!-- SOL: KONTROL PANELİ -->
      <div class="card">
        <div class="category-chips" id="catTabs"></div>

        <div class="row">
          <div class="form-group">
            <label for="styleSelect">Stil</label>
            <select id="styleSelect"></select>
          </div>
          <div class="form-group">
            <label for="providerSelect">Motor</label>
            <select id="providerSelect">
              <option value="auto">Otomatik</option>
              <option value="perchance">Perchance</option>
              <option value="horde">Stable Horde (SDXL)</option>
              <option value="pollinations">Pollinations</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="prompt">Prompt</label>
          <textarea id="prompt" placeholder="Görsel tarifini yazın..."></textarea>
        </div>

        <div class="row">
          <div class="form-group">
            <label for="shape">Boyut / Oran</label>
            <select id="shape">
              <option value="landscape">16:9 Geniş</option>
              <option value="square">1:1 Kare</option>
              <option value="portrait">9:16 Dikey</option>
            </select>
          </div>
          <div>
            <button id="genBtn" class="btn-generate" onclick="startGeneration()">
              <span>Görsel Üret</span>
            </button>
          </div>
        </div>
      </div>

      <!-- SAĞ: ÖNİZLEME -->
      <div class="card">
        <div class="preview-box" id="previewBox">
          <div class="spinner" id="spinner"></div>
          <p id="placeholderText" style="color:var(--text-muted); font-size:0.85rem;">Önizleme alanı</p>
          <img id="resultImg" style="display:none;" alt="Sonuç">
        </div>
        
        <div class="preview-meta" id="metaInfo">
          <span id="infoBadge">--</span>
          <a id="downloadLink" class="download-btn" href="#" download="image.png">İndir ↓</a>
        </div>
      </div>
    </div>

    <!-- ALT: GALERİ -->
    <div class="card" style="margin-top:24px;">
      <div class="section-title">Galeri</div>
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
        btn.className = 'chip' + (idx === 0 ? ' active' : '');
        btn.innerHTML = `${cat.icon} ${cat.name.split(' ')[0]}`;
        btn.onclick = () => selectCategory(catKey, btn);
        tabsEl.appendChild(btn);
      });

      selectCategory('anime', document.querySelector('.chip'));
      loadGallery();
    }

    function selectCategory(catKey, btnEl) {
      currentCategory = catKey;
      document.querySelectorAll('.chip').forEach(b => b.classList.remove('active'));
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
      if (!prompt) return alert('Lütfen prompt girin.');

      const style = document.getElementById('styleSelect').value;
      const provider = document.getElementById('providerSelect').value;
      const shape = document.getElementById('shape').value;
      const btn = document.getElementById('genBtn');
      const spinner = document.getElementById('spinner');
      const placeholder = document.getElementById('placeholderText');
      const resultImg = document.getElementById('resultImg');
      const metaInfo = document.getElementById('metaInfo');

      btn.disabled = true;
      btn.innerHTML = '<span>Üretiliyor...</span>';
      spinner.style.display = 'block';
      placeholder.style.display = 'block';
      placeholder.innerText = 'Görsel oluşturuluyor...';
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

          metaInfo.style.display = 'flex';
          document.getElementById('infoBadge').innerText = `${data.provider.toUpperCase()} • ${data.elapsed_seconds}s • ${data.size_kb} KB`;
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
        btn.innerHTML = '<span>Görsel Üret</span>';
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
