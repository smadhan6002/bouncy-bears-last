import os
import shutil
import base64
import io
from PIL import Image
import numpy as np
from scipy import ndimage

def generate():
    src_path = 'assets/LOGO.jpeg'
    im = Image.open(src_path)

    # 1. Perfect square crop centered around logo
    # Content bounding box: x: 278..957 (center 617.5), y: 240..992 (center 616)
    # Using 836 x 836 crop box centered at (617.5, 616)
    box = (200, 198, 1036, 1034)
    cropped_opaque = im.crop(box)

    # 2. Transparent master image
    cropped_rgba = cropped_opaque.convert('RGBA')
    arr = np.array(cropped_rgba)
    diff = np.sqrt(np.sum((arr[:, :, :3].astype(float) - 255)**2, axis=2))
    is_white = diff < 18
    labeled, _ = ndimage.label(is_white)
    bg_label = labeled[0, 0]
    bg_mask = (labeled == bg_label)
    arr[bg_mask, 3] = 0
    master_trans = Image.fromarray(arr)

    # 3. Opaque master image for Apple Touch Icon (per Apple HIG)
    master_opaque = cropped_opaque.convert('RGB')

    # 4. Generate resolutions
    img_16 = master_trans.resize((16, 16), Image.Resampling.LANCZOS)
    img_32 = master_trans.resize((32, 32), Image.Resampling.LANCZOS)
    img_48 = master_trans.resize((48, 48), Image.Resampling.LANCZOS)
    img_192 = master_trans.resize((192, 192), Image.Resampling.LANCZOS)
    img_512 = master_trans.resize((512, 512), Image.Resampling.LANCZOS)
    img_apple = master_opaque.resize((180, 180), Image.Resampling.LANCZOS)

    # 5. Save all image assets to root
    img_16.save('favicon-16x16.png')
    img_32.save('favicon-32x32.png')
    img_48.save('favicon-48x48.png')
    img_192.save('android-chrome-192x192.png')
    img_512.save('android-chrome-512x512.png')
    img_apple.save('apple-touch-icon.png')

    # Multi-resolution ICO: 16x16, 32x32, 48x48 (Google Favicon 48px compliant)
    master_trans.save('favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])

    # SVG Favicon embedding 512x512 PNG
    buf = io.BytesIO()
    img_512.save(buf, format='PNG')
    b64_data = base64.b64encode(buf.getvalue()).decode('ascii')
    svg_data = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <image href="data:image/png;base64,{b64_data}" x="0" y="0" width="512" height="512" />
</svg>
'''
    with open('favicon.svg', 'w', encoding='utf-8') as f:
        f.write(svg_data)

    # 6. Copy to public/ directory for standard structure
    os.makedirs('public', exist_ok=True)
    generated_files = [
        'favicon.ico',
        'favicon.svg',
        'favicon-16x16.png',
        'favicon-32x32.png',
        'favicon-48x48.png',
        'apple-touch-icon.png',
        'android-chrome-192x192.png',
        'android-chrome-512x512.png'
    ]
    for fn in generated_files:
        shutil.copy2(fn, os.path.join('public', fn))
        shutil.copy2(fn, os.path.join('assets', fn))

    print('Favicon generation completed successfully.')

if __name__ == '__main__':
    generate()
