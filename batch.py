import os
import re
import subprocess
import sys
from PIL import Image
from xml.etree import ElementTree


def get_dict(node):
    """Converte o XML do Plist em dicionário Python."""
    d = {}
    for i in range(0, len(node), 2):
        key = node[i].text
        val = node[i + 1]
        if val.tag == 'string':
            d[key] = val.text
        elif val.tag == 'dict':
            d[key] = get_dict(val)
        elif val.tag == 'true':
            d[key] = True
        elif val.tag == 'false':
            d[key] = False
        elif val.tag == 'integer':
            d[key] = int(val.text)
    return d


def process_atlas(plist_path):
    base_name = os.path.splitext(plist_path)[0]
    ccz_path = base_name + '.pvr.ccz'
    temp_png = base_name + "_TEMP_CONVERTED.png"

    if not os.path.exists(ccz_path):
        return False

    print(f"📦 Decodificando PVRTC2: {os.path.basename(ccz_path)}...")

    try:
        # Comando para converter PVR.CCZ para PNG usando o TexturePacker
        # Usamos --content-protection ou apenas o path se não houver chave
        cmd = [
            'TexturePacker',
            ccz_path,
            '--sheet', temp_png,
            '--data', 'null.plist',  # Arquivo dummy
            '--allow-free-size',
            '--no-trim'
        ]

        # Executa a conversão (stdout=DEVNULL para limpar o terminal)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists(temp_png):
            print(f"  ❌ Falha: O TexturePacker não gerou o PNG.")
            return False

        # Abrir imagem convertida e recortar
        img = Image.open(temp_png)
        tree = ElementTree.parse(plist_path)
        root = get_dict(tree.getroot()[0])
        frames = root.get('frames', {})

        output_dir = base_name + "_extraido"
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        for sprite_name, info in frames.items():
            rect_str = info.get('frame') or info.get('textureRect')
            coords = list(map(int, re.findall(r'\d+', rect_str)))
            x, y, w, h = coords

            rotated = info.get('rotated', False)
            box = (x, y, x + (h if rotated else w), y + (w if rotated else h))

            sprite = img.crop(box)
            if rotated:
                sprite = sprite.rotate(90, expand=True)

            clean_name = os.path.basename(sprite_name)
            if not clean_name.lower().endswith('.png'): clean_name += '.png'
            sprite.save(os.path.join(output_dir, clean_name))

        print(f"  ✅ Sucesso: {len(frames)} sprites em '{output_dir}'")

        # Limpeza de arquivos temporários
        img.close()
        os.remove(temp_png)
        if os.path.exists('null.plist'): os.remove('null.plist')
        return True

    except FileNotFoundError:
        print("  ❌ Erro: Comando 'TexturePacker' não encontrado. Instale-o e adicione ao PATH.")
        return False
    except Exception as e:
        print(f"  💥 Erro inesperado: {e}")
        return False


def main():
    folder = "."
    plists = [f for f in os.listdir(folder) if f.lower().endswith('.plist')]

    if not plists:
        print("Nenhum arquivo .plist encontrado.")
        return

    sucessos = 0
    for p in plists:
        if process_atlas(p): sucessos += 1

    print(f"\n🚀 Finalizado! {sucessos} atlas processados.")


if __name__ == '__main__':
    main()