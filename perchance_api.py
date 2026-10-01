"""
Perchance AI Image Generator - Resmi Olmayan API Wrapper
========================================================
Bu script, Perchance'ın resmi olmayan Python paketini kullanarak
görsel üretir. DİKKAT: Bu resmi bir API değildir ve her an bozulabilir.

Kurulum: pip install perchance Pillow
"""

import asyncio
from pathlib import Path

try:
    from perchance import ImageGenerator
    from PIL import Image
except ImportError:
    print("Gerekli paketleri yükleyin: pip install perchance Pillow")
    exit(1)


async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    shape: str = "square",
    output_path: str = "output.png",
) -> str:
    """
    Perchance AI ile görsel üretir.

    Args:
        prompt: Görsel açıklaması (İngilizce önerilir)
        negative_prompt: İstenmeyen öğeler
        shape: 'square', 'landscape', veya 'portrait'
        output_path: Çıktı dosya yolu

    Returns:
        Kaydedilen dosyanın yolu
    """
    print(f"🎨 Görsel üretiliyor: '{prompt}'")
    print(f"   Şekil: {shape}")

    async with ImageGenerator() as gen:
        result = await gen.image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            shape=shape,
        )

        binary = await result.download()
        image = Image.open(binary)
        image.save(output_path)
        print(f"✅ Görsel kaydedildi: {output_path}")
        return output_path


async def generate_batch(
    prompts: list[str],
    output_dir: str = "outputs",
    shape: str = "square",
) -> list[str]:
    """
    Birden fazla prompt için toplu görsel üretir.

    Args:
        prompts: Prompt listesi
        output_dir: Çıktı dizini
        shape: Görsel şekli

    Returns:
        Kaydedilen dosya yolları listesi
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    saved_files = []
    async with ImageGenerator() as gen:
        for i, prompt in enumerate(prompts, 1):
            print(f"\n[{i}/{len(prompts)}] Üretiliyor: '{prompt}'")
            try:
                result = await gen.image(prompt=prompt, shape=shape)
                binary = await result.download()
                image = Image.open(binary)

                file_path = output_path / f"image_{i:03d}.png"
                image.save(str(file_path))
                saved_files.append(str(file_path))
                print(f"  ✅ Kaydedildi: {file_path}")
            except Exception as e:
                print(f"  ❌ Hata: {e}")

    return saved_files


# ── Kullanım Örneği ──────────────────────────────────────────────
if __name__ == "__main__":
    # Tek görsel üret
    asyncio.run(
        generate_image(
            prompt="A beautiful sunset over a cyberpunk city, detailed, 4k",
            negative_prompt="blurry, low quality",
            shape="landscape",
            output_path="perchance_output.png",
        )
    )

    # Toplu üretim örneği (yorum kaldırarak kullanın)
    # prompts = [
    #     "A magical forest with glowing mushrooms",
    #     "A robot playing guitar in space",
    #     "An underwater castle with mermaids",
    # ]
    # asyncio.run(generate_batch(prompts, output_dir="batch_outputs"))
