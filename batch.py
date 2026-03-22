import os
import re
import subprocess
import shutil
import io
import sys
from PIL import Image
from xml.etree import ElementTree


def get_dict(node):
    """Converte a estrutura XML do plist para um dicionário Python."""
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
    """
    Converte PVR.CCZ para PNG, move o sheet completo para a pasta de destino
    e extrai os sprites individuais.
    """
    base_name = os.path.splitext(plist_path)[0]
    ccz_path = base_name + '.pvr.ccz'
    # Nome do arquivo PNG que o TexturePacker vai gerar inicialmente
    temp_png = base_name + "_full_sheet.png"

    if not os.path.exists(ccz_path):
        print(f"  ⚠️  Aviso: .pvr.ccz não encontrado para {os.path.basename(plist_path)}")
        return False

    print(f"📦 Processando: {os.path.basename(base_name)}")

    try:
        # 1. CHAMADA AO TEXTUREPACKER (Decodificação PVRTC2)
        cmd = [
            'TexturePacker',
            ccz_path,
            '--sheet', temp_png,
            '--data', 'null.plist',
            '--allow-free-size',
            '--no-trim',
            '--extrude', '0',  # <--- Força extrusão zero
            '--border-padding', '0',  # <--- Remove padding de borda
            '--shape-padding', '0',  # <--- Remove padding entre sprites
            '--max-size', '4096'  # <--- Aumenta o limite para 4k se necessário
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  ❌ Erro no TexturePacker (Status {result.returncode}):")
            print(f"     {result.stderr.strip()}")
            return False

        if not os.path.exists(temp_png):
            print(f"  ❌ Falha: O PNG não foi gerado.")
            return False

        # 2. ORGANIZAÇÃO DE PASTAS
        output_dir = base_name + "_extraido"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Mover o spritesheet completo para dentro da pasta final
        final_sheet_path = os.path.join(output_dir, temp_png)
        shutil.move(temp_png, final_sheet_path)
        print(f"  🖼️  Spritesheet completo salvo em: {output_dir}")

        # 3. RECORTE DOS SPRITES (Pillow)
        img = Image.open(final_sheet_path)
        tree = ElementTree.parse(plist_path)
        root = get_dict(tree.getroot()[0])
        frames = root.get('frames', {})

        count = 0
        for sprite_name, info in frames.items():
            # Extração de coordenadas {{x,y},{w,h}}
            rect_str = info.get('frame') or info.get('textureRect')
            coords = list(map(int, re.findall(r'\d+', rect_str)))
            x, y, w, h = coords

            rotated = info.get('rotated', False)

            # Define a área de corte (left, top, right, bottom)
            if rotated:
                box = (x, y, x + h, y + w)
            else:
                box = (x, y, x + w, y + h)

            sprite = img.crop(box)

            if rotated:
                # TexturePacker geralmente rotaciona 90 graus anti-horário
                sprite = sprite.rotate(90, expand=True)

            # Salva o arquivo individual
            clean_name = os.path.basename(sprite_name)
            if not clean_name.lower().endswith('.png'):
                clean_name += '.png'

            sprite.save(os.path.join(output_dir, clean_name))
            count += 1

        img.close()
        print(f"  ✅ Sucesso: {count} sprites extraídos.")

        # Limpeza de arquivos residuais
        if os.path.exists('null.plist'):
            os.remove('null.plist')

        return True

    except FileNotFoundError:
        print("  ❌ Erro: Comando 'TexturePacker' não encontrado no PATH.")
        return False
    except Exception as e:
        print(f"  💥 Erro inesperado: {e}")
        return False


def main():
    print("-" * 50)
    print("🚀 PROTIP - EXTRATOR DE SPRITES (PVR.CCZ + PLIST)")
    print("-" * 50)

    # Pasta atual ou passada via argumento
    folder = sys.argv[1] if len(sys.argv) > 1 else "."

    plists = [f for f in os.listdir(folder) if f.lower().endswith('.plist')]

    if not plists:
        print("❌ Nenhum arquivo .plist encontrado.")
        return

    print(f"🔍 Encontrados {len(plists)} atlas para processar...\n")

    sucessos = 0
    for p in plists:
        if process_atlas(os.path.join(folder, p)):
            sucessos += 1

    print("\n" + "=" * 50)
    print(f"📊 RELATÓRIO FINAL: {sucessos} atlas processados com sucesso.")
    print("=" * 50)


if __name__ == '__main__':
    main()