import os
import re
import sys
from PIL import Image
from xml.etree import ElementTree


def GetDict(node):
    d = {}
    for i in range(len(node)):
        if node[i].tag == 'key':
            key = node[i].text
            val = node[i + 1]
            if val.tag == 'string':
                d[key] = val.text
            elif val.tag == 'integer':
                d[key] = int(val.text)
            elif val.tag == 'dict':
                d[key] = GetDict(val)
            elif val.tag == 'false':
                d[key] = False
            elif val.tag == 'true':
                d[key] = True
    return d


def unpack_plist(plist_path):
    path_dir = os.path.dirname(plist_path)
    file_name = os.path.basename(plist_path).replace('.plist', '')
    img_path = os.path.join(path_dir, file_name + '.png')

    if not os.path.exists(img_path):
        print(f"Erro: Arquivo de imagem {img_path} não encontrado!")
        return

    tree = ElementTree.parse(plist_path)
    root_dict = GetDict(tree.getroot()[0])
    frames = root_dict['frames']
    img = Image.open(img_path)

    output_dir = os.path.join(path_dir, file_name + "_extraido")
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    for name, data in frames.items():
        # Formato comum: {{x,y},{w,h}}
        rect_str = data['frame'] if 'frame' in data else data['textureRect']
        rect = re.findall(r'\d+', rect_str)
        x, y, w, h = map(int, rect)

        # Rotação (alguns atlas giram o sprite para economizar espaço)
        rotated = data.get('rotated', False)

        box = (x, y, x + (h if rotated else w), y + (w if rotated else h))
        sprite = img.crop(box)

        if rotated:
            sprite = sprite.rotate(90, expand=True)

        sprite.save(os.path.join(output_dir, name))
        print(f"Extraído: {name}")


if __name__ == '__main__':
    # Digite o nome do seu arquivo aqui ou passe via terminal
    unpack_plist("tower_type_drone-hd.plist")