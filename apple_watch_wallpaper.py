import json
import logging
from re import I
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import random
import uuid

import create_icon

# apple watchの画面サイズ 272x340

def main():
    with open('pokesprite/data/pokemon.json', encoding='utf-8') as f:
        json_content = json.load(f)
    path_list = list(create_icon.get_image_path(json_content))
    sampled_list = random.sample(path_list, 500)
    for input_path, output_path in sampled_list:
        img_base = Image.new('RGBA', (272, 340), (0, 0, 0, 255))
        img = Image.open(input_path)
        img = create_icon.trim_image(img)
        # img = img.convert('RGB')
        # img = img.resize((100, 100), Image.NEAREST)
        img_base.paste(img, ((272-128)//2,(340-128)//2+35), mask=img)
        print(output_path)
        draw = ImageDraw.Draw(img_base)
        font = ImageFont.truetype("PixelMplus10-Regular.ttf", 20)
        msg = output_path.split('/')[-1][len('pokemon-'):-1*(len('.png'))]
        w, h = draw.textsize(msg, font=font)
        draw.text(((272-w)//2,(340-h)//2+110), msg,font=font)
        # draw.text((135,200), "にほんご" ,(255,255,255),)
        output_path_wallpaper = f'output_wallpaper/{uuid.uuid4()}.png'
        img_base.save(output_path_wallpaper)
        # img_base.save('temp.png')


if __name__ == '__main__':
    main()