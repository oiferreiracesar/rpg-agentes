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


def make_pdf(path, titulo, pistas, codigo_final, with_answers, verificado=True, enigma_texto=None):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Descubra o código do cadeado"
    c.drawCentredString(width / 2, height - 80, subtitle)

    y = height - 120
    if pistas:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "Pistas:")
        y -= 25
        c.setFont("Helvetica", 11)
        for i, pista in enumerate(pistas, 1):
            texto = f"{i}. {pista['texto']}"
            if with_answers:
                texto += f"   [valor: {pista['valor']}]"
            c.drawString(70, y, texto[:100])
            y -= 22
    elif enigma_texto:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "Enigma:")
        y -= 22
        c.setFont("Helvetica", 11)
        palavras = enigma_texto.split()
        linha = ""
        for palavra in palavras:
            teste = (linha + " " + palavra).strip()
            if c.stringWidth(teste, "Helvetica", 11) < width - 120:
                linha = teste
            else:
                c.drawString(70, y, linha)
                y -= 18
                linha = palavra
        if linha:
            c.drawString(70, y, linha)
            y -= 18

    if with_answers:
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y, f"Código final: {codigo_final}")
        if not verificado:
            y -= 25
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(
                60, y,
                "ATENÇÃO: este código NÃO foi verificado matematicamente pelo script — confira à mão antes de usar na mesa."
            )

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
        titulo = d.get("titulo", "Cadeado Numérico")

        pistas = dados.get("pistas", [])
        operacao = dados.get("operacao", "concatenacao")
        codigo_esperado = str(dados.get("codigo_final") or dados.get("codigo_resposta") or "")

        if pistas and codigo_esperado:
            # --- Modo estrito: verificação matemática completa ---
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
            make_pdf(p1, titulo, pistas, codigo_esperado, with_answers=False, verificado=True)
            make_pdf(p2, titulo, pistas, codigo_esperado, with_answers=True, verificado=True)
            print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: {operacao} das pistas resulta em '{codigo_esperado}')")
            continue

        # --- Modo de segurança: a IA não seguiu o formato estruturado
        # (pistas/operacao/codigo_final), mas ainda deu um enigma em texto
        # livre com um código final. Gera mesmo assim, mas SEM verificação
        # matemática, avisando isso claramente no PDF e no log — mais útil
        # que descartar o puzzle inteiro. ---
        enigma_texto = dados.get("enigma_matematico") or dados.get("conta_passo_a_passo")
        codigo_fallback = str(dados.get("codigo_resposta") or dados.get("codigo_final") or "")

        if not enigma_texto or not codigo_fallback:
            print(f"AVISO: '{titulo}' sem dados suficientes (nem formato estruturado, nem enigma+código), pulando.", file=sys.stderr)
            continue

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf(p1, titulo, [], codigo_fallback, with_answers=False, verificado=False, enigma_texto=enigma_texto)
        make_pdf(p2, titulo, [], codigo_fallback, with_answers=True, verificado=False, enigma_texto=enigma_texto)
        print(
            f"[{p}] OK (SEM VERIFICAÇÃO): '{titulo}' -> {p1} e {p2} — a IA não usou o formato "
            f"estruturado (pistas/operacao/codigo_final), gerado a partir de texto livre. "
            f"CONFIRA O CÓDIGO À MÃO antes de usar na mesa.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
