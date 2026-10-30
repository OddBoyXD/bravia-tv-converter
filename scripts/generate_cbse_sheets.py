#!/usr/bin/env python3
"""
CBSE Class 10 English Project Sheet Generator (V2 - 16:9 Uniform Standard)
"Bihar and Tripura: A Comparison of Cultural Heritage, Festivals, and Food"

Features:
- Exact 16:9 ratio for all photos (1080x608 px inside cards)
- 100% uniform card dimensions across all pages (1130x720 px)
- Simple text headline with Page number only (no paragraphs, no badges, no descriptions)
- Authentic HD photography (real Wikimedia Commons assets, no AI)
- Kharchi Puja festival celebration HD photo
- Sheet 4: Dedicated State Maps of Bihar and Tripura with clean ruled handwriting gaps
- Output: 4 print-ready A4 PNGs (300 DPI) and 1 compiled PDF
"""

import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

PAGE_W = 2480
PAGE_H = 3508
MARGIN_X = 80
MARGIN_Y = 100

# Color Palette
COLOR_BG = (255, 255, 255)
COLOR_BORDER = (148, 163, 184) # Dashed cutting line
COLOR_PHOTO_BORDER = (226, 232, 240)
COLOR_TEXT = (15, 23, 42)
COLOR_TEXT_MUTED = (100, 116, 139)
COLOR_RULED_LINE = (203, 213, 225)

# Uniform Card & Photo Dimensions (16:9)
CARD_W = 1130
IMG_W = 1080
IMG_H = 608  # 1080 * 9 / 16 = 607.5 -> 608 px
PAD_INNER = 25
HEADLINE_H = 55
CARD_H = PAD_INNER + IMG_H + 12 + HEADLINE_H + PAD_INNER  # 25 + 608 + 12 + 55 + 25 = 725 px

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

def draw_dashed_rect(draw, x0, y0, x1, y1, color, dash_len=20, space_len=14, width=3):
    for x in range(int(x0), int(x1), dash_len + space_len):
        draw.line([(x, y0), (min(x + dash_len, x1), y0)], fill=color, width=width)
        draw.line([(x, y1), (min(x + dash_len, x1), y1)], fill=color, width=width)
    for y in range(int(y0), int(y1), dash_len + space_len):
        draw.line([(x0, y), (x0, min(y + dash_len, y1))], fill=color, width=width)
        draw.line([(x1, y), (x1, min(y + dash_len, y1))], fill=color, width=width)

def crop_to_16_9(img, target_w, target_h):
    iw, ih = img.size
    scale = max(target_w / iw, target_h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    cx = (nw - target_w) // 2
    cy = (nh - target_h) // 2
    return resized.crop((cx, cy, cx + target_w, cy + target_h))

def render_uniform_card(canvas, box, img_obj, headline, comparison_pair=None):
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box

    # 1. Dashed Scissor Cut Border
    draw_dashed_rect(draw, x0, y0, x1, y1, COLOR_BORDER, dash_len=22, space_len=14, width=3)

    # 2. Scissor Icon & Cut Hint
    font_hint = get_font(18, bold=False)
    draw.text((x1 - 105, y0 + 8), "✂ Cut line", fill=COLOR_TEXT_MUTED, font=font_hint)

    # 3. Photo Box Area (Exact 16:9)
    px = x0 + PAD_INNER
    py = y0 + PAD_INNER

    if comparison_pair is None:
        # Single 16:9 Photo
        cropped = crop_to_16_9(img_obj, IMG_W, IMG_H)
        canvas.paste(cropped, (px, py))
        draw.rectangle([(px, py), (px + IMG_W, py + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)
    else:
        # Split Side-by-Side Comparison inside 16:9 frame
        img1, img2, lbl1, lbl2 = img_obj
        half_w = (IMG_W - 8) // 2
        c1 = crop_to_16_9(img1, half_w, IMG_H)
        c2 = crop_to_16_9(img2, half_w, IMG_H)
        canvas.paste(c1, (px, py))
        canvas.paste(c2, (px + half_w + 8, py))
        draw.rectangle([(px, py), (px + half_w, py + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)
        draw.rectangle([(px + half_w + 8, py), (px + IMG_W, py + IMG_H)], outline=COLOR_PHOTO_BORDER, width=2)

        # Subtle bottom labels for each side
        font_sub = get_font(20, bold=True)
        draw.rectangle([(px + 10, py + IMG_H - 38), (px + half_w - 10, py + IMG_H - 10)], fill=(0, 0, 0))
        draw.text((px + 20, py + IMG_H - 35), lbl1, fill=(255, 255, 255), font=font_sub)

        draw.rectangle([(px + half_w + 18, py + IMG_H - 38), (px + IMG_W - 10, py + IMG_H - 10)], fill=(0, 0, 0))
        draw.text((px + half_w + 28, py + IMG_H - 35), lbl2, fill=(255, 255, 255), font=font_sub)

    # 4. Simple Text Headline (Centered below image, no descriptions)
    text_y = py + IMG_H + 16
    font_head = get_font(30, bold=True)
    bbox = draw.textbbox((0, 0), headline, font=font_head)
    tw = bbox[2] - bbox[0]
    tx = x0 + (CARD_W - tw) // 2
    draw.text((tx, text_y), headline, fill=COLOR_TEXT, font=font_head)

def create_blank_sheet():
    img = Image.new("RGB", (PAGE_W, PAGE_H), COLOR_BG)
    return img

def render_state_map_card(canvas, box, map_img, headline):
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    card_w = x1 - x0
    card_h = y1 - y0

    # Dashed Scissor Cut Border
    draw_dashed_rect(draw, x0, y0, x1, y1, COLOR_BORDER, dash_len=24, space_len=16, width=3)
    draw.text((x1 - 110, y0 + 12), "✂ Cut line", fill=COLOR_TEXT_MUTED, font=get_font(20))

    # Map Box
    pad = 30
    box_w = card_w - (pad * 2)
    box_h = int(card_h * 0.72)

    mw, mh = map_img.size
    scale = min(box_w / mw, box_h / mh)
    rmw = int(mw * scale)
    rmh = int(mh * scale)
    resized_map = map_img.resize((rmw, rmh), Image.Resampling.LANCZOS)

    mx = x0 + pad + (box_w - rmw) // 2
    my = y0 + pad + (box_h - rmh) // 2
    canvas.paste(resized_map, (mx, my))

    # Simple Headline (No descriptions)
    gap_y = y0 + pad + box_h + 16
    font_head = get_font(36, bold=True)
    draw.text((x0 + pad + 20, gap_y), headline, fill=COLOR_TEXT, font=font_head)

    # Ruled Handwriting Lines for Student Notes
    line_y_start = gap_y + 55
    font_hint = get_font(20, bold=False)
    draw.text((x0 + pad + 20, line_y_start), "Student Notes / Heading:", fill=COLOR_TEXT_MUTED, font=font_hint)

    for i in range(2):
        ly = line_y_start + 45 + (i * 45)
        draw.line([(x0 + pad + 20, ly), (x1 - pad - 20, ly)], fill=COLOR_RULED_LINE, width=2)

def main():
    print("[*] Generating 16:9 Uniform CBSE Sheets & Single PDF...")
    os.makedirs("output_cbse", exist_ok=True)

    # Image Assets Mapping
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

    # Load all images
    imgs = {}
    for key, path in assets.items():
        if os.path.exists(path):
            imgs[key] = Image.open(path).convert("RGB")
        else:
            print(f"[!] Warning: Missing {path}")

    # Fallback for India combined map if SVG hasn't been rasterized
    if "map_india_combined" not in imgs:
        if os.path.exists("cbse_project_assets/16_Map_Bihar_in_India.png"):
            imgs["map_india_combined"] = Image.open("cbse_project_assets/16_Map_Bihar_in_India.png").convert("RGB")

    # Grid calculation for 2 columns x 3 rows
    col_gap = 60
    c0_x = MARGIN_X
    c1_x = c0_x + CARD_W + col_gap

    row_gap = 70
    start_y = (PAGE_H - (3 * CARD_H + 2 * row_gap)) // 2
    r0_y = start_y
    r1_y = r0_y + CARD_H + row_gap
    r2_y = r1_y + CARD_H + row_gap

    def get_slot(col, row):
        x = c0_x if col == 0 else c1_x
        y = [r0_y, r1_y, r2_y][row]
        return (x, y, x + CARD_W, y + CARD_H)

    # ==================== SHEET 1: BIHAR SECTION (Pages 4–7) ====================
    print("[*] Rendering Sheet 1: Bihar Section...")
    sheet1 = create_blank_sheet()
    render_uniform_card(sheet1, get_slot(0, 0), imgs["nalanda"], "Page 4: Nalanda Ancient University Ruins")
    render_uniform_card(sheet1, get_slot(1, 0), imgs["mahabodhi"], "Page 4: Mahabodhi Temple, Bodh Gaya")
    render_uniform_card(sheet1, get_slot(0, 1), imgs["chhath"], "Page 5: Chhath Puja Celebrations")
    render_uniform_card(sheet1, get_slot(1, 1), imgs["madhubani"], "Page 6: Traditional Madhubani Folk Painting")
    render_uniform_card(sheet1, get_slot(0, 2), imgs["thekua"], "Page 7: Traditional Bihari Thekua")
    render_uniform_card(sheet1, get_slot(1, 2), imgs["litti"], "Page 7: Traditional Bihari Litti Chokha")
    sheet1.save("output_cbse/Page_1_Bihar_Section.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 2: TRIPURA SECTION (Pages 8–12) ====================
    print("[*] Rendering Sheet 2: Tripura Section...")
    sheet2 = create_blank_sheet()
    render_uniform_card(sheet2, get_slot(0, 0), imgs["tripura_dress"], "Page 8: Traditional Tribal Dress of Tripura")
    render_uniform_card(sheet2, get_slot(1, 0), imgs["kharchi_celebration"], "Page 9: Kharchi Puja Celebrations")
    render_uniform_card(sheet2, get_slot(0, 1), imgs["fourteen_deities"], "Page 9: The Fourteen Deities (Chaturdash Devta)")
    render_uniform_card(sheet2, get_slot(1, 1), imgs["hojagiri"], "Page 10: Hojagiri Folk Dance")
    render_uniform_card(sheet2, get_slot(0, 2), imgs["unakoti"], "Page 11: Unakoti Rock Reliefs (Shiva Carving)")
    render_uniform_card(sheet2, get_slot(1, 2), imgs["mui_borok"], "Page 12: Traditional Tripuri Cuisine (Mui Borok)")
    sheet2.save("output_cbse/Page_2_Tripura_Section.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 3: COMPARISON & CUISINE (Pages 12–16) ====================
    print("[*] Rendering Sheet 3: Comparison & Geography...")
    sheet3 = create_blank_sheet()
    render_uniform_card(sheet3, get_slot(0, 0), imgs["mosdeng"], "Page 12: Traditional Fermented Food (Mosdeng / Berma)")
    render_uniform_card(sheet3, get_slot(1, 0),
                        (imgs["chhath"], imgs["kharchi_celebration"], "Chhath Puja (Bihar)", "Kharchi Puja (Tripura)"),
                        "Page 13: Comparison: Chhath Puja & Kharchi Puja", comparison_pair=True)
    render_uniform_card(sheet3, get_slot(0, 1),
                        (imgs["litti"], imgs["mosdeng"], "Litti Chokha (Bihar)", "Mui Borok (Tripura)"),
                        "Page 14: Comparison: Bihari Cuisine & Tripuri Cuisine", comparison_pair=True)
    render_uniform_card(sheet3, get_slot(1, 1), imgs["map_india_combined"],
                        "Page 15: Map of India: Bihar & Tripura")
    render_uniform_card(sheet3, get_slot(0, 2),
                        (imgs["ganga_plains"], imgs["jampui_hills"], "Ganga Plains (Bihar)", "Jampui Hills (Tripura)"),
                        "Page 16: Landscapes: Bihar Plains & Tripura Hills", comparison_pair=True)
    sheet3.save("output_cbse/Page_3_Comparison_Section.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 4: STATE DISTRICT MAPS ====================
    print("[*] Rendering Sheet 4: State District Maps...")
    sheet4 = create_blank_sheet()
    map_h = 1520
    map_w = PAGE_W - (MARGIN_X * 2)

    top_box = (MARGIN_X, 140, MARGIN_X + map_w, 140 + map_h)
    bot_box = (MARGIN_X, 140 + map_h + 80, MARGIN_X + map_w, 140 + (map_h * 2) + 80)

    render_state_map_card(sheet4, top_box, imgs["map_bihar"], "State Map of Bihar")
    render_state_map_card(sheet4, bot_box, imgs["map_tripura"], "State Map of Tripura")
    sheet4.save("output_cbse/Page_4_State_Maps.png", "PNG", dpi=(300, 300))

    # ==================== COMPILE ALL 4 SHEETS INTO SINGLE PDF ====================
    print("[*] Compiling all 4 sheets into high-resolution PDF...")
    pdf_path = "output_cbse/CBSE_Class10_Bihar_Tripura_Project.pdf"
    sheet1.save(pdf_path, "PDF", resolution=300.0, save_all=True, append_images=[sheet2, sheet3, sheet4])

    print("\n🎉 SUCCESS! Generated 4 Sheets + Master PDF:")
    for f in sorted(os.listdir("output_cbse")):
        sz = os.path.getsize(os.path.join("output_cbse", f)) / (1024 * 1024)
        print(f"  - {f} ({sz:.2f} MB)")

if __name__ == "__main__":
    main()
