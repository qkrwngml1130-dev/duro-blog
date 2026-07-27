#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""뚜뚜 캐릭터 일러스트 생성기.

사진(거즈 수건을 후드처럼 뒤집어쓴 뚜뚜)을 보고 벡터로 그린 캐릭터.
블로그 파스텔 팔레트(#FFF8F0 크림 배경)에 맞춤.
SVG로 그린 뒤 cairosvg로 PNG 저장 → assets/ 폴더.
"""

import math
import random

import cairosvg

W = H = 800

# ── 팔레트 ────────────────────────────────────────────────
BG        = "#FFF8F0"   # 크림 배경
FABRIC    = "#FCF5E9"   # 거즈 수건 밝은 면
FABRIC_SH = "#F1E5D2"   # 거즈 그늘
FOLD      = "#E9DAC2"   # 접힘선
SKIN      = "#FBE0CD"   # 피부
SKIN_SH   = "#F3CCB4"   # 피부 그늘
BLUSH     = "#F5B7B2"   # 볼터치
HAIR      = "#4B3A31"   # 머리카락
EYE       = "#3A2B24"   # 눈
BROW      = "#8A6B58"   # 눈썹
MOUTH     = "#D98079"   # 입
MOUTH_IN  = "#C4675F"   # 입 안쪽
CHERRY    = "#E4726A"   # 체리
APRICOT   = "#F2B45E"   # 살구/오렌지
LEAF      = "#9FBB8B"   # 잎
STEM      = "#88A96B"   # 줄기

# ── 주요 도형 기준값 ──────────────────────────────────────
HOOD  = (400, 415, 258, 270)   # 후드 바깥 (cx, cy, rx, ry)
FACE  = (400, 442, 172, 182)   # 얼굴 (후드 안쪽 구멍)
COLLAR = (400, 706, 236, 118)  # 턱 아래 감싼 천
HAND  = (598, 614, 54)         # 담요 밖으로 빼꼼 나온 주먹 (cx, cy, r)
BODY_TOP, BODY_BOT = 578, 800
BODY_L, BODY_R = 138, 662


def in_ellipse(x, y, cx, cy, rx, ry, margin=0.0):
    rx, ry = rx - margin, ry - margin
    if rx <= 0 or ry <= 0:
        return False
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def in_body(x, y, margin=0.0):
    """아래쪽 담요(몸통) 영역 근사."""
    if not (BODY_TOP + margin <= y <= BODY_BOT):
        return False
    t = min(1.0, (y - BODY_TOP) / (BODY_BOT - BODY_TOP))
    span = 262 * (1 - t) ** 2
    return (BODY_L + span + margin) <= x <= (BODY_R - span - margin)


# ── 과일 무늬 모티브 ──────────────────────────────────────
def cherry(x, y, s, rot):
    return f"""<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f}) scale({s:.2f})">
      <path d="M -4 -3 C -3 -11 2 -14 6 -15" fill="none" stroke="{STEM}" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M 5 -1 C 6 -8 7 -12 6 -15" fill="none" stroke="{STEM}" stroke-width="1.8" stroke-linecap="round"/>
      <circle cx="-5" cy="1" r="5.6" fill="{CHERRY}"/>
      <circle cx="6" cy="3" r="5.0" fill="{CHERRY}"/>
      <circle cx="-6.6" cy="-0.6" r="1.5" fill="#FFFFFF" opacity="0.45"/>
    </g>"""


def apricot(x, y, s, rot):
    return f"""<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f}) scale({s:.2f})">
      <circle cx="0" cy="1" r="7.4" fill="{APRICOT}"/>
      <circle cx="-2.4" cy="-1.6" r="2.0" fill="#FFFFFF" opacity="0.4"/>
      <path d="M 1 -6 C 5 -10 9 -10 10 -8 C 9 -5 5 -4 1 -6 Z" fill="{LEAF}"/>
    </g>"""


def sprig(x, y, s, rot):
    return f"""<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f}) scale({s:.2f})">
      <path d="M -9 6 C -3 1 4 -3 11 -7" fill="none" stroke="{STEM}" stroke-width="1.6" stroke-linecap="round"/>
      <path d="M -5 4 C -6 -2 -2 -4 0 -1 C 0 2 -3 5 -5 4 Z" fill="{LEAF}"/>
      <path d="M 2 -1 C 1 -7 5 -9 7 -6 C 7 -3 4 0 2 -1 Z" fill="{LEAF}"/>
      <path d="M -1 7 C 3 5 6 7 5 10 C 2 11 0 9 -1 7 Z" fill="{LEAF}"/>
    </g>"""


MOTIFS = (cherry, apricot, sprig)


def scatter_pattern(seed=7):
    """천(후드·몸통·턱천) 위에만 과일 무늬를 뿌린다. 얼굴/손은 피함."""
    rnd = random.Random(seed)
    placed, out = [], []
    tries = 0
    while len(placed) < 34 and tries < 6000:
        tries += 1
        x = rnd.uniform(60, 740)
        y = rnd.uniform(180, 790)

        on_fabric = (
            in_ellipse(x, y, *HOOD, margin=26)
            or in_ellipse(x, y, *COLLAR, margin=22)
            or in_body(x, y, margin=26)
        )
        if not on_fabric:
            continue
        if in_ellipse(x, y, *FACE, margin=-18):          # 얼굴 위엔 금지
            continue
        if math.dist((x, y), HAND[:2]) < HAND[2] + 26:   # 손 위에도 금지
            continue
        if any(math.dist((x, y), p) < 74 for p in placed):
            continue

        placed.append((x, y))
        motif = MOTIFS[rnd.randrange(3)]
        out.append(motif(x, y, rnd.uniform(0.82, 1.12), rnd.uniform(-28, 28)))
    return "\n".join(out)


def build_svg(background=True, view_box=None):
    hcx, hcy, hrx, hry = HOOD
    fcx, fcy, frx, fry = FACE
    ccx, ccy, crx, cry = COLLAR
    hx, hy, hr = HAND
    vb = view_box or f"0 0 {W} {H}"
    bg = (f'<rect width="{W}" height="{H}" fill="{BG}"/>'
          f'<circle cx="400" cy="430" r="330" fill="#FDEDF0" opacity="0.55"/>') if background else ""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{vb}">
  <defs>
    <clipPath id="faceClip">
      <ellipse cx="{fcx}" cy="{fcy}" rx="{frx}" ry="{fry}"/>
    </clipPath>
    <clipPath id="hoodClip">
      <ellipse cx="{hcx}" cy="{hcy}" rx="{hrx}" ry="{hry}"/>
    </clipPath>
    <clipPath id="canvasClip">
      <rect x="0" y="0" width="{W}" height="{H}"/>
    </clipPath>
    <!-- 후드가 얼굴에 드리우는 부드러운 그늘 -->
    <radialGradient id="faceShade" cx="0.5" cy="0.45" r="0.62">
      <stop offset="0.55" stop-color="{SKIN_SH}" stop-opacity="0"/>
      <stop offset="1" stop-color="{SKIN_SH}" stop-opacity="0.55"/>
    </radialGradient>
  </defs>

  {bg}

  <g clip-path="url(#canvasClip)">

    <!-- 몸통(감싼 담요) -->
    <path d="M {BODY_L} {BODY_BOT} C {BODY_L} 660, 250 {BODY_TOP}, 400 {BODY_TOP}
             C 550 {BODY_TOP}, {BODY_R} 660, {BODY_R} {BODY_BOT} Z" fill="{FABRIC}"/>
    <path d="M {BODY_L} {BODY_BOT} C {BODY_L} 660, 250 {BODY_TOP}, 400 {BODY_TOP}
             C 330 616, 268 700, 252 {BODY_BOT} Z" fill="{FABRIC_SH}" opacity="0.55"/>

    <!-- 후드(머리에 두른 거즈) -->
    <ellipse cx="{hcx}" cy="{hcy}" rx="{hrx}" ry="{hry}" fill="{FABRIC_SH}"/>
    <ellipse cx="{hcx - 8}" cy="{hcy - 8}" rx="{hrx - 13}" ry="{hry - 13}" fill="{FABRIC}"/>

    <!-- 후드 접힘선 -->
    <g clip-path="url(#hoodClip)" fill="none" stroke="{FOLD}" stroke-width="4.5"
       stroke-linecap="round" opacity="0.75">
      <path d="M 214 300 C 268 214, 352 176, 432 178"/>
      <path d="M 186 392 C 218 300, 300 232, 396 218"/>
      <path d="M 592 300 C 556 232, 486 190, 424 182"/>
      <path d="M 618 400 C 606 306, 540 236, 452 214"/>
      <path d="M 200 486 C 176 424, 180 356, 196 314"/>
    </g>

    <!-- 얼굴 -->
    <ellipse cx="{fcx}" cy="{fcy}" rx="{frx}" ry="{fry}" fill="{SKIN}"/>
    <g clip-path="url(#faceClip)">
      <!-- 후드가 드리운 부드러운 그늘 (얼굴 가장자리) -->
      <ellipse cx="{fcx}" cy="{fcy}" rx="{frx}" ry="{fry}" fill="url(#faceShade)"/>
      <!-- 후드 아래 살짝 보이는 배냇머리 -->
      <path d="M 236 336 C 262 258, 322 224, 400 226 C 478 228, 540 262, 566 340
               C 528 288, 476 268, 428 276 C 396 282, 372 296, 340 292
               C 300 288, 264 302, 236 336 Z"
            fill="{HAIR}" opacity="0.9"/>
      <path d="M 300 292 C 282 276, 268 272, 252 276" fill="none" stroke="{HAIR}"
            stroke-width="5" stroke-linecap="round" opacity="0.8"/>
      <path d="M 500 286 C 520 272, 536 272, 550 280" fill="none" stroke="{HAIR}"
            stroke-width="5" stroke-linecap="round" opacity="0.8"/>
    </g>

    <!-- 턱 아래로 감싼 천 -->
    <ellipse cx="{ccx}" cy="{ccy}" rx="{crx}" ry="{cry}" fill="{FABRIC}"/>
    <path d="M 176 664 C 258 622, 542 622, 624 664 C 540 674, 260 674, 176 664 Z"
          fill="{FABRIC_SH}" opacity="0.7"/>
    <path d="M 210 692 C 296 646, 504 646, 590 692" fill="none" stroke="{FOLD}"
          stroke-width="4.5" stroke-linecap="round" opacity="0.55"/>
    <path d="M 256 742 C 330 706, 470 706, 544 742" fill="none" stroke="{FOLD}"
          stroke-width="4" stroke-linecap="round" opacity="0.4"/>

    <!-- 눈썹 -->
    <path d="M 288 380 C 306 366, 336 364, 352 372" fill="none" stroke="{BROW}"
          stroke-width="6" stroke-linecap="round" opacity="0.55"/>
    <path d="M 448 372 C 466 364, 496 366, 512 380" fill="none" stroke="{BROW}"
          stroke-width="6" stroke-linecap="round" opacity="0.55"/>

    <!-- 눈 -->
    <ellipse cx="322" cy="440" rx="34" ry="40" fill="{EYE}"/>
    <ellipse cx="478" cy="440" rx="34" ry="40" fill="{EYE}"/>
    <circle cx="311" cy="426" r="11.5" fill="#FFFFFF" opacity="0.95"/>
    <circle cx="467" cy="426" r="11.5" fill="#FFFFFF" opacity="0.95"/>
    <circle cx="332" cy="456" r="5" fill="#FFFFFF" opacity="0.5"/>
    <circle cx="488" cy="456" r="5" fill="#FFFFFF" opacity="0.5"/>

    <!-- 볼터치 -->
    <ellipse cx="272" cy="512" rx="36" ry="24" fill="{BLUSH}" opacity="0.45"/>
    <ellipse cx="528" cy="512" rx="36" ry="24" fill="{BLUSH}" opacity="0.45"/>

    <!-- 코 -->
    <path d="M 388 498 C 396 508, 406 508, 414 500" fill="none" stroke="{SKIN_SH}"
          stroke-width="6" stroke-linecap="round"/>

    <!-- 살짝 벌린 입 -->
    <ellipse cx="400" cy="552" rx="23" ry="18" fill="{MOUTH}"/>
    <ellipse cx="400" cy="558" rx="14" ry="9" fill="{MOUTH_IN}" opacity="0.65"/>

    <!-- 담요 밖으로 빼꼼 나온 주먹 -->
    <g transform="translate({hx},{hy})">
      <circle cx="0" cy="0" r="{hr}" fill="{SKIN}"/>
      <g fill="none" stroke="{SKIN_SH}" stroke-width="5" stroke-linecap="round" opacity="0.65">
        <path d="M -40 -22 C -20 -34, 8 -36, 28 -28"/>
        <path d="M -46 2 C -24 -8, 6 -10, 30 -2"/>
        <path d="M -42 26 C -22 18, 6 16, 28 24"/>
      </g>
      <path d="M -34 -30 C -46 -14, -46 8, -36 22" fill="none" stroke="{SKIN_SH}"
            stroke-width="5" stroke-linecap="round" opacity="0.5"/>
    </g>

    <!-- 거즈 과일 무늬 -->
    {scatter_pattern()}

  </g>
</svg>"""


def render(svg, path, size):
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=path,
                     output_width=size, output_height=size)
    print("saved:", path)


def circle_crop(src, dst, size=600):
    """프로필용: 원형으로 잘라낸 PNG (투명 바깥)."""
    from PIL import Image, ImageDraw
    img = Image.open(src).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    img.putalpha(mask.resize((size, size), Image.LANCZOS))
    img.save(dst)
    print("saved:", dst)


def main():
    # 1) 기본형 (크림 배경)
    svg = build_svg()
    with open("assets/ddudu_character.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    render(svg, "assets/ddudu_character.png", 800)

    # 2) 투명 배경 (사진 위에 올리거나 다른 배경과 합성용)
    render(build_svg(background=False), "assets/ddudu_character_transparent.png", 800)

    # 3) 프로필용 원형 아이콘 (얼굴 위주로 확대)
    render(build_svg(view_box="152 182 496 496"), "assets/_profile_square.png", 600)
    circle_crop("assets/_profile_square.png", "assets/ddudu_character_profile.png", 600)
    import os
    os.remove("assets/_profile_square.png")


if __name__ == "__main__":
    main()
