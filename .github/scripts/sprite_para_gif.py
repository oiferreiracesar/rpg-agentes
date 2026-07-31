"""
Converte um sprite sheet (grade de quadros num único PNG) em GIF(s) animados.

Uso:
    python3 sprite_para_gif.py entrada.png --cols 4 --rows 4 --duracao 120

Parâmetros principais:
    --cols / --rows      Quantas colunas e linhas tem a grade do sprite sheet
    --linha              Se só quiser animar UMA linha específica (ex: "0" pra
                          primeira linha). Se omitido, gera um GIF por linha.
    --duracao             Milissegundos por quadro (padrão: 120ms = ~8 fps)
    --cor-fundo           Cor de fundo a remover (chroma key), formato "R,G,B".
                          Se omitido, tenta detectar automaticamente (usa a cor
                          do canto superior esquerdo do primeiro quadro).
    --sem-remover-fundo   Não remove fundo nenhum, mantém sólido no GIF.
    --saida                Pasta de saída (padrão: mesma pasta da imagem de entrada)
"""

import argparse
import os
import sys

from PIL import Image


def detectar_cor_fundo(sheet, cell_w, cell_h):
    """Usa o pixel do canto superior esquerdo do sprite sheet inteiro como
    referência de cor de fundo — funciona bem quando o fundo é sólido e
    uniforme atrás de todos os quadros."""
    return sheet.getpixel((0, 0))[:3]


def remover_fundo(frame, cor_fundo, tolerancia=30):
    """Converte para RGBA e torna transparente qualquer pixel próximo da
    cor de fundo informada (chroma key com tolerância, pra suavizar bordas
    anti-aliased)."""
    frame = frame.convert("RGBA")
    pixels = frame.load()
    r0, g0, b0 = cor_fundo
    for y in range(frame.height):
        for x in range(frame.width):
            r, g, b, a = pixels[x, y]
            if abs(r - r0) <= tolerancia and abs(g - g0) <= tolerancia and abs(b - b0) <= tolerancia:
                pixels[x, y] = (r, g, b, 0)
    return frame


def fatiar_sheet(sheet, cols, rows):
    """Divide o sprite sheet numa matriz [linha][coluna] de quadros individuais."""
    cell_w = sheet.width // cols
    cell_h = sheet.height // rows
    matriz = []
    for r in range(rows):
        linha = []
        for c in range(cols):
            box = (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)
            linha.append(sheet.crop(box))
        matriz.append(linha)
    return matriz, cell_w, cell_h


def quadro_esta_vazio(frame, cor_fundo, tolerancia=30):
    """Detecta se um quadro é só fundo (célula vazia na grade — comum em
    sprite sheets onde nem toda linha/coluna está preenchida)."""
    frame_rgb = frame.convert("RGB")
    r0, g0, b0 = cor_fundo
    amostras = 0
    diferentes = 0
    for x in range(0, frame_rgb.width, max(1, frame_rgb.width // 12)):
        for y in range(0, frame_rgb.height, max(1, frame_rgb.height // 12)):
            r, g, b = frame_rgb.getpixel((x, y))
            amostras += 1
            if not (abs(r - r0) <= tolerancia and abs(g - g0) <= tolerancia and abs(b - b0) <= tolerancia):
                diferentes += 1
    return diferentes == 0


def montar_gif(frames, caminho_saida, duracao_ms, remover_bg, cor_fundo):
    processados = []
    for f in frames:
        if remover_bg:
            f = remover_fundo(f, cor_fundo)
        processados.append(f.convert("RGBA"))

    if remover_bg:
        processados[0].save(
            caminho_saida,
            save_all=True,
            append_images=processados[1:],
            duration=duracao_ms,
            loop=0,
            disposal=2,
            transparency=0,
        )
    else:
        rgb_frames = [f.convert("RGB") for f in processados]
        rgb_frames[0].save(
            caminho_saida,
            save_all=True,
            append_images=rgb_frames[1:],
            duration=duracao_ms,
            loop=0,
        )


def main():
    parser = argparse.ArgumentParser(description="Converte sprite sheet em GIF(s) animados.")
    parser.add_argument("entrada", help="Caminho do PNG do sprite sheet")
    parser.add_argument("--cols", type=int, required=True, help="Número de colunas na grade")
    parser.add_argument("--rows", type=int, required=True, help="Número de linhas na grade")
    parser.add_argument("--linha", type=int, default=None, help="Gerar só a linha X (0-indexado). Se omitido, gera todas.")
    parser.add_argument("--duracao", type=int, default=120, help="Duração de cada quadro em ms (padrão 120)")
    parser.add_argument("--cor-fundo", type=str, default=None, help='Cor a remover, formato "R,G,B"')
    parser.add_argument("--sem-remover-fundo", action="store_true", help="Não remove o fundo, mantém sólido")
    parser.add_argument("--saida", type=str, default=None, help="Pasta de saída")
    args = parser.parse_args()

    if not os.path.exists(args.entrada):
        print(f"ERRO: arquivo '{args.entrada}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    sheet = Image.open(args.entrada)
    matriz, cell_w, cell_h = fatiar_sheet(sheet, args.cols, args.rows)

    remover_bg = not args.sem_remover_fundo
    if args.cor_fundo:
        cor_fundo = tuple(int(v) for v in args.cor_fundo.split(","))
    else:
        cor_fundo = detectar_cor_fundo(sheet, cell_w, cell_h)

    pasta_saida = args.saida or os.path.dirname(os.path.abspath(args.entrada))
    os.makedirs(pasta_saida, exist_ok=True)
    nome_base = os.path.splitext(os.path.basename(args.entrada))[0]

    linhas_para_gerar = [args.linha] if args.linha is not None else list(range(args.rows))

    print(f"Cor de fundo detectada/usada: RGB{cor_fundo}")
    print(f"Grade: {args.cols} colunas x {args.rows} linhas, célula {cell_w}x{cell_h}px\n")

    for r in linhas_para_gerar:
        if r < 0 or r >= args.rows:
            print(f"AVISO: linha {r} fora do intervalo (0 a {args.rows - 1}), pulando.", file=sys.stderr)
            continue

        frames = matriz[r]
        frames_validos = [f for f in frames if not quadro_esta_vazio(f, cor_fundo)]

        if not frames_validos:
            print(f"Linha {r}: nenhum quadro com conteúdo (célula vazia), pulando.")
            continue

        caminho_saida = os.path.join(pasta_saida, f"{nome_base}_linha{r}.gif")
        montar_gif(frames_validos, caminho_saida, args.duracao, remover_bg, cor_fundo)
        print(f"Linha {r}: {len(frames_validos)} quadro(s) válido(s) -> {caminho_saida}")


if __name__ == "__main__":
    main()
