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


def embaralhar(palavra, seed, tentativas=50):
    """Embaralha as letras, garantindo que o resultado é genuinamente
    diferente da palavra original (evita o caso raro de embaralhar e a
    letra cair no mesmo lugar de novo, principalmente em palavras curtas)."""
    letras = list(palavra)
    if len(set(letras)) <= 1:
        # palavra de uma letra só ou todas iguais — nao da pra embaralhar
        return palavra, False
    rnd = random.Random(seed)
    for _ in range(tentativas):
        embaralhada = letras[:]
        rnd.shuffle(embaralhada)
        resultado = "".join(embaralhada)
        if resultado != palavra:
            return resultado, True
    return palavra, False


def make_pdf(path, titulo, dica, embaralhada, resposta, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Desembaralhe a palavra"
    c.drawCentredString(width / 2, height - 80, subtitle)

    c.setFont("Helvetica-Bold", 30)
    letras_espacadas = "  ".join(embaralhada)
    c.drawCentredString(width / 2, height - 160, letras_espacadas)

    if dica:
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(width / 2, height - 200, f"Dica: {dica}")

    if with_answers:
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 250, f"Resposta: {resposta}")

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

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "anagrama"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo anagrama encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for i, d in enumerate(dinamicas):
        dados = d.get("dados", {})
        palavra = dados.get("palavra_original", "")
        dica = dados.get("dica", "")
        titulo = d.get("titulo", "Anagrama")

        if not palavra:
            print(f"AVISO: '{titulo}' sem 'palavra_original', pulando.", file=sys.stderr)
            continue

        palavra_norm = normalize(palavra).replace(" ", "")
        embaralhada, ok = embaralhar(palavra_norm, seed=i + 7)
        if not ok:
            print(f"AVISO: '{titulo}' — não consegui embaralhar '{palavra_norm}' de forma genuinamente diferente (palavra curta demais ou letras repetidas). Pulando.", file=sys.stderr)
            continue

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf(p1, titulo, dica, embaralhada, palavra_norm, with_answers=False)
        make_pdf(p2, titulo, dica, embaralhada, palavra_norm, with_answers=True)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: embaralhamento é diferente do original)")


if __name__ == "__main__":
    main()
