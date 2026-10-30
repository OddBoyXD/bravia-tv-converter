#!/usr/bin/env python3
"""
CBSE Class 10 English Project Sheet Generator
"Bihar and Tripura: A Comparison of Cultural Heritage, Festivals, and Food"
Generates 5 print-ready 300 DPI A4 image sheets (2480x3508 px) and combines them into a single PDF.
"""

import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

# A4 Dimensions at 300 DPI
PAGE_W = 2480
PAGE_H = 3508
MARGIN = 90

# Colors
COLOR_BG = (255, 255, 255)
COLOR_CARD_BORDER = (160, 174, 192) # Dashed cut border
COLOR_TEXT_MAIN = (15, 23, 42)
COLOR_TEXT_MUTED = (71, 85, 105)
COLOR_BIHAR = (194, 65, 12)
COLOR_TRIPURA = (4, 120, 87)
COLOR_COMPARE = (109, 40, 217)
COLOR_HEADER_BG = (30, 58, 138)

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

def download_image(url):
    print(f"Downloading from web: {url[:80]}...")
    headers = {"User-Agent": "CBSE-School-Project-Generator/1.0 (cbse.project@edu.gov.in)"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    return img

def create_base_page(sheet_title, sheet_subtitle):
    img = Image.new("RGB", (PAGE_W, PAGE_H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Top Header Banner
    header_h = 130
    draw.rectangle([(MARGIN, MARGIN), (PAGE_W - MARGIN, MARGIN + header_h)], fill=COLOR_HEADER_BG)
    
    font_title = get_font(42, bold=True)
    font_sub = get_font(28, bold=False)

    draw.text((MARGIN + 35, MARGIN + 22), sheet_title, fill=(255, 255, 255), font=font_title)
    draw.text((MARGIN + 35, MARGIN + 75), sheet_subtitle, fill=(226, 232, 240), font=font_sub)

    return img, draw

def draw_dashed_rect(draw, x0, y0, x1, y1, color, dash_len=20, space_len=14, width=3):
    # Top and bottom
    for x in range(int(x0), int(x1), dash_len + space_len):
        draw.line([(x, y0), (min(x + dash_len, x1), y0)], fill=color, width=width)
        draw.line([(x, y1), (min(x + dash_len, x1), y1)], fill=color, width=width)
    # Left and right
    for y in range(int(y0), int(y1), dash_len + space_len):
        draw.line([(x0, y), (x0, min(y + dash_len, y1))], fill=color, width=width)
        draw.line([(x1, y), (x1, min(y + dash_len, y1))], fill=color, width=width)

def render_photo_card(canvas, box, img_obj, badge_text, badge_color, heading, sub_text, comparison_side=None):
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = box
    card_w = x1 - x0
    card_h = y1 - y0

    # Draw dashed scissor-cut border around card
    draw_dashed_rect(draw, x0, y0, x1, y1, COLOR_CARD_BORDER, dash_len=22, space_len=14, width=3)

    # Scissor cutting icon hint in top right
    font_hint = get_font(18, bold=False)
    draw.text((x1 - 100, y0 + 10), "✂ Cut line", fill=(148, 163, 184), font=font_hint)

    # Photo Box Area
    pad = 22
    photo_x0 = x0 + pad
    photo_y0 = y0 + pad
    photo_w = card_w - (pad * 2)
    photo_h = int(card_h * 0.72)

    # Scale photo to fill photo_w x photo_h
    if img_obj:
        if comparison_side is None:
            # Single photo card
            iw, ih = img_obj.size
            scale = max(photo_w / iw, photo_h / ih)
            new_w = int(iw * scale)
            new_h = int(ih * scale)
            resized = img_obj.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Crop center
            cx = (new_w - photo_w) // 2
            cy = (new_h - photo_h) // 2
            cropped = resized.crop((cx, cy, cx + photo_w, cy + photo_h))
            canvas.paste(cropped, (photo_x0, photo_y0))
        else:
            # Side-by-side comparison inside one card
            img1, img2, label1, label2 = img_obj
            half_w = (photo_w - 10) // 2

            for idx, (sub_img, sub_lbl) in enumerate([(img1, label1), (img2, label2)]):
                sx = photo_x0 if idx == 0 else photo_x0 + half_w + 10
                iw, ih = sub_img.size
                scale = max(half_w / iw, photo_h / ih)
                rw = int(iw * scale)
                rh = int(ih * scale)
                r_img = sub_img.resize((rw, rh), Image.Resampling.LANCZOS)
                cx = (rw - half_w) // 2
                cy = (rh - photo_h) // 2
                c_img = r_img.crop((cx, cy, cx + half_w, cy + photo_h))
                canvas.paste(c_img, (sx, photo_y0))

                # Overlay label at bottom of each half
                draw.rectangle([(sx + 10, photo_y0 + photo_h - 40), (sx + half_w - 10, photo_y0 + photo_h - 8)], fill=(0, 0, 0))
                font_sub_lbl = get_font(20, bold=True)
                draw.text((sx + 20, photo_y0 + photo_h - 37), sub_lbl, fill=(255, 255, 255), font=font_sub_lbl)

    # Caption / Text Box below image
    text_y = photo_y0 + photo_h + 16

    # Badge Pill
    badge_font = get_font(22, bold=True)
    badge_pad_x = 18
    badge_pad_y = 6
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = (bbox[2] - bbox[0]) + badge_pad_x * 2
    bh = (bbox[3] - bbox[1]) + badge_pad_y * 2
    draw.rounded_rectangle([(photo_x0, text_y), (photo_x0 + bw, text_y + bh)], radius=6, fill=badge_color)
    draw.text((photo_x0 + badge_pad_x, text_y + badge_pad_y), badge_text, fill=(255, 255, 255), font=badge_font)

    # Main Heading
    head_font = get_font(32, bold=True)
    head_y = text_y + bh + 12
    draw.text((photo_x0, head_y), heading, fill=COLOR_TEXT_MAIN, font=head_font)

    # Educational Description
    sub_font = get_font(22, bold=False)
    desc_y = head_y + 44
    draw.text((photo_x0, desc_y), sub_text, fill=COLOR_TEXT_MUTED, font=sub_font)

def main():
    print("[*] Starting CBSE Project A4 Sheet Generation...")
    os.makedirs("output_cbse", exist_ok=True)

    local_map = {
        "nalanda": "cbse_project_assets/01_Nalanda_University_Ruins_Bihar.jpg",
        "mahabodhi": "cbse_project_assets/02_Mahabodhi_Temple_Bodh_Gaya_Bihar.jpg",
        "chhath": "cbse_project_assets/03_Chhath_Puja_Celebration_Bihar.jpg",
        "madhubani": "cbse_project_assets/04_Madhubani_Mithila_Folk_Painting_Bihar.jpg",
        "thekua": "cbse_project_assets/05_Traditional_Thekua_Bihar.jpg",
        "litti": "cbse_project_assets/06_Traditional_Litti_Chokha_Bihar.jpg",
        "tripura_dress": "cbse_project_assets/07_Traditional_Tribal_Dress_Tripura.jpg",
        "kharchi_temple": "cbse_project_assets/08_Kharchi_Puja_Chaturdasha_Temple_Tripura.jpg",
        "fourteen_deities": "cbse_project_assets/09_Fourteen_Deities_Chaturdash_Devta_Tripura.jpg",
        "hojagiri": "cbse_project_assets/10_Hojagiri_Folk_Dance_Reang_Tripura.jpg",
        "unakoti": "cbse_project_assets/11_Unakoti_Rock_Reliefs_Shiva_Tripura.jpg",
        "mui_borok": "cbse_project_assets/13_Tripura_Traditional_Food_Mui_Borok.jpg",
        "mosdeng": "cbse_project_assets/13b_Tripura_Fermented_Mosdeng_Food.jpg",
        "ganga_plains": "cbse_project_assets/14_Landscape_Bihar_Ganga_Plains.jpg",
        "jampui_hills": "cbse_project_assets/15b_Landscape_Tripura_Jampui_Hills.jpg",
        "map_bihar": "cbse_project_assets/18_State_Map_Bihar_Districts.png",
        "map_tripura": "cbse_project_assets/19_State_Map_Tripura_Districts.png",
        "map_india_bihar": "cbse_project_assets/16_Map_Bihar_in_India.png",
        "map_india_tripura": "cbse_project_assets/17_Map_Tripura_in_India.png"
    }

    urls = {
        "nalanda": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f9/Remains_of_Nalanda_University.jpg/1280px-Remains_of_Nalanda_University.jpg",
        "mahabodhi": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/63/Mahabodhi_Temple%2C_Bodh_Gaya%2C_Bihar%2C_India.jpg/1280px-Mahabodhi_Temple%2C_Bodh_Gaya%2C_Bihar%2C_India.jpg",
        "chhath": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f7/CHHATH_PUJA.jpg/1280px-CHHATH_PUJA.jpg",
        "madhubani": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/28/Madhubani_art.jpg/1280px-Madhubani_art.jpg",
        "thekua": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e0/Thekua.jpg/1280px-Thekua.jpg",
        "litti": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/26/Litti_chokha_dipped_in_Ghee.jpg/1280px-Litti_chokha_dipped_in_Ghee.jpg",
        "tripura_dress": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b5/Traditional_dress_of_Tripura.jpg/1280px-Traditional_dress_of_Tripura.jpg",
        "kharchi_temple": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/57/Temple_of_14_gods-Tripura.jpg/1280px-Temple_of_14_gods-Tripura.jpg",
        "fourteen_deities": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7c/CHATURDASH_DEVTA_TEMPLE%2CTRIPURA.jpg/1280px-CHATURDASH_DEVTA_TEMPLE%2CTRIPURA.jpg",
        "hojagiri": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8b/Hojagiri_dance_on_the_streets.jpg/1280px-Hojagiri_dance_on_the_streets.jpg",
        "unakoti": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/30/Unakoti.jpg/1280px-Unakoti.jpg",
        "mui_borok": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/37/A_women_serving_Tripuri_traditional_dishes.jpg/1280px-A_women_serving_Tripuri_traditional_dishes.jpg",
        "mosdeng": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fe/Wahan_Mosdeng_and_Ruti-_Agartala-_Tripura.jpg/1280px-Wahan_Mosdeng_and_Ruti-_Agartala-_Tripura.jpg",
        "ganga_plains": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/80/Ganga_River_in_plains.jpg/1280px-Ganga_River_in_plains.jpg",
        "jampui_hills": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3b/Jampui_2.jpg/1280px-Jampui_2.jpg",
        "map_bihar": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a9/Bihar_districts.svg/1280px-Bihar_districts.svg.png",
        "map_tripura": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/42/Tripura-district-map.svg/1280px-Tripura-district-map.svg.png",
        "map_india_bihar": "https://upload.wikimedia.org/wikipedia/commons/2/24/Bihar_in_India.png",
        "map_india_tripura": "https://upload.wikimedia.org/wikipedia/commons/4/49/Tripura_in_India.png"
    }

    # Load local images or download
    imgs = {}
    for key, local_f in local_map.items():
        if os.path.exists(local_f):
            print(f"Loading local asset: {local_f}")
            imgs[key] = Image.open(local_f).convert("RGB")
        else:
            imgs[key] = download_image(urls[key])

    # Common grid coordinates for 2x2 cards (Sheets 1–4)
    grid_top = MARGIN + 160
    col_w = (PAGE_W - (MARGIN * 2) - 40) // 2
    row_h = (PAGE_H - grid_top - MARGIN - 40) // 2

    c0_x0 = MARGIN
    c0_x1 = c0_x0 + col_w
    c1_x0 = c0_x1 + 40
    c1_x1 = c1_x0 + col_w

    r0_y0 = grid_top
    r0_y1 = r0_y0 + row_h
    r1_y0 = r0_y1 + 40
    r1_y1 = r1_y0 + row_h

    # ==================== SHEET 1: BIHAR HERITAGE & FESTIVALS ====================
    print("[*] Rendering Sheet 1: Bihar Heritage & Festivals...")
    p1, _ = create_base_page(
        "CBSE CLASS 10 ENGLISH PROJECT • BIHAR & TRIPURA",
        "Sheet 1 of 5: Cultural Heritage & Festivals of Bihar (Pages 4–6)"
    )
    render_photo_card(p1, (c0_x0, r0_y0, c0_x1, r0_y1), imgs["nalanda"],
                      "PAGE 4 • BIHAR HERITAGE", COLOR_BIHAR,
                      "1. Ancient Ruins of Nalanda Mahavihara",
                      "Ancient Buddhist university (5th–12th CE) in Rajgir, Bihar. UNESCO World Heritage Site.")

    render_photo_card(p1, (c1_x0, r0_y0, c1_x1, r0_y1), imgs["mahabodhi"],
                      "PAGE 4 • BIHAR HERITAGE", COLOR_BIHAR,
                      "2. Mahabodhi Temple, Bodh Gaya",
                      "Sacred UNESCO World Heritage site where Lord Buddha attained supreme enlightenment.")

    render_photo_card(p1, (c0_x0, r1_y0, c0_x1, r1_y1), imgs["chhath"],
                      "PAGE 5 • BIHAR FESTIVAL", COLOR_BIHAR,
                      "3. Chhath Puja Celebrations in Bihar",
                      "Devotees offering Arghya standing in holy river Ganga to the setting & rising Sun.")

    render_photo_card(p1, (c1_x0, r1_y0, c1_x1, r1_y1), imgs["madhubani"],
                      "PAGE 6 • BIHAR FOLK ART", COLOR_BIHAR,
                      "4. Traditional Madhubani (Mithila) Painting",
                      "Authentic folk art from Mithila region of Bihar with intricate geometric patterns.")

    p1.save("output_cbse/Page_1_Bihar_Heritage_Festivals.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 2: BIHAR CUISINE & TRIPURA TRIBAL CULTURE ====================
    print("[*] Rendering Sheet 2: Bihar Cuisine & Tripura Tribal Culture...")
    p2, _ = create_base_page(
        "CBSE CLASS 10 ENGLISH PROJECT • BIHAR & TRIPURA",
        "Sheet 2 of 5: Bihar Traditional Cuisine & Tripura Tribal Culture (Pages 7–9)"
    )
    render_photo_card(p2, (c0_x0, r0_y0, c0_x1, r0_y1), imgs["thekua"],
                      "PAGE 7 • BIHAR FOOD", COLOR_BIHAR,
                      "5. Traditional Bihari Thekua",
                      "Sacred crispy festive sweet prepared from whole wheat flour, jaggery, and desi ghee.")

    render_photo_card(p2, (c1_x0, r0_y0, c1_x1, r0_y1), imgs["litti"],
                      "PAGE 7 • BIHAR FOOD", COLOR_BIHAR,
                      "6. Traditional Bihari Litti Chokha",
                      "Roasted wheat balls stuffed with spiced sattu, served dipped in pure ghee with chokha.")

    render_photo_card(p2, (c0_x0, r1_y0, c0_x1, r1_y1), imgs["tripura_dress"],
                      "PAGE 8 • TRIPURA CULTURE", COLOR_TRIPURA,
                      "7. Traditional Tribal Attire of Tripura",
                      "Indigenous tribal women wearing handwoven 'Rignai' and 'Risa' with tribal jewelry.")

    render_photo_card(p2, (c1_x0, r1_y0, c1_x1, r1_y1), imgs["kharchi_temple"],
                      "PAGE 9 • TRIPURA FESTIVAL", COLOR_TRIPURA,
                      "8. Kharchi Puja Festival Celebrations",
                      "The royal and tribal festival of Tripura at Chaturdasha Temple for earth purification.")

    p2.save("output_cbse/Page_2_Bihar_Food_Tripura_Culture.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 3: TRIPURA HERITAGE, DANCE & FOOD ====================
    print("[*] Rendering Sheet 3: Tripura Heritage, Dance & Food...")
    p3, _ = create_base_page(
        "CBSE CLASS 10 ENGLISH PROJECT • BIHAR & TRIPURA",
        "Sheet 3 of 5: Sacred Heritage, Folk Dance & Cuisine of Tripura (Pages 9–12)"
    )
    render_photo_card(p3, (c0_x0, r0_y0, c0_x1, r0_y1), imgs["fourteen_deities"],
                      "PAGE 9 • TRIPURA DEITIES", COLOR_TRIPURA,
                      "9. Temple of the Fourteen Deities",
                      "Historical shrine in Old Agartala housing the ancestral metallic head-idols.")

    render_photo_card(p3, (c1_x0, r0_y0, c1_x1, r0_y1), imgs["hojagiri"],
                      "PAGE 10 • TRIPURA FOLK DANCE", COLOR_TRIPURA,
                      "10. Hojagiri Dance (Reang Community)",
                      "Acrobatic folk dance where Reang dancers balance on pitchers and brass plates with lamps.")

    render_photo_card(p3, (c0_x0, r1_y0, c0_x1, r1_y1), imgs["unakoti"],
                      "PAGE 11 • TRIPURA HERITAGE", COLOR_TRIPURA,
                      "11. Unakoti Rock Carvings: Giant Shiva",
                      "Colossal 30-foot bas-relief rock sculpture of Lord Shiva in the forested hills of Tripura.")

    render_photo_card(p3, (c1_x0, r1_y0, c1_x1, r1_y1), imgs["mui_borok"],
                      "PAGE 12 • TRIPURA CUISINE", COLOR_TRIPURA,
                      "12. Traditional Tripuri Cuisine (Mui Borok)",
                      "Organic tribal meal featuring wild forest herbs, bamboo shoots, and berma preparations.")

    p3.save("output_cbse/Page_3_Tripura_Sacred_Heritage_Food.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 4: COMPARATIVE ANALYSIS & GEOGRAPHY ====================
    print("[*] Rendering Sheet 4: Comparative Analysis & Geography...")
    p4, _ = create_base_page(
        "CBSE CLASS 10 ENGLISH PROJECT • BIHAR & TRIPURA",
        "Sheet 4 of 5: Comparative Analysis & Landscapes (Pages 13–16)"
    )
    render_photo_card(p4, (c0_x0, r0_y0, c0_x1, r0_y1),
                      (imgs["chhath"], imgs["kharchi_temple"], "Chhath Puja (Bihar)", "Kharchi Puja (Tripura)"),
                      "PAGE 13 • FESTIVAL COMPARISON", COLOR_COMPARE,
                      "13. Chhath Puja (Bihar) vs. Kharchi Puja (Tripura)",
                      "Veneration of the Sun God in Bihar contrasted with 14-deity earth cleansing in Tripura.",
                      comparison_side="split")

    render_photo_card(p4, (c1_x0, r0_y0, c1_x1, r0_y1),
                      (imgs["litti"], imgs["mosdeng"], "Litti Chokha (Bihar)", "Mui Borok (Tripura)"),
                      "PAGE 14 • FOOD COMPARISON", COLOR_COMPARE,
                      "14. Bihari Cuisine vs. Tripuri Cuisine",
                      "Sattu, wheat & ghee dishes of Bihar contrasted with boiled, fermented cuisine of Tripura.",
                      comparison_side="split")

    render_photo_card(p4, (c0_x0, r1_y0, c0_x1, r1_y1),
                      (imgs["map_india_bihar"], imgs["map_india_tripura"], "Bihar (East India)", "Tripura (Northeast)"),
                      "PAGE 15 • GEOGRAPHICAL LOCATION", COLOR_COMPARE,
                      "15. Map of India Highlighting Bihar & Tripura",
                      "Official geographic locations: Bihar in Eastern India and Tripura in Northeastern India.",
                      comparison_side="split")

    render_photo_card(p4, (c1_x0, r1_y0, c1_x1, r1_y1),
                      (imgs["ganga_plains"], imgs["jampui_hills"], "Ganga Plains (Bihar)", "Jampui Hills (Tripura)"),
                      "PAGE 16 • LANDSCAPE COMPARISON", COLOR_COMPARE,
                      "16. Bihar (Plains) vs. Tripura (Hills & Valleys)",
                      "Fertile flat alluvial river plains of Bihar contrasted with lush green hill ridges of Tripura.",
                      comparison_side="split")

    p4.save("output_cbse/Page_4_Comparative_Analysis_Geography.png", "PNG", dpi=(300, 300))

    # ==================== SHEET 5: STATE DISTRICT MAPS WITH HANDWRITING GAP ====================
    print("[*] Rendering Sheet 5: State District Maps...")
    p5, draw5 = create_base_page(
        "CBSE CLASS 10 ENGLISH PROJECT • BIHAR & TRIPURA",
        "Sheet 5 of 5: State District Maps with Headline Writing Space"
    )

    map_card_h = (PAGE_H - grid_top - MARGIN - 40) // 2

    # Top: Bihar Map
    b_y0 = grid_top
    b_y1 = b_y0 + map_card_h
    draw_dashed_rect(draw5, MARGIN, b_y0, PAGE_W - MARGIN, b_y1, COLOR_CARD_BORDER, dash_len=22, space_len=14, width=3)
    draw5.text((PAGE_W - MARGIN - 100, b_y0 + 10), "✂ Cut line", fill=(148, 163, 184), font=get_font(18))

    # Place Bihar Map Image (centered)
    m_bihar = imgs["map_bihar"]
    m_pad = 20
    m_box_w = PAGE_W - (MARGIN * 2) - (m_pad * 2)
    m_box_h = int(map_card_h * 0.70)
    bw, bh = m_bihar.size
    scale_b = min(m_box_w / bw, m_box_h / bh)
    rbw = int(bw * scale_b)
    rbh = int(bh * scale_b)
    r_bihar = m_bihar.resize((rbw, rbh), Image.Resampling.LANCZOS)
    bx_pos = MARGIN + m_pad + (m_box_w - rbw) // 2
    by_pos = b_y0 + m_pad + (m_box_h - rbh) // 2
    p5.paste(r_bihar, (bx_pos, by_pos))

    # Headline writing gap below Bihar Map
    gap_y = b_y0 + m_pad + m_box_h + 10
    draw5.rectangle([(MARGIN + m_pad, gap_y), (PAGE_W - MARGIN - m_pad, b_y1 - m_pad)], fill=(248, 250, 252), outline=(226, 232, 240), width=2)
    draw5.text((MARGIN + m_pad + 20, gap_y + 12), "✍️ HEADLINE / STUDENT PROJECT NOTES: ____________________________________________________________________", fill=COLOR_TEXT_MUTED, font=get_font(22, bold=True))
    draw5.text((MARGIN + m_pad + 20, gap_y + 46), "STATE OF BIHAR", fill=COLOR_BIHAR, font=get_font(26, bold=True))
    draw5.text((MARGIN + m_pad + 260, gap_y + 48), "• Showing 38 Administrative Districts & State Capital (Patna) along the River Ganga basin.", fill=COLOR_TEXT_MAIN, font=get_font(22))

    # Bottom: Tripura Map
    t_y0 = b_y1 + 40
    t_y1 = t_y0 + map_card_h
    draw_dashed_rect(draw5, MARGIN, t_y0, PAGE_W - MARGIN, t_y1, COLOR_CARD_BORDER, dash_len=22, space_len=14, width=3)
    draw5.text((PAGE_W - MARGIN - 100, t_y0 + 10), "✂ Cut line", fill=(148, 163, 184), font=get_font(18))

    # Place Tripura Map Image (centered)
    m_tripura = imgs["map_tripura"]
    tw, th = m_tripura.size
    scale_t = min(m_box_w / tw, m_box_h / th)
    rtw = int(tw * scale_t)
    rth = int(th * scale_t)
    r_tripura = m_tripura.resize((rtw, rth), Image.Resampling.LANCZOS)
    tx_pos = MARGIN + m_pad + (m_box_w - rtw) // 2
    ty_pos = t_y0 + m_pad + (m_box_h - rth) // 2
    p5.paste(r_tripura, (tx_pos, ty_pos))

    # Headline writing gap below Tripura Map
    t_gap_y = t_y0 + m_pad + m_box_h + 10
    draw5.rectangle([(MARGIN + m_pad, t_gap_y), (PAGE_W - MARGIN - m_pad, t_y1 - m_pad)], fill=(248, 250, 252), outline=(226, 232, 240), width=2)
    draw5.text((MARGIN + m_pad + 20, t_gap_y + 12), "✍️ HEADLINE / STUDENT PROJECT NOTES: ____________________________________________________________________", fill=COLOR_TEXT_MUTED, font=get_font(22, bold=True))
    draw5.text((MARGIN + m_pad + 20, t_gap_y + 46), "STATE OF TRIPURA", fill=COLOR_TRIPURA, font=get_font(26, bold=True))
    draw5.text((MARGIN + m_pad + 300, t_gap_y + 48), "• Showing 8 Administrative Districts & State Capital (Agartala) bordered by Bangladesh.", fill=COLOR_TEXT_MAIN, font=get_font(22))

    p5.save("output_cbse/Page_5_State_Maps_Bihar_Tripura.png", "PNG", dpi=(300, 300))

    # ==================== COMBINE ALL 5 PAGES INTO SINGLE PDF ====================
    print("[*] Combining all 5 sheets into a single high-resolution PDF...")
    pdf_path = "output_cbse/CBSE_Class10_Bihar_Tripura_Project.pdf"
    p1.save(pdf_path, "PDF", resolution=300.0, save_all=True, append_images=[p2, p3, p4, p5])

    print("\n🎉 SUCCESS! ALL 5 SHEETS + COMPLETE PDF GENERATED:")
    for f in sorted(os.listdir("output_cbse")):
        sz = os.path.getsize(os.path.join("output_cbse", f)) / (1024 * 1024)
        print(f"  - {f} ({sz:.2f} MB)")

if __name__ == "__main__":
    main()
