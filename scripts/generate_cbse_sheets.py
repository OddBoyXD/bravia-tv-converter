#!/usr/bin/env python3
"""
CBSE Class 10 English Project Sheet Generator (V5 - Edge-to-Edge Maximized 16:9, Crease Guides)
"Bihar and Tripura: A Comparison of Cultural Heritage, Festivals, and Food"

Features:
- Maximized 16:9 photos (1220x686 px) extending edge-to-edge with virtually NO side bezel (MARGIN_X = 12 px)
- Subtle cutting crease guide lines between columns and rows for effortless scissor cutting
- Clean white background guaranteed for all maps (no black/dark transparency artifacts)
- High-resolution Administrative Map of Bihar + Official Tripura District Map
- Authentic HD photography:
  * Tripuri girls in handwoven Rignai & Risa with faces fully in focus
  * Authentic Tripuri Mui Borok Thali
  * Authentic Tripuri Fermented Food (Gudok / Gwdwk made with Berma)
  * Live Kharchi Puja celebration
- Centered simple titles under each photo
- Output: 4 print-ready A4 PNGs (300 DPI) and 1 compiled master PDF
"""

import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

PAGE_W = 2480
PAGE_H = 3508

# Edge-to-Edge Margins (Virtually no side bezel)
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
COLOR_CREASE = (226, 232, 240) # Faint crease cut guide

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
    """Converts any transparent/RGBA image to solid RGB on a pure white background."""
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

    # 1. Photo Area (Exact 16:9 with subtle clean border)
    if comparison_pair is None:
        cropped = crop_to_16_9(img_obj, IMG_W, IMG_H, focus=focus)
        canvas.paste(cropped, (x0, y0))
        draw.rectangle([(x0, y0), (x0 + IMG_W, y0 + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)
    else:
        # Side-by-side comparison inside 16:9 frame
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

    # 2. Simple Headline - Centered in middle
    text_y = y0 + IMG_H + GAP_IMG_TEXT
    font_head = get_font(30, bold=True)
    draw.text((center_x, text_y), headline, fill=COLOR_TEXT, font=font_head, anchor="mt")

def draw_sheet_cutting_creases(canvas, start_y):
    """Draws subtle, clean cutting crease lines down the middle column and between rows."""
    draw = ImageDraw.Draw(canvas)
    
    # Vertical crease down the exact center
    mid_x = MARGIN_X + IMG_W + (COL_GAP // 2)
    grid_total_h = (3 * CARD_H) + (2 * ROW_GAP)
    draw.line([(mid_x, start_y - 20), (mid_x, start_y + grid_total_h + 20)], fill=COLOR_CREASE, width=1)

    # Horizontal creases between rows
    r1_crease_y = start_y + CARD_H + (ROW_GAP // 2)
    r2_crease_y = start_y + (2 * CARD_H) + ROW_GAP + (ROW_GAP // 2)
    draw.line([(MARGIN_X, r1_crease_y), (PAGE_W - MARGIN_X, r1_crease_y)], fill=COLOR_CREASE, width=1)
    draw.line([(MARGIN_X, r2_crease_y), (PAGE_W - MARGIN_X, r2_crease_y)], fill=COLOR_CREASE, width=1)

def render_clean_state_map(canvas, x0, y0, box_w, box_h, map_img, headline):
    draw = ImageDraw.Draw(canvas)
    center_x = x0 + box_w // 2

    # Ensure pure white background
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

    # Centered Title
    title_y = y0 + map_area_h + 20
    font_head = get_font(42, bold=True)
    draw.text((center_x, title_y), headline, fill=COLOR_TEXT, font=font_head, anchor="mt")

def create_blank_sheet():
    return Image.new("RGB", (PAGE_W, PAGE_H), COLOR_BG)

def main():
    print("[*] Generating Edge-to-Edge 16:9 CBSE Sheets & Single PDF...")
    os.makedirs("output_cbse", exist_ok=True)

    assets = {
        "nalanda": "cbse_project_assets/01_Nalanda_University_Ruins_Bihar.jpg",
        "mahabodhi": "cbse_project_assets/02_Mahabodhi_Temple_Bodh_Gaya_Bihar.jpg",
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
        "mosdeng": "cbse_project_assets/13b_Tripura_Fermented_Mosdeng_Food.jpg",
        "ganga_plains": "cbse_project_assets/14_Landscape_Bihar_Ganga_Plains.jpg",
        "jampui_hills": "cbse_project_assets/15b_Landscape_Tripura_Jampui_Hills.jpg",
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

    # Fallback for India map
    if "map_india_combined" not in imgs:
        if os.path.exists("cbse_project_assets/16_Map_Bihar_in_India.png"):
            imgs["map_india_combined"] = Image.open("cbse_project_assets/16_Map_Bihar_in_India.png")

    # Grid calculation
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

    # ==================== SHEET 1: BIHAR SECTION ====================
    print("[*] Rendering Sheet 1: Bihar Section...")
    sheet1 = create_blank_sheet()
    draw_sheet_cutting_creases(sheet1, start_y)
    x, y = get_pos(0, 0); render_maximized_card(sheet1, x, y, imgs["nalanda"], "Nalanda Ancient University Ruins")
    x, y = get_pos(1, 0); render_maximized_card(sheet1, x, y, imgs["mahabodhi"], "Mahabodhi Temple, Bodh Gaya")
    x, y = get_pos(0, 1); render_maximized_card(sheet1, x, y, imgs["chhath"], "Chhath Puja Celebrations")
    x, y = get_pos(1, 1); render_maximized_card(sheet1, x, y, imgs["madhubani"], "Traditional Madhubani Folk Painting")
    x, y = get_pos(0, 2); render_maximized_card(sheet1, x, y, imgs["thekua"], "Traditional Bihari Thekua")
    x, y = get_pos(1, 2); render_maximized_card(sheet1, x, y, imgs["litti"], "Traditional Bihari Litti Chokha")
    sheet1.save("output_cbse/Page_1_Bihar_Section.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 2: TRIPURA SECTION ====================
    print("[*] Rendering Sheet 2: Tripura Section...")
    sheet2 = create_blank_sheet()
    draw_sheet_cutting_creases(sheet2, start_y)
    x, y = get_pos(0, 0); render_maximized_card(sheet2, x, y, imgs["tripura_dress"], "Traditional Tribal Dress of Tripura", focus="top")
    x, y = get_pos(1, 0); render_maximized_card(sheet2, x, y, imgs["kharchi_celebration"], "Kharchi Puja Celebrations")
    x, y = get_pos(0, 1); render_maximized_card(sheet2, x, y, imgs["fourteen_deities"], "The Fourteen Deities (Chaturdash Devta)")
    x, y = get_pos(1, 1); render_maximized_card(sheet2, x, y, imgs["hojagiri"], "Hojagiri Folk Dance")
    x, y = get_pos(0, 2); render_maximized_card(sheet2, x, y, imgs["unakoti"], "Unakoti Rock Reliefs (Lord Shiva Carving)")
    x, y = get_pos(1, 2); render_maximized_card(sheet2, x, y, imgs["mui_borok"], "Traditional Tripuri Cuisine (Mui Borok)")
    sheet2.save("output_cbse/Page_2_Tripura_Section.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 3: COMPARISON & CUISINE ====================
    print("[*] Rendering Sheet 3: Comparison & Geography...")
    sheet3 = create_blank_sheet()
    draw_sheet_cutting_creases(sheet3, start_y)
    x, y = get_pos(0, 0); render_maximized_card(sheet3, x, y, imgs["mosdeng"], "Traditional Fermented Food (Gudok / Berma)")
    x, y = get_pos(1, 0); render_maximized_card(sheet3, x, y,
                                               (imgs["chhath"], imgs["kharchi_celebration"], "Chhath Puja (Bihar)", "Kharchi Puja (Tripura)"),
                                               "Comparison: Chhath Puja & Kharchi Puja", comparison_pair=True)
    x, y = get_pos(0, 1); render_maximized_card(sheet3, x, y,
                                               (imgs["litti"], imgs["mui_borok"], "Litti Chokha (Bihar)", "Mui Borok (Tripura)"),
                                               "Comparison: Bihari Cuisine & Tripuri Cuisine", comparison_pair=True)
    x, y = get_pos(1, 1); render_maximized_card(sheet3, x, y, imgs["map_india_combined"],
                                               "Map of India: Bihar & Tripura")
    x, y = get_pos(0, 2); render_maximized_card(sheet3, x, y,
                                               (imgs["ganga_plains"], imgs["jampui_hills"], "Ganga Plains (Bihar)", "Jampui Hills (Tripura)"),
                                               "Landscapes: Bihar Plains & Tripura Hills", comparison_pair=True)
    sheet3.save("output_cbse/Page_3_Comparison_Section.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 4: STATE DISTRICT MAPS ====================
    print("[*] Rendering Sheet 4: State District Maps...")
    sheet4 = create_blank_sheet()
    map_box_w = PAGE_W - (MARGIN_X * 2)
    map_box_h = (PAGE_H - 120) // 2

    # Draw middle crease between top and bottom maps
    draw4 = ImageDraw.Draw(sheet4)
    mid_map_y = 50 + map_box_h + 10
    draw4.line([(MARGIN_X, mid_map_y), (PAGE_W - MARGIN_X, mid_map_y)], fill=COLOR_CREASE, width=1)

    render_clean_state_map(sheet4, MARGIN_X, 50, map_box_w, map_box_h, imgs["map_bihar"], "State Map of Bihar")
    render_clean_state_map(sheet4, MARGIN_X, 50 + map_box_h + 20, map_box_w, map_box_h, imgs["map_tripura"], "State Map of Tripura")
    sheet4.save("output_cbse/Page_4_State_Maps.png", "PNG", dpi=(300, 300))

    # ==================== MASTER PDF COMPILATION ====================
    print("[*] Compiling all 4 sheets into high-resolution PDF...")
    pdf_path = "output_cbse/CBSE_Class10_Bihar_Tripura_Project.pdf"
    sheet1.save(pdf_path, "PDF", resolution=300.0, save_all=True, append_images=[sheet2, sheet3, sheet4])

    print("\n🎉 SUCCESS! Generated 4 Sheets + Master PDF:")
    for f in sorted(os.listdir("output_cbse")):
        sz = os.path.getsize(os.path.join("output_cbse", f)) / (1024 * 1024)
        print(f"  - {f} ({sz:.2f} MB)")

if __name__ == "__main__":
    main()
