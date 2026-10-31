#!/usr/bin/env python3
"""
CBSE Class 10 English Project Sheet Generator (V6 - Exact Prompt Alignment)
"Bihar and Tripura: A Comparison of Cultural Heritage, Festivals, and Food"

Exact Project Page Mapping:
- PAGE 4: Nalanda Ancient University Ruins
- PAGE 5: Chhath Puja: Prayers to the Sun
- PAGE 6: Traditional Madhubani Painting
- PAGE 7: Traditional Food of Bihar: Thekua & Litti Chokha
- PAGE 8: Tripura Indigenous Tribal Traditional Dress
- PAGE 9: Kharchi Puja: The Fourteen Deities
- PAGE 10: Hojagiri Folk Dance (Reang Community)
- PAGE 11: Unakoti Giant Shiva Rock Relief
- PAGE 12: Traditional Tripuri Cuisine (Mui Borok)
- PAGE 13: Comparison of Festivals: Chhath Puja & Kharchi Puja
- PAGE 14: Comparison of Food: Bihar & Tripura Cuisine
- PAGE 16: Geography: Map of India (Bihar & Tripura)
- PLUS: State Map of Bihar & State Map of Tripura (Pure White Background)

Formatting:
- 12 Maximized 16:9 Photos across 2 Sheets (6 cards per sheet)
- 1 Dedicated State Maps Sheet (Bihar & Tripura)
- Edge-to-Edge width (1220x686 px per photo), virtually NO side bezels
- Faint cutting creases down the center and between rows
- Clean centered headlines, zero cut-line text, zero notes prompts, zero watermarks
- Output: 3 A4 PNGs (300 DPI) and 1 compiled master PDF
"""

import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

PAGE_W = 2480
PAGE_H = 3508

# Edge-to-Edge Margins (No side bezel)
MARGIN_X = 12
COL_GAP = 16

# Maximized 16:9 Photo Dimensions
IMG_W = (PAGE_W - (MARGIN_X * 2) - COL_GAP) // 2  # 1220 px
IMG_H = int(IMG_W * 9 / 16)                        # 686 px (Exact 16:9)

GAP_IMG_TEXT = 12
TEXT_H = 46
CARD_H = IMG_H + GAP_IMG_TEXT + TEXT_H            # 744 px
ROW_GAP = 40

# Colors
COLOR_BG = (255, 255, 255)
COLOR_PHOTO_BORDER = (203, 213, 225)
COLOR_TEXT = (15, 23, 42)
COLOR_CREASE = (226, 232, 240)

def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def ensure_white_bg(img):
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(white_bg, rgba)
        return composite.convert("RGB")
    return img.convert("RGB")

def crop_to_16_9(img, target_w, target_h, focus="center"):
    img = ensure_white_bg(img)
    iw, ih = img.size
    scale = max(target_w / iw, target_h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)

    cx = (nw - target_w) // 2
    if focus == "top":
        cy = max(0, int((nh - target_h) * 0.10))
    elif focus == "bottom":
        cy = max(0, int((nh - target_h) * 0.90))
    else:
        cy = max(0, (nh - target_h) // 2)

    return resized.crop((cx, cy, cx + target_w, cy + target_h))

def render_maximized_card(canvas, x0, y0, img_obj, headline, focus="center", comparison_pair=None):
    draw = ImageDraw.Draw(canvas)
    center_x = x0 + IMG_W // 2

    # Photo Area
    if comparison_pair is None:
        cropped = crop_to_16_9(img_obj, IMG_W, IMG_H, focus=focus)
        canvas.paste(cropped, (x0, y0))
        draw.rectangle([(x0, y0), (x0 + IMG_W, y0 + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)
    else:
        img1, img2, lbl1, lbl2 = img_obj
        half_w = (IMG_W - 8) // 2
        c1 = crop_to_16_9(img1, half_w, IMG_H, focus=focus)
        c2 = crop_to_16_9(img2, half_w, IMG_H, focus=focus)
        canvas.paste(c1, (x0, y0))
        canvas.paste(c2, (x0 + half_w + 8, y0))
        draw.rectangle([(x0, y0), (x0 + half_w, y0 + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)
        draw.rectangle([(x0 + half_w + 8, y0), (x0 + IMG_W, y0 + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)

        font_sub = get_font(20, bold=True)
        h1_cx = x0 + half_w // 2
        lbl1_bbox = draw.textbbox((0, 0), lbl1, font=font_sub)
        lbl1_w = (lbl1_bbox[2] - lbl1_bbox[0]) + 24
        draw.rounded_rectangle([(h1_cx - lbl1_w // 2, y0 + IMG_H - 40), (h1_cx + lbl1_w // 2, y0 + IMG_H - 10)], radius=4, fill=(0, 0, 0))
        draw.text((h1_cx, y0 + IMG_H - 25), lbl1, fill=(255, 255, 255), font=font_sub, anchor="mm")

        h2_cx = x0 + half_w + 8 + half_w // 2
        lbl2_bbox = draw.textbbox((0, 0), lbl2, font=font_sub)
        lbl2_w = (lbl2_bbox[2] - lbl2_bbox[0]) + 24
        draw.rounded_rectangle([(h2_cx - lbl2_w // 2, y0 + IMG_H - 40), (h2_cx + lbl2_w // 2, y0 + IMG_H - 10)], radius=4, fill=(0, 0, 0))
        draw.text((h2_cx, y0 + IMG_H - 25), lbl2, fill=(255, 255, 255), font=font_sub, anchor="mm")

    # Simple Headline - Centered
    text_y = y0 + IMG_H + GAP_IMG_TEXT
    font_head = get_font(28, bold=True)
    draw.text((center_x, text_y), headline, fill=COLOR_TEXT, font=font_head, anchor="mt")

def draw_sheet_cutting_creases(canvas, start_y):
    draw = ImageDraw.Draw(canvas)
    mid_x = MARGIN_X + IMG_W + (COL_GAP // 2)
    grid_total_h = (3 * CARD_H) + (2 * ROW_GAP)
    draw.line([(mid_x, start_y - 20), (mid_x, start_y + grid_total_h + 20)], fill=COLOR_CREASE, width=1)

    r1_crease_y = start_y + CARD_H + (ROW_GAP // 2)
    r2_crease_y = start_y + (2 * CARD_H) + ROW_GAP + (ROW_GAP // 2)
    draw.line([(MARGIN_X, r1_crease_y), (PAGE_W - MARGIN_X, r1_crease_y)], fill=COLOR_CREASE, width=1)
    draw.line([(MARGIN_X, r2_crease_y), (PAGE_W - MARGIN_X, r2_crease_y)], fill=COLOR_CREASE, width=1)

def render_clean_state_map(canvas, x0, y0, box_w, box_h, map_img, headline):
    draw = ImageDraw.Draw(canvas)
    center_x = x0 + box_w // 2
    clean_map = ensure_white_bg(map_img)

    map_area_h = int(box_h * 0.80)
    mw, mh = clean_map.size
    scale = min(box_w / mw, map_area_h / mh)
    rmw = int(mw * scale)
    rmh = int(mh * scale)
    resized_map = clean_map.resize((rmw, rmh), Image.Resampling.LANCZOS)

    mx = x0 + (box_w - rmw) // 2
    my = y0 + (map_area_h - rmh) // 2
    canvas.paste(resized_map, (mx, my))

    title_y = y0 + map_area_h + 20
    font_head = get_font(42, bold=True)
    draw.text((center_x, title_y), headline, fill=COLOR_TEXT, font=font_head, anchor="mt")

def create_blank_sheet():
    return Image.new("RGB", (PAGE_W, PAGE_H), COLOR_BG)

def main():
    print("[*] Generating CBSE Sheets Exactly Matching User Specification...")
    os.makedirs("output_cbse", exist_ok=True)

    assets = {
        "nalanda": "cbse_project_assets/01_Nalanda_University_Ruins_Bihar.jpg",
        "chhath": "cbse_project_assets/03_Chhath_Puja_Celebration_Bihar.jpg",
        "madhubani": "cbse_project_assets/04_Madhubani_Mithila_Folk_Painting_Bihar.jpg",
        "thekua": "cbse_project_assets/05_Traditional_Thekua_Bihar.jpg",
        "litti": "cbse_project_assets/06_Traditional_Litti_Chokha_Bihar.jpg",
        "tripura_dress": "cbse_project_assets/07_Traditional_Tribal_Dress_Tripura.jpg",
        "kharchi_celebration": "cbse_project_assets/08_Kharchi_Puja_Celebration_Tripura.jpg",
        "fourteen_deities": "cbse_project_assets/09_Fourteen_Deities_Chaturdash_Devta_Tripura.jpg",
        "hojagiri": "cbse_project_assets/10_Hojagiri_Folk_Dance_Reang_Tripura.jpg",
        "unakoti": "cbse_project_assets/11_Unakoti_Rock_Reliefs_Shiva_Tripura.jpg",
        "mui_borok": "cbse_project_assets/13_Tripura_Traditional_Food_Mui_Borok.jpg",
        "map_india_combined": "cbse_project_assets/16_Map_India_Bihar_Tripura_Combined.png",
        "map_bihar": "cbse_project_assets/18_State_Map_Bihar_Districts.png",
        "map_tripura": "cbse_project_assets/19_State_Map_Tripura_Districts.png"
    }

    imgs = {}
    for key, path in assets.items():
        if os.path.exists(path):
            imgs[key] = Image.open(path)
        else:
            print(f"[!] Warning: Missing {path}")

    if "map_india_combined" not in imgs:
        if os.path.exists("cbse_project_assets/16_Map_Bihar_in_India.png"):
            imgs["map_india_combined"] = Image.open("cbse_project_assets/16_Map_Bihar_in_India.png")

    c0_x = MARGIN_X
    c1_x = c0_x + IMG_W + COL_GAP

    grid_total_h = (3 * CARD_H) + (2 * ROW_GAP)
    start_y = (PAGE_H - grid_total_h) // 2
    r0_y = start_y
    r1_y = r0_y + CARD_H + ROW_GAP
    r2_y = r1_y + CARD_H + ROW_GAP

    def get_pos(col, row):
        x = c0_x if col == 0 else c1_x
        y = [r0_y, r1_y, r2_y][row]
        return x, y

    # ==================== SHEET 1 (PAGES 4 TO 9) ====================
    print("[*] Rendering Sheet 1 (Pages 4–9)...")
    sheet1 = create_blank_sheet()
    draw_sheet_cutting_creases(sheet1, start_y)

    # Page 4: Nalanda Ruins
    x, y = get_pos(0, 0); render_maximized_card(sheet1, x, y, imgs["nalanda"], "Nalanda Ancient University Ruins")
    # Page 5: Chhath Puja
    x, y = get_pos(1, 0); render_maximized_card(sheet1, x, y, imgs["chhath"], "Chhath Puja: Prayers to the Sun")
    # Page 6: Madhubani Paintings
    x, y = get_pos(0, 1); render_maximized_card(sheet1, x, y, imgs["madhubani"], "Traditional Madhubani Painting")
    # Page 7: Food of Bihar (Thekua & Litti Chokha)
    x, y = get_pos(1, 1); render_maximized_card(sheet1, x, y,
                                               (imgs["thekua"], imgs["litti"], "Thekua", "Litti Chokha"),
                                               "Food of Bihar: Thekua & Litti Chokha", comparison_pair=True)
    # Page 8: Tripura Tribal Traditional Dress
    x, y = get_pos(0, 2); render_maximized_card(sheet1, x, y, imgs["tripura_dress"], "Tripura Indigenous Tribal Traditional Dress", focus="top")
    # Page 9: Kharchi Puja Fourteen Deities
    x, y = get_pos(1, 2); render_maximized_card(sheet1, x, y, imgs["fourteen_deities"], "Kharchi Puja: The Fourteen Deities")

    sheet1.save("output_cbse/Page_1_Core_Topics.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 2 (PAGES 10 TO 16) ====================
    print("[*] Rendering Sheet 2 (Pages 10–16)...")
    sheet2 = create_blank_sheet()
    draw_sheet_cutting_creases(sheet2, start_y)

    # Page 10: Hojagiri Folk Dance
    x, y = get_pos(0, 0); render_maximized_card(sheet2, x, y, imgs["hojagiri"], "Hojagiri Folk Dance (Reang Community)")
    # Page 11: Unakoti Rock Reliefs
    x, y = get_pos(1, 0); render_maximized_card(sheet2, x, y, imgs["unakoti"], "Unakoti Giant Shiva Rock Relief")
    # Page 12: Food of Tripura (Mui Borok)
    x, y = get_pos(0, 1); render_maximized_card(sheet2, x, y, imgs["mui_borok"], "Food of Tripura: Traditional Mui Borok Cuisine")
    # Page 13: Comparison of Festivals
    x, y = get_pos(1, 1); render_maximized_card(sheet2, x, y,
                                               (imgs["chhath"], imgs["kharchi_celebration"], "Chhath Puja (Bihar)", "Kharchi Puja (Tripura)"),
                                               "Comparison of Festivals: Chhath Puja & Kharchi Puja", comparison_pair=True)
    # Page 14: Comparison of Food
    x, y = get_pos(0, 2); render_maximized_card(sheet2, x, y,
                                               (imgs["litti"], imgs["mui_borok"], "Bihar Cuisine", "Tripura Cuisine"),
                                               "Comparison of Food: Bihar & Tripura", comparison_pair=True)
    # Page 16: Geography & History Comparison (Map of India)
    x, y = get_pos(1, 2); render_maximized_card(sheet2, x, y, imgs["map_india_combined"], "Geography: Map of India (Bihar & Tripura Highlighted)")

    sheet2.save("output_cbse/Page_2_Comparisons.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 3: STATE DISTRICT MAPS ====================
    print("[*] Rendering Sheet 3: State District Maps...")
    sheet3 = create_blank_sheet()
    map_box_w = PAGE_W - (MARGIN_X * 2)
    map_box_h = (PAGE_H - 120) // 2

    draw3 = ImageDraw.Draw(sheet3)
    mid_map_y = 50 + map_box_h + 10
    draw3.line([(MARGIN_X, mid_map_y), (PAGE_W - MARGIN_X, mid_map_y)], fill=COLOR_CREASE, width=1)

    render_clean_state_map(sheet3, MARGIN_X, 50, map_box_w, map_box_h, imgs["map_bihar"], "State Map of Bihar")
    render_clean_state_map(sheet3, MARGIN_X, 50 + map_box_h + 20, map_box_w, map_box_h, imgs["map_tripura"], "State Map of Tripura")
    sheet3.save("output_cbse/Page_3_State_Maps.png", "PNG", dpi=(300, 300))

    # ==================== MASTER PDF COMPILATION ====================
    print("[*] Compiling all 3 sheets into high-resolution master PDF...")
    pdf_path = "output_cbse/CBSE_Class10_Bihar_Tripura_Project.pdf"
    sheet1.save(pdf_path, "PDF", resolution=300.0, save_all=True, append_images=[sheet2, sheet3])

    print("\n🎉 SUCCESS! Generated 3 Master Sheets + Master PDF:")
    for f in sorted(os.listdir("output_cbse")):
        sz = os.path.getsize(os.path.join("output_cbse", f)) / (1024 * 1024)
        print(f"  - {f} ({sz:.2f} MB)")

if __name__ == "__main__":
    main()
