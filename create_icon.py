import json
import logging
from re import I
import sys
from PIL import Image


def get_image_path(json_content):
    logger = logging.getLogger(name='app')
    items_iter = json_content.items().__iter__()
    INPUT_GEN8 = 'pokesprite/pokemon-gen8/regular/{}.png'
    INPUT_GEN8_F = 'pokesprite/pokemon-gen8/regular/female/{}.png'
    OUTPUT = 'output/pokemon-{}.png'
    f = open('output/example.txt', 'w', encoding='utf-8')
    while True:
        try:
            number_str, param = next(items_iter)
        except StopIteration:
            logger.debug('対象ファイルイテレーション終了')
            break
        # if number_str != '869':
        #     continue
        name_ja = param['slug']['jpn']
        name_en = param['slug']['eng']
        # gen7_forms = param['gen-7']['forms']
        gen8_forms = param['gen-8']['forms']
        for form_name, form_param in gen8_forms.items():
            # emojiに使えない記号を置換する。
            name_ja = name_ja.translate(str.maketrans(':', '-'))
            # form_nameに応じて画像ファイルと出力ファイル名を決定する。
            if form_name == '$':
                input_name = name_en
                output_name = name_ja
                logger.info('#%s %s', number_str, param["name"]["jpn"])
            elif 'is_alias_of' in form_param:
                # このformのファイルはなく、別のformのエイリアスになっている。
                if form_param["is_alias_of"] == '$':
                    # name_en を参照し、outputはform_nameを取る。
                    input_name = name_en
                    output_name = f'{name_ja}-{form_name}'
                    logger.info('#%s %s-%s', number_str, param["name"]["jpn"], form_name)
                else:
                    input_name = f'{name_en}-{form_param["is_alias_of"]}'
                    output_name = f'{name_ja}-{form_name}'
                    logger.info('#%s %s-%s', number_str, param["name"]["jpn"], form_param["is_alias_of"])
            else:
                input_name = f'{name_en}-{form_name}'
                output_name = f'{name_ja}-{form_name}'
                logger.info('#%s %s-%s', number_str, param["name"]["jpn"], form_name)
            yield (INPUT_GEN8.format(input_name), OUTPUT.format(output_name))
            # 使用例テキスト
            example_logical_name = param["name"]["jpn"] if form_name == '$' else form_name
            f.write(f':pokemon-{output_name}: {example_logical_name}\n')
            # メスのグラフィックがある場合
            if form_param.get('has_female'):
                logger.info('#%s %s メスあり', number_str, form_name)
                f.write(f':pokemon-{output_name}-f: {example_logical_name}-f\n')
                yield (INPUT_GEN8_F.format(input_name), OUTPUT.format(f'{output_name}-f'))
    f.close()


def trim_image(img):
    logger = logging.getLogger(name='app')
    # 最小矩形でクロップ
    img = img.convert('RGBA')
    alpha = img.split()[-1].point(lambda x: 0 if x < 230 else x)
    img_tmp = img.copy()
    img_tmp.putalpha(alpha)
    crop = img_tmp.split()[-1].getbbox()
    img = img.crop(crop)
    # 倍率2の倍数かつ128px以下で最大にリサイズ
    width, height = img.size
    longer = width if width > height else height
    # 倍率計算。拡大後128px以下になる整数倍率以下で最大の2の累乗
    MAX_IMAGE_SIZE = 128
    resize_rate = [2**i for i in range(7) if 2**i * longer < MAX_IMAGE_SIZE][-1]
    logger.debug('width %dpx height %dpx', width, height)
    logger.debug('%sが長い', "幅" if width > height else "高さ")
    logger.debug(
        '整数最大%d倍 -> 2の累乗最大%d倍 -> %d',
        MAX_IMAGE_SIZE // longer, resize_rate, longer * resize_rate
    )
    width_resized = width * resize_rate
    height_resized = height * resize_rate
    # ドット絵のシャープさを保ちたいのでNN
    img = img.resize((width_resized, height_resized), Image.NEAREST)
    # 縦横の長い方に合わせて正方形にする
    new_size = (longer * resize_rate,) * 2
    img_base = Image.new(img.mode, new_size, 0)
    paste_position = (
        0 if width >= height else (height_resized - width_resized) // 2,  # left
        0 if height >= width else (width_resized - height_resized) // 2,  # top
    )
    logger.debug('left %dpx top %dpx', paste_position[0], paste_position[1])
    img_base.paste(img, paste_position)
    img = img_base
    # ドット絵のシャープさを保ちたいのでNN
    img = img.resize((128, 128), Image.NEAREST)
    return img


def main():
    # ログ
    logger = logging.getLogger(name='app')
    logger.setLevel(logging.INFO)
    # logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    with open('pokesprite/data/pokemon.json', encoding='utf-8') as f:
        json_content = json.load(f)
    for input_path, output_path in get_image_path(json_content):
        img = Image.open(input_path)
        img = trim_image(img)
        img.save(output_path)


if __name__ == '__main__':
    main()
