🎮 PVR.CCZ & Plist Batch Extractor
Este é um script de automação em Python desenvolvido para processar em lote (batch) arquivos de atlas de sprites comprimidos em formato .pvr.ccz acompanhados de seus respectivos arquivos .plist.

O diferencial desta ferramenta é a integração com o TexturePacker CLI, permitindo a extração de texturas mesmo quando utilizam compressão de hardware como PVRTC2, que bibliotecas de imagem comuns (como Pillow) não conseguem decodificar nativamente.

🚀 Funcionalidades
Processamento em Lote: Varre diretórios inteiros em busca de pares .plist / .pvr.ccz.

Decodificação Avançada: Suporte a formatos PVRTC (2 e 4 bits) via CLI.

Recorte Automático: Utiliza as coordenadas do Plist para extrair cada sprite individualmente.

Suporte a Rotação: Identifica e corrige automaticamente sprites que foram rotacionados no atlas para economia de espaço.

Organização Inteligente: Cria pastas separadas para cada atlas processado.

🛠️ Pré-requisitos
Antes de rodar o script, você precisará de:

Python 3.x instalado.

Pillow (PIL): Para manipulação e recorte de imagens.

Bash
pip install Pillow
TexturePacker CLI: O software TexturePacker deve estar instalado e seu executável configurado no PATH do sistema.

📦 Como Usar
Clone este repositório:

Bash
git clone https://github.com/seu-usuario/pvr-ccz-extractor.git
Coloque seus arquivos .plist e .pvr.ccz na pasta do script (ou aponte para o diretório desejado).

Execute o script:

Bash
python extractor.py
⚠️ Tratamento de Erros Comuns
Exit Status 10: Geralmente indica que o arquivo .pvr.ccz está protegido por uma Content Protection Key. Se você possuir a chave de 128 bits, ela deve ser adicionada aos argumentos do comando no script.

Command 'TexturePacker' not found: Verifique se o TexturePacker está acessível via terminal/linha de comando.

👨‍🏫 Sobre o Projeto
Este projeto foi desenvolvido como parte das atividades de automação e ferramentas de design no PROTIP (Laboratório de Prototipagem) da Universidade de Brasília (UnB), sob coordenação do Prof. Miguel Eduardo Gutierrez Paredes.


Link para baixar e testar o TexturePacker 7. educativo Full Mega
https://link-center.net/686699/3YpRWt2KqobY
