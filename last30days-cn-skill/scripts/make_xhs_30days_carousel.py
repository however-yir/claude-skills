from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

W, H = 1242, 1660
PAGES = 6

OUT_DIR = Path('/Users/however-yir/Documents/Playground/last30days-cn-skill/assets/xhs_30days_share')
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_SONGTI = '/System/Library/Fonts/Supplemental/Songti.ttc'
FONT_HEITI = '/System/Library/Fonts/STHeiti Light.ttc'


def f(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, index=index)


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
    lines = []
    for para in text.split('\n'):
        if not para:
            lines.append('')
            continue
        current = ''
        for ch in para:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def draw_wrapped(draw, x, y, text, font, fill, max_width, line_gap=16):
    lines = wrap_lines(draw, text, font, max_width)
    yy = y
    for line in lines:
        draw.text((x, yy), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line if line else '中', font=font)
        yy += (bbox[3] - bbox[1]) + line_gap
    return yy


def paper_bg(seed: int):
    random.seed(seed)
    img = Image.new('RGB', (W, H), '#fbfbfa')
    d = ImageDraw.Draw(img)

    # vertical paper folds
    for x in [W // 3, W * 2 // 3]:
        d.line([(x, 0), (x, H)], fill=(232, 230, 228), width=2)

    # subtle noise / fibers
    fibers = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fibers)
    for _ in range(1200):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        a = random.randint(8, 20)
        c = random.randint(215, 235)
        fd.point((x, y), fill=(c, c, c, a))

    # faint red sketch marks
    for _ in range(80):
        x1 = random.randint(0, W)
        y1 = random.randint(0, H)
        x2 = x1 + random.randint(-120, 120)
        y2 = y1 + random.randint(-80, 80)
        fd.line([(x1, y1), (x2, y2)], fill=(220, 188, 194, random.randint(14, 24)), width=1)

    img = Image.alpha_composite(img.convert('RGBA'), fibers).convert('RGB')
    img = img.filter(ImageFilter.GaussianBlur(radius=0.2))
    return img


def draw_footer_dots(draw: ImageDraw.ImageDraw, page: int):
    total_width = 18 * PAGES
    start_x = W // 2 - total_width // 2
    y = H - 80
    for i in range(PAGES):
        fill = (216, 67, 106) if i == page - 1 else (170, 170, 170)
        draw.ellipse((start_x + i * 18, y, start_x + i * 18 + 8, y + 8), fill=fill)


def page_common(page: int):
    img = paper_bg(seed=20260331 + page)
    d = ImageDraw.Draw(img)

    # page number
    num_font = f(FONT_HEITI, 30)
    d.rounded_rectangle((1110, 38, 1210, 86), radius=22, fill=(210, 210, 210, 100), outline=(200, 200, 200), width=1)
    d.text((1135, 48), f'{page}/{PAGES}', font=num_font, fill=(120, 120, 120))

    draw_footer_dots(d, page)
    return img, d


def build_pages():
    title_font = f(FONT_SONGTI, 92, index=0)
    h_font = f(FONT_HEITI, 42)
    body_font = f(FONT_SONGTI, 48, index=0)
    body_small = f(FONT_SONGTI, 41, index=0)
    mono_like = f(FONT_HEITI, 34)

    pages = []

    # Page 1
    img, d = page_common(1)
    y = 180
    y = draw_wrapped(d, 86, y, '我把最近30天热点\n写成了一个\n趋势 Skill', title_font, (210, 63, 107), 960, line_gap=22)
    y += 36
    d.text((86, y), '**SKILL.md**', font=h_font, fill=(60, 60, 60))
    y += 94
    text = '```\n名称：last30days\n\n触发条件：\n- 要看最近30天趋势\n- 要中外平台对照\n- 要中文可读结论\n```'
    draw_wrapped(d, 86, y, text, body_small, (35, 35, 35), 1060, line_gap=14)
    pages.append(img)

    # Page 2
    img, d = page_common(2)
    y = 140
    block = '- 还要尽量避开全网噪音\n\n能力描述：\n让“感觉热”变成可验证的热。\n\n调用后，报告会给你：\n- Top trends\n- 跨平台重合点\n- 中国 vs 海外叙事差异\n- 新出现且增长快的信号\n\n```\n不是为了追热点\n是为了看懂热点怎么形成\n```'
    y = draw_wrapped(d, 86, y, block, body_font, (38, 38, 38), 1060, line_gap=18)
    y += 42
    tail = '我是做 AI 工作流的。\n\n写 Skill 这件事，本质上是告诉模型：\n什么时候该严谨，什么时候该克制。'
    draw_wrapped(d, 86, y, tail, body_small, (48, 48, 48), 1060, line_gap=16)
    pages.append(img)

    # Page 3
    img, d = page_common(3)
    y = 140
    d.text((86, y), '这个 30day skill 我主要做了三件事：', font=h_font, fill=(210, 63, 107))
    y += 100
    block = '1) 平台收敛\n只看 X / Weibo / Xiaohongshu / Douyin\n\n2) 窗口固定\n证据窗口 = 最近30天\n\n3) 输出可交付\n不是一堆链接，而是结构化中文报告\n\n```\n趋势扫描 -> 交叉验证 -> 信号提炼\n```'
    draw_wrapped(d, 86, y, block, body_small, (35, 35, 35), 1060, line_gap=18)
    pages.append(img)

    # Page 4
    img, d = page_common(4)
    y = 140
    d.text((86, y), '它不是泛搜索，它更像趋势雷达。', font=h_font, fill=(210, 63, 107))
    y += 94
    cmd = 'python3 scripts/last30days.py "你的主题" \\\n  --emit=json \\\n  --search x,weibo,xiaohongshu,douyin \\\n  --no-native-web \\\n  --days=30'
    y = draw_wrapped(d, 86, y, cmd, mono_like, (34, 34, 34), 1060, line_gap=12)
    y += 56
    block = '然后你拿到的，不是“看起来很多信息”。\n\n而是：\n- 哪个平台在带节奏\n- 哪些话题在跨平台扩散\n- 中国和海外叙事在哪些点分叉\n- 哪些信号值得继续跟踪\n\n这才是可以复用的洞察。'
    draw_wrapped(d, 86, y, block, body_small, (43, 43, 43), 1060, line_gap=16)
    pages.append(img)

    # Page 5
    img, d = page_common(5)
    y = 140
    d.text((86, y), '我最常用的三个场景：', font=h_font, fill=(210, 63, 107))
    y += 100
    block = '场景 1：周一晨会前\n先扫一遍，避免“凭感觉讲趋势”。\n\n场景 2：做内容选题前\n先看平台重叠，再决定写什么。\n\n场景 3：做中外对照时\n直接看叙事差异，减少主观脑补。\n\n```\n它不替你下结论\n它先把证据铺平\n```'
    draw_wrapped(d, 86, y, block, body_small, (36, 36, 36), 1060, line_gap=17)
    pages.append(img)

    # Page 6
    img, d = page_common(6)
    y = 150
    head = '如果你也在做内容 / 产品 / 投研，\n可以抄这个结构：'
    y = draw_wrapped(d, 86, y, head, h_font, (210, 63, 107), 1060, line_gap=20)
    y += 44
    block = '1) 定主题\n2) 定时间窗（最近30天）\n3) 定平台边界（4个平台）\n4) 跑一次结构化报告\n5) 持续跟踪同一批信号\n\n项目：last30days-cn-skill\n\n把“刷到的热点”\n变成“可复用的洞察工作流”。'
    draw_wrapped(d, 86, y, block, body_font, (35, 35, 35), 1060, line_gap=18)
    pages.append(img)

    for i, page in enumerate(pages, start=1):
        out = OUT_DIR / f'xhs_30days_slide_{i}.png'
        page.save(out, quality=96)
        print(out)


if __name__ == '__main__':
    build_pages()
