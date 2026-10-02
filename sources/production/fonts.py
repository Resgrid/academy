"""Use installed fonts for media rendering on macOS, Linux or Windows."""
import os
from pathlib import Path
from PIL import ImageFont


def font(size, bold=False):
    override = os.environ.get('ACADEMY_FONT_BOLD' if bold else 'ACADEMY_FONT_REGULAR')
    candidates = [override] if override else []
    candidates += ['/System/Library/Fonts/Supplemental/' + ('Arial Bold.ttf' if bold else 'Arial.ttf'),
                   '/usr/share/fonts/truetype/dejavu/' + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),
                   'C:/Windows/Fonts/' + ('arialbd.ttf' if bold else 'arial.ttf'),
                   'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf']
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    raise ValueError('Install Arial or DejaVu Sans, or set ACADEMY_FONT_REGULAR and ACADEMY_FONT_BOLD to installed font paths.')
