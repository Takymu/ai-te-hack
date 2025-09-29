from __future__ import annotations

import math
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap
def add_speech_bubble(
    image_bytes: bytes,
    text: str,
    head_x: float,
    head_y: float,
    font_path: str = None,
    max_bubble_width: int = 200,
    min_font_size: int = 6
) -> bytes:
    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    draw = ImageDraw.Draw(image)
    
    # Style parameters
    BORDER_COLOR = "black"
    FILL_COLOR = "white"
    BORDER_WIDTH = 3
    TEXT_COLOR = "black"
    
    # Convert float coordinates to int
    head_coords = (int(head_x), int(head_y))
    
    def compute_text_bubble_coords(
        draw: ImageDraw.ImageDraw,
        text: str,
        head_coords: tuple[int, int],
        font_path: str = None,
        max_bubble_width: int = 200,
        min_font_size: int = 6
    ) -> tuple[tuple[int, int, int, int], ImageFont.FreeTypeFont, str]:
        # Calculate font size based on text length
        base_font_size = 40
        scale = 1 / math.sqrt(len(text) / 20 + 1)
        font_size = max(int(base_font_size * scale), min_font_size)
        
        # Safe font
        try:
            font = ImageFont.truetype(font_path or "arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        
        # Wrap text
        max_chars = max(1, int(max_bubble_width / (font_size * 0.6)))
        wrapped_lines = textwrap.wrap(text, width=max_chars)
        wrapped_text = "\n".join(wrapped_lines)
        
        # Calculate text size
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=4)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate bubble rectangle coordinates around the head
        head_x, head_y = head_coords
        margin = 30
        x1 = head_x - text_width // 2 - margin
        y1 = head_y - text_height - 60
        x2 = head_x + text_width // 2 + margin
        y2 = y1 + text_height + margin * 2

        # shift bubble a bit upward to not overlap faces
        y1 -= 80
        y2 -= 80

        # Clamp within image bounds
        img_w, img_h = image.size
        # horizontal clamp
        if x1 < 5:
            dx = 5 - x1
            x1 += dx; x2 += dx
        elif x2 > img_w - 5:
            dx = (img_w - 5) - x2
            x1 += dx; x2 += dx
        # vertical clamp
        if y1 < 5:
            dy = 5 - y1
            y1 += dy; y2 += dy
        elif y2 > img_h - 5:
            dy = (img_h - 5) - y2
            y1 += dy; y2 += dy

        return (x1, y1, x2, y2), font, wrapped_text
    
    def interpolate_point(center, head, ratio=0.7):
        cx, cy = center
        hx, hy = head
        return (int(cx + (hx - cx) * ratio), int(cy + (hy - cy) * ratio))
    
    def scale_polygon(points, scale):
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        return [(int(cx + (x - cx) * scale), int(cy + (y - cy) * scale)) for x, y in points]
    
    def get_ellipse_foci(x1, y1, x2, y2):
        """Return two foci and center of the ellipse defined by bounding box."""
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        a = abs(x2 - x1) / 2
        b = abs(y2 - y1) / 2
        if a >= b:
            c = math.sqrt(max(a * a - b * b, 0))
            return (int(cx - c), cy), (int(cx + c), cy), (cx, cy)
        else:
            c = math.sqrt(max(b * b - a * a, 0))
            return (cx, int(cy - c)), (cx, int(cy + c)), (cx, cy)

    def draw_bubble_with_tail(
        draw,
        ellipse_coords,
        head_coords,
        wrapped_text,
        font,
        BORDER_COLOR="black",
        FILL_COLOR="white",
        BORDER_WIDTH=3,
        TEXT_COLOR="black"
    ):
        # Draw tail
        f1, f2, center = get_ellipse_foci(*ellipse_coords)
        tip = interpolate_point(center, head_coords, ratio=0.7)
        triangle = [f1, f2, tip]
        
        # Draw border (scaled triangle)
        scale_factor = 1 + BORDER_WIDTH / 20.0
        triangle_border = scale_polygon(triangle, scale_factor)
        
        # Draw border (ellipse)
        border_coords = (
            ellipse_coords[0] - BORDER_WIDTH,
            ellipse_coords[1] - BORDER_WIDTH,
            ellipse_coords[2] + BORDER_WIDTH,
            ellipse_coords[3] + BORDER_WIDTH,
        )
        draw.ellipse(border_coords, fill=BORDER_COLOR)
        draw.polygon(triangle_border, fill=BORDER_COLOR)
        
        # Draw white bubble
        # Ensure ellipse coords ordered correctly after clamping
        x1, y1, x2, y2 = ellipse_coords
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        ellipse_coords = (x1, y1, x2, y2)
        draw.ellipse(ellipse_coords, fill=FILL_COLOR)
        draw.polygon(triangle, fill=FILL_COLOR)
        
        # Draw text
        x1, y1, x2, y2 = ellipse_coords
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=4)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        text_x = cx - text_w // 2
        text_y = cy - text_h // 2
        
        draw.multiline_text(
            (text_x, text_y),
            wrapped_text,
            font=font,
            fill=TEXT_COLOR,
            align="center",
            spacing=4
        )
    
    if text.strip():
        rect, font, wrapped_text = compute_text_bubble_coords(
            draw, text, head_coords, font_path, max_bubble_width, min_font_size
        )
        draw_bubble_with_tail(
            draw, rect, head_coords, wrapped_text, font,
            BORDER_COLOR, FILL_COLOR, BORDER_WIDTH, TEXT_COLOR
        )
    
    # Convert result back to bytes
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')
    return output_buffer.getvalue()