import argparse
import json
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


def normalize(word):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return word.upper().translate(repl).replace(" ", "")


class Cruzadinha:
    def __init__(self):
        self.celulas = {}  # (linha, coluna) -> letra
        self.palavras_colocadas = []  # [{"palavra","dica","linha","coluna","direcao","numero"}]

    def cabe(self, palavra, linha, coluna, direcao):
        dr, dc = (0, 1) if direcao == "H" else (1, 0)
        tem_intersecao = False
        for i, ch in enumerate(palavra):
            r, c = linha + dr * i, coluna + dc * i
            existente = self.celulas.get((r, c))
            if existente is not None:
                if existente != ch:
                    return False
                tem_intersecao = True
            else:
                # evita palavra colada em outra sem intersecao real
                # (celula vizinha ocupada na direcao perpendicular, sem ser cruzamento)
                perp = (0, 1) if direcao == "V" else (1, 0)
                viz1 = self.celulas.get((r + perp[0], c + perp[1]))
                viz2 = self.celulas.get((r - perp[0], c - perp[1]))
                if viz1 is not None or viz2 is not None:
                    return False
        # celula antes e depois da palavra tem que estar livres (evita grudar)
        r0, c0 = linha - dr, coluna - dc
        r1, c1 = linha + dr * len(palavra), coluna + dc * len(palavra)
        if self.celulas.get((r0, c0)) is not None or self.celulas.get((r1, c1)) is not None:
            return False
        return tem_intersecao

    def colocar(self, palavra, dica, linha, coluna, direcao):
        dr, dc = (0, 1) if direcao == "H" else (1, 0)
        for i, ch in enumerate(palavra):
            self.celulas[(linha + dr * i, coluna + dc * i)] = ch
        self.palavras_colocadas.append({
            "palavra": palavra, "dica": dica, "linha": linha, "coluna": coluna, "direcao": direcao
        })

    def tentar_encaixar_cruzando(self, palavra, dica):
        for existente in self.palavras_colocadas:
            p_existente = existente["palavra"]
            for i, ch in enumerate(palavra):
                for j, ch2 in enumerate(p_existente):
                    if ch != ch2:
                        continue
                    # tenta cruzar perpendicular a "existente" nesse ponto
                    nova_direcao = "V" if existente["direcao"] == "H" else "H"
                    if existente["direcao"] == "H":
                        r_cruz = existente["linha"]
                        c_cruz = existente["coluna"] + j
                        linha = r_cruz - i
                        coluna = c_cruz
                    else:
                        r_cruz = existente["linha"] + j
                        c_cruz = existente["coluna"]
                        linha = r_cruz
                        coluna = c_cruz - i
                    if self.cabe(palavra, linha, coluna, nova_direcao):
                        self.colocar(palavra, dica, linha, coluna, nova_direcao)
                        return True
        return False

    def bounds(self):
        rows = [r for r, c in self.celulas]
        cols = [c for r, c in self.celulas]
        return min(rows), max(rows), min(cols), max(cols)

    def verificar_tudo(self):
        """Confere, célula por célula, que cada palavra colocada realmente
        bate com o que está na grade final — mesma filosofia de verificação
        rigorosa do caça-palavras."""
        for p in self.palavras_colocadas:
            dr, dc = (0, 1) if p["direcao"] == "H" else (1, 0)
            for i, ch in enumerate(p["palavra"]):
                r, c = p["linha"] + dr * i, p["coluna"] + dc * i
                if self.celulas.get((r, c)) != ch:
                    return False, p["palavra"]
        return True, None


def montar_cruzadinha(pares, seed):
    pares_ordenados = sorted(pares, key=lambda x: len(x["palavra"]), reverse=True)
    grade = Cruzadinha()

    primeira = pares_ordenados[0]
    grade.colocar(primeira["palavra"], primeira["dica"], 0, 0, "H")

    nao_encaixadas = []
    for par in pares_ordenados[1:]:
        if not grade.tentar_encaixar_cruzando(par["palavra"], par["dica"]):
            nao_encaixadas.append(par["palavra"])

    return grade, nao_encaixadas


def numerar_palavras(grade):
    """Numera as palavras no estilo de cruzadinha tradicional — número novo
    toda vez que uma célula é início de uma palavra Horizontal e/ou Vertical."""
    min_r, max_r, min_c, max_c = grade.bounds()
    inicios = {}
    for p in grade.palavras_colocadas:
        inicios.setdefault((p["linha"], p["coluna"]), []).append(p)

    numero = 1
    posicoes_ordenadas = sorted(inicios.keys(), key=lambda rc: (rc[0], rc[1]))
    for rc in posicoes_ordenadas:
        for p in inicios[rc]:
            p["numero"] = numero
        numero += 1


def make_pdf(path, titulo, grade, with_answers):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    min_r, max_r, min_c, max_c = grade.bounds()
    n_rows = max_r - min_r + 1
    n_cols = max_c - min_c + 1

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 50, titulo)
    c.setFont("Helvetica-Oblique", 11)
    subtitle = "Gabarito do Mestre" if with_answers else "Palavras Cruzadas"
    c.drawCentredString(width / 2, height - 70, subtitle)

    cell = min(28, 460 / max(n_rows, n_cols))
    x0 = width / 2 - n_cols * cell / 2
    y0 = height - 110

    for (r, c_) in grade.celulas:
        rr, cc = r - min_r, c_ - min_c
        x = x0 + cc * cell
        y = y0 - rr * cell
        c.rect(x, y - cell, cell, cell, stroke=1, fill=0)
        if with_answers:
            c.setFont("Courier-Bold", int(cell * 0.5))
            c.drawCentredString(x + cell / 2, y - cell * 0.7, grade.celulas[(r, c_)])

    for p in grade.palavras_colocadas:
        rr, cc = p["linha"] - min_r, p["coluna"] - min_c
        x = x0 + cc * cell
        y = y0 - rr * cell
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x + 1, y - 8, str(p["numero"]))

    y_dicas = y0 - n_rows * cell - 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y_dicas, "Dicas:")
    c.setFont("Helvetica", 9)
    y_cursor = y_dicas - 16
    for direcao_nome, direcao_key in (("Horizontais", "H"), ("Verticais", "V")):
        itens = [p for p in grade.palavras_colocadas if p["direcao"] == direcao_key]
        if not itens:
            continue
        c.setFont("Helvetica-Bold", 9)
        c.drawString(60, y_cursor, direcao_nome + ":")
        y_cursor -= 13
        c.setFont("Helvetica", 9)
        for p in sorted(itens, key=lambda x: x["numero"]):
            texto = f"{p['numero']}. {p['dica']}"
            c.drawString(70, y_cursor, texto[:95])
            y_cursor -= 13

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

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "palavras_cruzadas"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo palavras_cruzadas encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for i, d in enumerate(dinamicas):
        dados = d.get("dados", {})
        pares_raw = dados.get("pares") or dados.get("palavras") or dados.get("termos") or []
        titulo = d.get("titulo", "Palavras Cruzadas")

        if len(pares_raw) < 2:
            print(f"AVISO: '{titulo}' tem menos de 2 palavras, pulando.", file=sys.stderr)
            continue

        def extrair_palavra(item):
            for chave in ("palavra", "termo", "resposta", "texto"):
                if chave in item and isinstance(item[chave], str):
                    return item[chave]
            return ""

        def extrair_dica(item):
            for chave in ("dica", "pista", "descricao"):
                if chave in item and isinstance(item[chave], str):
                    return item[chave]
            return ""

        pares = [{"palavra": normalize(extrair_palavra(par)), "dica": extrair_dica(par)} for par in pares_raw]
        pares = [par for par in pares if len(par["palavra"]) >= 2]

        grade, nao_encaixadas = montar_cruzadinha(pares, seed=i + 7)
        numerar_palavras(grade)

        ok, palavra_com_erro = grade.verificar_tudo()
        if not ok:
            print(f"ERRO: '{titulo}' — falha de verificação na palavra '{palavra_com_erro}'. Pulando este puzzle inteiro.", file=sys.stderr)
            continue

        if nao_encaixadas:
            print(
                f"AVISO: '{titulo}' — não consegui cruzar {len(nao_encaixadas)} palavra(s) "
                f"na grade ({', '.join(nao_encaixadas)}). O puzzle sai só com as que "
                f"encaixaram ({len(grade.palavras_colocadas)} de {len(pares)}).",
                file=sys.stderr,
            )

        if len(grade.palavras_colocadas) < 2:
            print(f"ERRO: '{titulo}' — menos de 2 palavras encaixaram de verdade, não vale a pena gerar. Pulando.", file=sys.stderr)
            continue

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf(p1, titulo, grade, with_answers=False)
        make_pdf(p2, titulo, grade, with_answers=True)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} ({len(grade.palavras_colocadas)} palavras verificadas célula a célula)")


if __name__ == "__main__":
    main()
