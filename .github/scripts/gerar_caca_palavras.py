import json
import os
import random
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (-1, 1)]


def make_grid(size):
    return [[None for _ in range(size)] for _ in range(size)]


def can_place(grid, size, word, row, col, dr, dc):
    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i
        if not (0 <= r < size and 0 <= c < size):
            return False
        if grid[r][c] is not None and grid[r][c] != ch:
            return False
    return True


def place_word(grid, size, word, placements, attempts=800):
    for _ in range(attempts):
        dr, dc = random.choice(DIRECTIONS)
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        if can_place(grid, size, word, row, col, dr, dc):
            for i, ch in enumerate(word):
                r, c = row + dr * i, col + dc * i
                grid[r][c] = ch
            placements.append({"word": word, "row": row, "col": col, "dr": dr, "dc": dc})
            return True
    return False


def fill_random(grid, size):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in range(size):
        for c in range(size):
            if grid[r][c] is None:
                grid[r][c] = random.choice(letters)


def verify_word_in_grid(grid, word, row, col, dr, dc):
    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i
        if grid[r][c] != ch:
            return False
    return True


def normalize(word):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return word.upper().translate(repl).replace(" ", "")


def build_puzzle(words, size, seed):
    random.seed(seed)
    words = [normalize(w) for w in words]
    grid = make_grid(size)
    placements = []
    for w in sorted(words, key=len, reverse=True):
        if not place_word(grid, size, w, placements):
            raise RuntimeError(f"Nao coube no grid {size}x{size}: {w} (aumente o tamanho da grade ou reduza as palavras)")
    fill_random(grid, size)
    for p in placements:
        ok = verify_word_in_grid(grid, p["word"], p["row"], p["col"], p["dr"], p["dc"])
        if not ok:
            raise RuntimeError(f"Falha de verificacao para a palavra: {p['word']}")
    return grid, placements, words, size


def draw_grid(c, grid, size, x0, y0, cell, highlight=None):
    highlight = highlight or []
    c.setFont("Courier-Bold", max(8, int(220 / size)))
    for r in range(size):
        for col in range(size):
            x = x0 + col * cell
            y = y0 - r * cell
            if (r, col) in highlight:
                c.setFillColor(HexColor("#f5c542"))
                c.rect(x - cell / 2 + 2, y - cell / 2 + 2, cell - 4, cell - 4, fill=1, stroke=0)
                c.setFillColor(HexColor("#1a1a1a"))
            else:
                c.setFillColor(HexColor("#1a1a1a"))
            c.drawCentredString(x, y - 4, grid[r][col])
    c.setStrokeColor(HexColor("#888888"))
    c.rect(x0 - cell / 2, y0 - (size - 1) * cell - cell / 2, size * cell, size * cell, fill=0, stroke=1)


def highlighted_cells(placements):
    cells = set()
    for p in placements:
        for i in range(len(p["word"])):
            r, c = p["row"] + p["dr"] * i, p["col"] + p["dc"] * i
            cells.add((r, c))
    return cells


def make_pdf(path, titulo, grid, size, placements, words, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Encontre as palavras ocultas"
    c.drawCentredString(width / 2, height - 80, subtitle)

    cell = min(26, 620 / size)
    x0 = width / 2 - (size - 1) * cell / 2
    y0 = height - 130

    highlight = highlighted_cells(placements) if with_answers else None
    draw_grid(c, grid, size, x0, y0, cell, highlight)

    c.setFont("Helvetica-Bold", 11)
    ly = y0 - size * cell - 30
    c.drawString(60, ly, "Palavras a encontrar:")
    c.setFont("Helvetica", 10)
    col_x = [60, 220, 380, 460]
    words_sorted = sorted(words)
    for i, w in enumerate(words_sorted):
        cx = col_x[i % len(col_x)]
        cy = ly - 18 - (i // len(col_x)) * 16
        c.drawString(cx, cy, "• " + w)

    c.showPage()
    c.save()


def slugify(text):
    text = normalize(text).lower().replace("_", " ")
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def main():
    path = "output/10-puzzles.json"
    if not os.path.exists(path):
        print("output/10-puzzles.json não encontrado — nada a gerar (ok, esse passo é opcional).", file=sys.stderr)
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "caca_palavras"]
    if not dinamicas:
        print("Nenhuma dinâmica do tipo caca_palavras encontrada em 10-puzzles.json.")
        return

    os.makedirs("output/puzzles", exist_ok=True)

    for i, d in enumerate(dinamicas):
        dados = d.get("dados", {})
        palavras = dados.get("palavras", [])
        tamanho = dados.get("tamanho_grade_sugerido", 14)
        titulo = d.get("titulo", f"Caça-palavras {i+1}")

        if len(palavras) < 3:
            print(f"AVISO: '{titulo}' tem menos de 3 palavras, pulando.", file=sys.stderr)
            continue

        try:
            grid, placements, words, size = build_puzzle(palavras, tamanho, seed=i + 7)
        except RuntimeError as e:
            print(f"AVISO: não consegui montar '{titulo}' com grade {tamanho}x{tamanho} ({e}). Tentando grade maior...", file=sys.stderr)
            try:
                grid, placements, words, size = build_puzzle(palavras, tamanho + 4, seed=i + 7)
            except RuntimeError as e2:
                print(f"ERRO: desisti de '{titulo}': {e2}", file=sys.stderr)
                continue

        slug = slugify(titulo)
        p1 = f"output/puzzles/{slug}_JOGADORES.pdf"
        p2 = f"output/puzzles/{slug}_GABARITO.pdf"
        make_pdf(p1, titulo, grid, size, placements, words, with_answers=False)
        make_pdf(p2, titulo, grid, size, placements, words, with_answers=True)
        print(f"OK: '{titulo}' -> {p1} e {p2} (grade {size}x{size}, {len(words)} palavras verificadas)")


if __name__ == "__main__":
    main()
