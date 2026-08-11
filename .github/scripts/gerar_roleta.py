import argparse
import json
import math
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

CORES = [
    HexColor("#c0392b"), HexColor("#2980b9"), HexColor("#27ae60"),
    HexColor("#f39c12"), HexColor("#8e44ad"), HexColor("#16a085"),
    HexColor("#d35400"), HexColor("#2c3e50"),
]


def normalizar_opcao(item):
    """A IA às vezes manda cada opção como um objeto em vez de texto puro
    (ex: {"nome": "..."} em vez de "..."). Extrai um texto de exibição de
    qualquer um dos dois formatos, nunca deixa passar um dict cru adiante."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for chave in ("nome", "titulo", "texto", "opcao", "label", "valor"):
            if chave in item and isinstance(item[chave], str):
                return item[chave]
        # nenhum campo reconhecido — usa o primeiro valor de texto que achar
        for v in item.values():
            if isinstance(v, str):
                return v
        return str(item)
    return str(item)


def normalize(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def calcular_angulos(opcoes, pesos):
    """Converte pesos em graus reais de cada fatia — soma tem que bater
    exatamente 360, senão a roleta fica com um espaço em branco ou
    sobreposição."""
    total_peso = sum(pesos)
    angulos = []
    inicio = 0.0
    for peso in pesos:
        fatia = 360.0 * peso / total_peso
        angulos.append((inicio, inicio + fatia))
        inicio += fatia
    return angulos


def verificar(angulos):
    if not angulos:
        return False, "nenhuma opção"
    if abs(angulos[-1][1] - 360.0) > 0.01:
        return False, f"soma dos ângulos deu {angulos[-1][1]:.2f}, deveria ser 360"
    for i in range(len(angulos) - 1):
        if abs(angulos[i][1] - angulos[i + 1][0]) > 0.01:
            return False, f"fatia {i} e {i+1} não são contíguas (sobreposição ou espaço)"
    return True, ""


def make_pdf(path, titulo, opcoes, pesos, contexto):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 60, titulo)

    if contexto:
        c.setFont("Helvetica-Oblique", 10)
        largura_max = width - 100
        palavras = contexto.split()
        linhas, linha_atual = [], ""
        for palavra in palavras:
            teste = (linha_atual + " " + palavra).strip()
            if c.stringWidth(teste, "Helvetica-Oblique", 10) < largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        y_contexto = height - 80
        for linha in linhas[:3]:
            c.drawCentredString(width / 2, y_contexto, linha)
            y_contexto -= 14

    cx, cy = width / 2, height / 2 + 30
    raio = 180

    angulos = calcular_angulos(opcoes, pesos)

    for i, (inicio, fim) in enumerate(angulos):
        cor = CORES[i % len(CORES)]
        c.setFillColor(cor)
        p = c.beginPath()
        p.moveTo(cx, cy)
        passos = max(2, int((fim - inicio) / 2))
        for j in range(passos + 1):
            ang = math.radians(inicio + (fim - inicio) * j / passos)
            x = cx + raio * math.cos(ang)
            y = cy + raio * math.sin(ang)
            p.lineTo(x, y)
        p.close()
        c.drawPath(p, fill=1, stroke=1)

        ang_meio = math.radians((inicio + fim) / 2)
        tx = cx + raio * 0.62 * math.cos(ang_meio)
        ty = cy + raio * 0.62 * math.sin(ang_meio)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 11)
        c.saveState()
        c.translate(tx, ty)
        rotacao = math.degrees(ang_meio)
        if 90 < rotacao < 270:
            rotacao += 180
        c.rotate(rotacao)
        texto = opcoes[i]

        # Quebra em até 3 linhas em vez de truncar cedo com "..." — só
        # encurta de verdade se nem assim couber.
        largura_disponivel = raio * 0.85
        if c.stringWidth(texto, "Helvetica-Bold", 11) <= largura_disponivel:
            c.drawCentredString(0, 0, texto)
        else:
            palavras = texto.split()
            linhas, linha_atual = [], ""
            for palavra in palavras:
                teste = (linha_atual + " " + palavra).strip()
                if c.stringWidth(teste, "Helvetica-Bold", 11) <= largura_disponivel:
                    linha_atual = teste
                else:
                    if linha_atual:
                        linhas.append(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual)

            if len(linhas) > 3:
                sobra = " ".join(linhas[2:])
                while sobra and c.stringWidth(sobra + "…", "Helvetica-Bold", 11) > largura_disponivel:
                    sobra = sobra[:-1]
                linhas = linhas[:2] + [sobra + "…"]

            offsets = {1: [0], 2: [7, -7], 3: [14, 0, -14]}
            for linha, dy in zip(linhas, offsets[len(linhas)]):
                c.drawCentredString(0, dy, linha)
        c.restoreState()

    c.setStrokeColor(HexColor("#000000"))
    c.setLineWidth(2)
    c.circle(cx, cy, raio, stroke=1, fill=0)

    # seta indicadora fixa no topo
    c.setFillColor(HexColor("#000000"))
    seta = c.beginPath()
    seta.moveTo(cx - 12, cy + raio + 5)
    seta.lineTo(cx + 12, cy + raio + 5)
    seta.lineTo(cx, cy + raio + 25)
    seta.close()
    c.drawPath(seta, fill=1, stroke=1)

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(HexColor("#000000"))
    c.drawCentredString(
        width / 2, 60,
        "Recorte, fure o centro, prenda um clipe de papel com uma caneta — gire e deixe a sorte decidir."
    )

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

    dinamicas = [d for d in data.get("dinamicas", []) if d.get("tipo") == "roleta_decisao"]
    if not dinamicas:
        print(f"[{p}] Nenhuma dinâmica do tipo roleta_decisao encontrada em 10-puzzles.json.")
        return

    pasta_puzzles = os.path.join(p, "puzzles")
    os.makedirs(pasta_puzzles, exist_ok=True)

    for d in dinamicas:
        titulo = d.get("titulo", "Roleta de Decisão")
        try:
            dados = d.get("dados", {})
            opcoes_brutas = dados.get("opcoes", [])
            opcoes = [normalizar_opcao(o) for o in opcoes_brutas]
            pesos = dados.get("pesos") or [1] * len(opcoes)

            if not all(isinstance(pe, (int, float)) for pe in pesos):
                print(f"AVISO: '{titulo}' — 'pesos' tem valor não-numérico, usando pesos iguais.", file=sys.stderr)
                pesos = [1] * len(opcoes)

            contexto = d.get("contexto_narrativo", "") or dados.get("contexto_narrativo", "")

            if len(opcoes) < 2:
                print(f"AVISO: '{titulo}' precisa de pelo menos 2 opções, pulando.", file=sys.stderr)
                continue
            if len(pesos) != len(opcoes):
                print(f"AVISO: '{titulo}' — 'pesos' não bate em quantidade com 'opcoes', usando pesos iguais.", file=sys.stderr)
                pesos = [1] * len(opcoes)

            angulos = calcular_angulos(opcoes, pesos)
            ok, motivo = verificar(angulos)
            if not ok:
                print(f"ERRO: '{titulo}' — {motivo}. Pulando.", file=sys.stderr)
                continue

            slug = slugify(titulo)
            p1 = os.path.join(pasta_puzzles, f"{slug}_ROLETA.pdf")
            make_pdf(p1, titulo, opcoes, pesos, contexto)
            print(f"[{p}] OK: '{titulo}' -> {p1} (verificado: {len(opcoes)} fatias somam 360°)")
        except Exception as e:
            # Nunca deixa uma roleta com dado inesperado derrubar o script
            # inteiro — pula só essa e segue pras próximas.
            print(f"ERRO INESPERADO em '{titulo}': {e}. Pulando esta roleta, seguindo com as demais.", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
