import argparse
import json
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# Confirmados visualmente (renderizados de verdade, sem virar quadrado vazio)
# na fonte padrão do reportlab — nunca usar símbolo fora desta lista.
SIMBOLOS_SEGUROS = list("♠♥♦♣★●▲▼◆✦✧✱✲✳✴❄❉❊❋✓✗✕✖†‡§¶")


def normalize(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def sanitizar_chave(chave):
    """Garante que todo símbolo da chave é seguro pra imprimir. Se o agente
    de IA mandou um símbolo fora da lista segura (ou repetido), substitui por
    um símbolo seguro e ainda não usado, preservando a estrutura da chave."""
    usados = set()
    disponiveis = [s for s in SIMBOLOS_SEGUROS]
    nova_chave = {}
    for letra, simbolo in chave.items():
        if simbolo in SIMBOLOS_SEGUROS and simbolo not in usados:
            nova_chave[letra] = simbolo
            usados.add(simbolo)
        else:
            substituto = next(s for s in disponiveis if s not in usados)
            nova_chave[letra] = substituto
            usados.add(substituto)
    return nova_chave


def codificar(mensagem, chave):
    """Aplica a chave (letra -> simbolo) a cada letra da mensagem.
    Letras sem entrada na chave passam direto (ex: espaco, pontuacao)."""
    out = []
    for ch in mensagem:
        if ch in chave:
            out.append(chave[ch])
        else:
            out.append(ch)
    return "".join(out)


def decodificar(mensagem_codificada, chave):
    """Inverte a chave e decodifica, pra verificar que bate com a resposta."""
    chave_inversa = {v: k for k, v in chave.items()}
    out = []
    for ch in mensagem_codificada:
        if ch in chave_inversa:
            out.append(chave_inversa[ch])
        else:
            out.append(ch)
    return "".join(out)


def verificar(mensagem_original, chave):
    """Codifica e decodifica de volta, confirma que bate com o original —
    prova que a chave é reversível e sem colisão antes de imprimir."""
    codificada = codificar(mensagem_original, chave)
    decodificada = decodificar(codificada, chave)
    return decodificada == mensagem_original, codificada


def make_pdf(path, titulo, chave, mensagem_codificada, resposta, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Decifre a mensagem"
    c.drawCentredString(width / 2, height - 80, subtitle)

    # tabela de chave (letra -> simbolo)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, height - 120, "Chave de decodificação:")
    c.setFont("Courier", 10)
    itens = sorted(chave.items())
    col_x = [60, 180, 300, 420]
    for i, (letra, simbolo) in enumerate(itens):
        cx = col_x[i % len(col_x)]
        cy = height - 140 - (i // len(col_x)) * 16
        c.drawString(cx, cy, f"{letra} = {simbolo}")

    linha_y = height - 140 - ((len(itens) - 1) // len(col_x) + 1) * 16 - 30

    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, linha_y, "Mensagem codificada:")
    c.setFont("Courier-Bold", 13)
    # quebra a mensagem em linhas de ~40 caracteres pra caber na pagina
    largura_linha = 40
    partes = [mensagem_codificada[i:i+largura_linha] for i in range(0, len(mensagem_codificada), largura_linha)]
    y = linha_y - 25
    for parte in partes:
        c.drawString(60, y, parte)
        y -= 20

    if with_answers:
        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, "Resposta decodificada:")
        c.setFont("Helvetica", 12)
        y -= 20
        c.drawString(60, y, resposta)

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

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "cifra"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo cifra encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for d in dinamicas:
        dados = d.get("dados", {})
        chave = dados.get("chave", {})
        resposta = dados.get("resposta", "")
        titulo = d.get("titulo", "Cifra")

        if not chave or not resposta:
            print(f"AVISO: '{titulo}' sem 'chave' ou 'resposta', pulando.", file=sys.stderr)
            continue

        resposta_norm = normalize(resposta)
        chave_norm = {normalize(k): v for k, v in chave.items()}
        chave_norm = sanitizar_chave(chave_norm)

        ok, codificada = verificar(resposta_norm, chave_norm)
        if not ok:
            print(f"ERRO: '{titulo}' — a chave fornecida não decodifica de volta pra resposta original. Pulando.", file=sys.stderr)
            continue

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf(p1, titulo, chave_norm, codificada, resposta_norm, with_answers=False)
        make_pdf(p2, titulo, chave_norm, codificada, resposta_norm, with_answers=True)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: decodifica corretamente)")


if __name__ == "__main__":
    main()
