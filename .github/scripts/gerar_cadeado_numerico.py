import argparse
import json
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def normalize(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def calcular(valores, operacao):
    if operacao == "concatenacao":
        return "".join(str(v) for v in valores)
    if operacao == "soma":
        return str(sum(valores))
    if operacao == "produto":
        resultado = 1
        for v in valores:
            resultado *= v
        return str(resultado)
    return None


def slugify(text):
    text = normalize(text).lower()
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def make_pdf(path, titulo, pistas, codigo_final, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Descubra o código do cadeado"
    c.drawCentredString(width / 2, height - 80, subtitle)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, height - 120, "Pistas:")
    c.setFont("Helvetica", 11)
    y = height - 145
    for i, pista in enumerate(pistas, 1):
        texto = f"{i}. {pista['texto']}"
        if with_answers:
            texto += f"   [valor: {pista['valor']}]"
        c.drawString(70, y, texto[:100])
        y -= 22

    if with_answers:
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, f"Código final: {codigo_final}")

    c.showPage()
    c.save()


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

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "cadeado_numerico"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo cadeado_numerico encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for d in dinamicas:
        dados = d.get("dados", {})
        pistas = dados.get("pistas", [])
        operacao = dados.get("operacao", "concatenacao")
        codigo_esperado = str(dados.get("codigo_final", ""))
        titulo = d.get("titulo", "Cadeado Numérico")

        if not pistas or not codigo_esperado:
            print(f"AVISO: '{titulo}' sem 'pistas' ou 'codigo_final', pulando.", file=sys.stderr)
            continue

        try:
            valores = [int(pista["valor"]) for pista in pistas]
        except (KeyError, ValueError, TypeError):
            print(f"ERRO: '{titulo}' — alguma pista não tem 'valor' numérico válido. Pulando.", file=sys.stderr)
            continue

        codigo_calculado = calcular(valores, operacao)
        if codigo_calculado is None:
            print(f"ERRO: '{titulo}' — operação '{operacao}' desconhecida (use concatenacao, soma ou produto). Pulando.", file=sys.stderr)
            continue

        if codigo_calculado != codigo_esperado:
            print(
                f"ERRO: '{titulo}' — o código declarado ('{codigo_esperado}') não bate com o "
                f"resultado real de aplicar '{operacao}' às pistas (deu '{codigo_calculado}'). Pulando.",
                file=sys.stderr,
            )
            continue

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf(p1, titulo, pistas, codigo_esperado, with_answers=False)
        make_pdf(p2, titulo, pistas, codigo_esperado, with_answers=True)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: {operacao} das pistas resulta em '{codigo_esperado}')")


if __name__ == "__main__":
    main()
