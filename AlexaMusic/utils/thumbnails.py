# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
Copyright (c) 2021 ~ Present Team Alexa <https://github.com/TheTeamAlexa>

This program is free software: you can redistribute it and can modify
as you want or you can collabe if you have new ideas.
"""


import os
import re
import textwrap

import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL

def change_image_size(max_width, max_height, image):
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))


def draw_text(draw, title, views, duration, status, font, font2, arial, name_font):
    para = textwrap.wrap(title, width=30)

    draw.text((5, 5), "TSERIES MUSIC", fill="white", font=name_font)
    draw.text(
        (600, 150),
        status,
        fill="white",
        stroke_width=3,
        stroke_fill="black",
        font=font2,
    )

    for j, line in enumerate(para):
        y_position = 280 if j == 0 else 340
        draw.text(
            (600, y_position),
            line,
            fill="white",
            stroke_width=1,
            stroke_fill="black",
            font=font,
        )

    draw.text((600, 450), f"Views: {views[:23]}", (255, 255, 255), font=arial)
    draw.text((600, 500), f"Duration: {duration[:23]} Mins", (255, 255, 255), font=arial)
    draw.text((600, 550), f"Owner: TEAM ATOMIC", (255, 255, 255), font=arial)


async def fetch_video_details(videoid):
    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
        title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        return title, duration, thumbnail, views, channel


async def download_thumbnail(thumbnail_url, videoid):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                await f.write(await resp.read())
                await f.close()


def process_image(videoid, title, duration, views, status):
    youtube = Image.open(f"cache/thumb{videoid}.png")
    image1 = change_image_size(1280, 720, youtube)
    image2 = image1.convert("RGBA")

    background = image2.filter(filter=ImageFilter.GaussianBlur(15))
    background = ImageEnhance.Brightness(background).enhance(0.6)

    Xcenter, Ycenter = youtube.width / 2, youtube.height / 2
    logo = youtube.crop((Xcenter - 250, Ycenter - 250, Xcenter + 250, Ycenter + 250))
    logo.thumbnail((520, 520), Image.LANCZOS)
    logo = ImageOps.expand(logo, border=15, fill="white")
    background.paste(logo, (50, 100))

    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("assets/font2.ttf", 40)
    font2 = ImageFont.truetype("assets/font2.ttf", 70)
    arial = ImageFont.truetype("assets/font2.ttf", 30)
    name_font = ImageFont.truetype("assets/font.ttf", 30)

    draw_text(draw, title, views, duration, status, font, font2, arial, name_font)

    background.save(f"cache/{videoid}.png")


async def generate_thumbnail(videoid, status="NOW PLAYING"):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    try:
        title, duration, thumbnail_url, views, _ = await fetch_video_details(videoid)
        await download_thumbnail(thumbnail_url, videoid)
        process_image(videoid, title, duration, views, status)
        os.remove(f"cache/thumb{videoid}.png")

        return f"cache/{videoid}.png"

    except Exception:
        return YOUTUBE_IMG_URL
