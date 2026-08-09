import argparse
import json
import os
import random
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def normalize(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def verificar(elementos, ordem_correta):
    """Confirma que 'ordem_correta' é de fato uma reordenação válida de
    'elementos' — mesmos itens, mesma quantidade, sem inventar nem sumir com
    nenhum. Evita o caso de a IA escrever a ordem certa com erro de digitação
    que não bate mais com a lista real de elementos."""
    if len(elementos) != len(ordem_correta):
        return False, "quantidade de itens diferente entre 'elementos' e 'ordem_correta'"
    if sorted(elementos) != sorted(ordem_correta):
        return False, "os itens de 'ordem_correta' não são exatamente os mesmos de 'elementos' (conferir digitação)"
    if len(set(elementos)) != len(elementos):
        return False, "'elementos' tem itens duplicados — cada carta precisa ser única pra não haver ambiguidade"
    return True, ""


def make_pdf_cartas(path, titulo, elementos, embaralhados, pista, ordem_correta, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre — ordem correta" if with_answers else "Recorte e reordene as cartas"
    c.drawCentredString(width / 2, height - 80, subtitle)

    if pista and not with_answers:
        y_pista = height - 105
        c.drawCentredString(width / 2, y_pista, f"Pista: {pista}")

    lista = ordem_correta if with_answers else embaralhados

    card_w, card_h = 160, 90
    cols = 3
    start_x = (width - (cols * card_w + (cols - 1) * 20)) / 2
    start_y = height - 160

    for i, item in enumerate(lista):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + 20)
        y = start_y - row * (card_h + 20)

        c.rect(x, y - card_h, card_w, card_h, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 11)
        palavras = item.split()
        linhas, linha_atual = [], ""
        for palavra in palavras:
            teste = (linha_atual + " " + palavra).strip()
            if c.stringWidth(teste, "Helvetica-Bold", 11) < card_w - 16:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        linhas = linhas[:3]

        text_y = y - card_h / 2 + (len(linhas) - 1) * 7
        for linha in linhas:
            c.drawCentredString(x + card_w / 2, text_y, linha)
            text_y -= 14

        if with_answers:
            c.setFont("Helvetica", 8)
            c.drawString(x + 4, y - 12, f"{i + 1}º")

    c.showPage()
    c.save()


def slugify(text):
    text = normalize(text).lower().replace("_", " ")
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

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "sequencia_logica"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo sequencia_logica encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for i, d in enumerate(dinamicas):
        dados = d.get("dados", {})
        elementos = dados.get("elementos", [])
        ordem_correta = dados.get("ordem_correta", [])
        pista = dados.get("pista_in_fiction", "")
        titulo = d.get("titulo", "Sequência Lógica")

        if not elementos or not ordem_correta:
            print(f"AVISO: '{titulo}' sem 'elementos' ou 'ordem_correta', pulando.", file=sys.stderr)
            continue

        ok, motivo = verificar(elementos, ordem_correta)
        if not ok:
            print(f"ERRO: '{titulo}' — {motivo}. Pulando.", file=sys.stderr)
            continue

        rnd = random.Random(i + 7)
        embaralhados = elementos[:]
        tentativas = 0
        while embaralhados == ordem_correta and tentativas < 20:
            rnd.shuffle(embaralhados)
            tentativas += 1

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf_cartas(p1, titulo, elementos, embaralhados, pista, ordem_correta, with_answers=False)
        make_pdf_cartas(p2, titulo, elementos, embaralhados, pista, ordem_correta, with_answers=True)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: {len(elementos)} itens batem entre elementos e ordem correta)")


if __name__ == "__main__":
    main()
