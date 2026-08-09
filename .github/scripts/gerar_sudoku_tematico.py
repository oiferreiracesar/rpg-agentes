import argparse
import json
import os
import random
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# Solucao base valida de sudoku 4x4 (numeros 1-4, caixas 2x2) — ponto de
# partida fixo e ja confirmado correto; a variedade entre puzzles vem de
# permutar quais simbolos representam 1, 2, 3 e 4.
BASE_4X4 = [
    [1, 2, 3, 4],
    [3, 4, 1, 2],
    [2, 1, 4, 3],
    [4, 3, 2, 1],
]


def normalize(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def verificar_grade(grade):
    """Confere linha, coluna e caixa 2x2 — todas precisam ter os 4 símbolos
    únicos, sem repetição, senão não é um sudoku válido de verdade."""
    esperado = set(range(4))
    for linha in grade:
        if set(linha) != esperado:
            return False, "linha inválida"
    for c in range(4):
        coluna = {grade[r][c] for r in range(4)}
        if coluna != esperado:
            return False, "coluna inválida"
    for br in range(0, 4, 2):
        for bc in range(0, 4, 2):
            caixa = {grade[br + i][bc + j] for i in range(2) for j in range(2)}
            if caixa != esperado:
                return False, "caixa 2x2 inválida"
    return True, ""


def gerar_grade(simbolos, seed):
    """Permuta quais dos 4 símbolos correspondem a 1,2,3,4 no padrão base,
    de forma determinística a partir do seed — dá variedade sem precisar
    resolver o problema combinatório completo de gerar sudoku do zero."""
    rnd = random.Random(seed)
    ordem = list(range(4))
    rnd.shuffle(ordem)
    # ordem[i] diz qual simbolo representa o numero (i+1) no grid base
    mapa = {i + 1: simbolos[ordem[i]] for i in range(4)}
    grade_simbolos = [[mapa[BASE_4X4[r][c]] for c in range(4)] for r in range(4)]
    grade_indices = [[ordem.index(BASE_4X4[r][c] - 1) for c in range(4)] for r in range(4)]
    return grade_simbolos, grade_indices


def make_pdf(path, titulo, grade_simbolos, mascara_visivel, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Sudoku 4x4 — cada símbolo aparece uma vez por linha, coluna e quadrante"
    c.drawCentredString(width / 2, height - 80, subtitle)

    # Calcula o tamanho de fonte que faz o pior caso (palavra mais larga)
    # ainda caber dentro da célula, com uma margem — evita o texto vazar
    # pra célula vizinha quando o símbolo é uma palavra longa.
    palavra_mais_larga = max((s for linha in grade_simbolos for s in linha), key=len)
    cell = 75
    font_size = 22
    while c.stringWidth(palavra_mais_larga, "Helvetica-Bold", font_size) > cell - 10 and font_size > 8:
        font_size -= 1

    x0 = width / 2 - 2 * cell
    y0 = height - 130

    c.setLineWidth(1)
    for r in range(4):
        for col in range(4):
            x = x0 + col * cell
            y = y0 - r * cell
            c.rect(x, y - cell, cell, cell, stroke=1, fill=0)
            mostrar = with_answers or mascara_visivel[r][col]
            if mostrar:
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(x + cell / 2, y - cell * 0.6, grade_simbolos[r][col])

    # linhas grossas nas bordas dos quadrantes 2x2
    c.setLineWidth(3)
    c.line(x0, y0, x0 + 4 * cell, y0)
    c.line(x0, y0 - 4 * cell, x0 + 4 * cell, y0 - 4 * cell)
    c.line(x0, y0 - 2 * cell, x0 + 4 * cell, y0 - 2 * cell)
    c.line(x0, y0, x0, y0 - 4 * cell)
    c.line(x0 + 4 * cell, y0, x0 + 4 * cell, y0 - 4 * cell)
    c.line(x0 + 2 * cell, y0, x0 + 2 * cell, y0 - 4 * cell)

    c.showPage()
    c.save()


def slugify(text):
    text = normalize(text).lower()
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta onde estão os JSONs (padrão: output)")
    args = parser.parse_args()
    p = args.pasta

    path = os.path.join(p, "10-puzzles.json")
    if not os.path.exists(path):
        print(f"{path} não encontrado — nada a gerar (ok, esse passo é opcional).", file=sys.stderr)
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "sudoku_tematico"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo sudoku_tematico encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for i, d in enumerate(dinamicas):
        dados = d.get("dados", {})
        simbolos = dados.get("simbolos", [])
        titulo = d.get("titulo", "Sudoku Temático")

        if len(simbolos) != 4:
            print(f"AVISO: '{titulo}' precisa de exatamente 4 símbolos em 'simbolos' (veio {len(simbolos)}), pulando.", file=sys.stderr)
            continue

        grade_simbolos, _ = gerar_grade(simbolos, seed=i + 7)
        grade_numerica = [[simbolos.index(s) for s in linha] for linha in grade_simbolos]
        ok, motivo = verificar_grade(grade_numerica)
        if not ok:
            print(f"ERRO: '{titulo}' — grade gerada não é um sudoku válido ({motivo}). Pulando.", file=sys.stderr)
            continue

        rnd = random.Random(i + 100)
        mascara_visivel = [[rnd.random() < 0.5 for _ in range(4)] for _ in range(4)]
        # garante pelo menos 1 pista visivel por linha, senao fica impossivel
        for r in range(4):
            if not any(mascara_visivel[r]):
                mascara_visivel[r][rnd.randint(0, 3)] = True

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf(p1, titulo, grade_simbolos, mascara_visivel, with_answers=False)
        make_pdf(p2, titulo, grade_simbolos, mascara_visivel, with_answers=True)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: linhas, colunas e quadrantes válidos)")


if __name__ == "__main__":
    main()
