import argparse
import json
import os
import random
import re
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def buscar_campo_lista(dados, contem):
    for chave, valor in dados.items():
        if not isinstance(valor, list):
            continue
        chave_norm = normalize(chave).lower().replace("_", "")
        if any(normalize(c).lower().replace("_", "") in chave_norm for c in contem):
            return valor
    return None


def buscar_campo_texto_simples(dados, contem):
    for chave, valor in dados.items():
        if not isinstance(valor, str):
            continue
        chave_norm = normalize(chave).lower().replace("_", "")
        if any(normalize(c).lower().replace("_", "") in chave_norm for c in contem):
            return valor
    return ""


def limpar_numeracao(item):
    """Se a IA já escreveu o item com número na frente ('1. Faça X'), tira
    esse número — senão a resposta fica visível de graça no próprio texto,
    o que anula o puzzle. Também converte item numérico puro (ex: 1, 2, 3)
    em string, caso a IA tenha mandado só os índices em vez do texto."""
    if isinstance(item, (int, float)):
        return str(item)
    texto = str(item)
    return re.sub(r"^\s*\d+[\.\):\-]?\s*", "", texto).strip()


def resolver_por_palavra_chave(rotulo, elementos):
    """Quando 'ordem_correta' vem como rótulo curto (ex: 'abismo') em vez do
    texto completo do elemento (ex: 'Toque na Runas do Abismo'), procura
    qual elemento CONTÉM esse rótulo como palavra, e devolve o texto
    completo dele — assim a carta impressa sempre mostra o texto real."""
    rotulo_norm = normalize(str(rotulo)).lower()
    for elem in elementos:
        if rotulo_norm in normalize(elem).lower():
            return elem
    return None


def normalize(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def verificar(elementos, ordem_correta):
    """Confirma que 'ordem_correta' é uma sub-sequência válida de
    'elementos' — todo item da ordem certa precisa existir em elementos,
    sem duplicar. 'elementos' pode ter itens A MAIS (cartas-isca que não
    fazem parte da sequência certa — deixa o puzzle mais difícil de
    propósito) — só não pode faltar nenhum item que a ordem_correta pede."""
    if len(set(ordem_correta)) != len(ordem_correta):
        return False, "'ordem_correta' tem itens duplicados — cada posição precisa ser única"
    if len(set(elementos)) != len(elementos):
        return False, "'elementos' tem itens duplicados — cada carta precisa ser única pra não haver ambiguidade"
    faltando = set(ordem_correta) - set(elementos)
    if faltando:
        return False, f"'ordem_correta' cita item(ns) que não estão em 'elementos': {', '.join(faltando)}"
    return True, ""


def make_pdf_cartas(path, titulo, elementos, embaralhados, pista, ordem_correta, with_answers, iscas=None):
    iscas = iscas or []
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
    if iscas and not with_answers:
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(width / 2, height - 120, f"Atenção: {len(iscas)} carta(s) aqui não pertencem à sequência certa.")
    if iscas and with_answers:
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(width / 2, height - 105, f"Cartas-isca (não entram na sequência): {', '.join(iscas)}")

    # Gabarito mostra só a ordem correta (sem as iscas, pra ficar claro pro
    # mestre); jogadores veem todas as cartas juntas, embaralhadas.
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

        eh_isca = item in iscas
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
        # NUNCA marca "(isca)" na versão do jogador — isso entregaria a
        # resposta de graça. O aviso de quantas iscas existem já foi dado
        # no topo da página, sem dizer QUAIS são.

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
        elementos_brutos = (
            dados.get("elementos")
            or buscar_campo_lista(dados, contem=["elementos", "passos", "etapas", "itens", "cartas", "opcoes", "disponivel"])
            or []
        )
        ordem_brutos = (
            dados.get("ordem_correta")
            or dados.get("sequencia_correta")
            or buscar_campo_lista(dados, contem=["ordem", "sequencia", "resposta"])
            or []
        )
        pista = dados.get("pista_in_fiction", "") or buscar_campo_texto_simples(dados, ["pista", "dica"])
        titulo = d.get("titulo", "Sequência Lógica")

        if not elementos_brutos or not ordem_brutos:
            print(f"AVISO: '{titulo}' sem elementos ou ordem correta reconhecíveis, pulando.", file=sys.stderr)
            continue

        # Limpa numeração visível de cada item (ex: "1. Faça X" -> "Faça X"),
        # senão a resposta vaza no próprio texto do item.
        elementos = [limpar_numeracao(e) for e in elementos_brutos]

        # A IA pode mandar "ordem_correta" como os mesmos textos reordenados
        # (formato oficial), OU como uma lista de números indicando a posição
        # de cada elemento (ex: [1,2,3,4]) — detecta qual é o caso e resolve
        # pro formato de texto de qualquer jeito.
        if all(isinstance(x, (int, float)) for x in ordem_brutos):
            try:
                # tenta 1-based primeiro (mais comum em enumeração humana)
                ordem_correta = [elementos[int(idx) - 1] for idx in ordem_brutos]
            except (IndexError, ValueError):
                try:
                    ordem_correta = [elementos[int(idx)] for idx in ordem_brutos]
                except (IndexError, ValueError):
                    print(f"ERRO: '{titulo}' — 'ordem_correta' tem índices que não batem com a quantidade de elementos. Pulando.", file=sys.stderr)
                    continue
        else:
            ordem_limpa = [limpar_numeracao(x) for x in ordem_brutos]
            # Se os itens não batem com o texto exato dos elementos (ex: a
            # IA mandou rótulo curto "abismo" em vez do texto completo),
            # tenta resolver por palavra-chave antes de desistir.
            if not set(ordem_limpa).issubset(set(elementos)):
                resolvidos = []
                for item in ordem_limpa:
                    if item in elementos:
                        resolvidos.append(item)
                    else:
                        achado = resolver_por_palavra_chave(item, elementos)
                        resolvidos.append(achado if achado else item)
                ordem_correta = resolvidos
            else:
                ordem_correta = ordem_limpa

        ok, motivo = verificar(elementos, ordem_correta)
        if not ok:
            print(f"ERRO: '{titulo}' — {motivo}. Pulando.", file=sys.stderr)
            continue

        rnd = random.Random(i + 7)
        embaralhados = elementos[:]
        tentativas = 0
        while embaralhados[:len(ordem_correta)] == ordem_correta and tentativas < 20:
            rnd.shuffle(embaralhados)
            tentativas += 1

        iscas = [e for e in elementos if e not in ordem_correta]
        if iscas:
            print(f"[{p}] Nota: '{titulo}' tem {len(iscas)} carta(s)-isca que não entram na sequência certa: {', '.join(iscas)}")

        slug = slugify(titulo)
        p1 = os.path.join(pasta_puzzles, f"{slug}_JOGADORES.pdf")
        p2 = os.path.join(pasta_puzzles, f"{slug}_GABARITO.pdf")
        make_pdf_cartas(p1, titulo, elementos, embaralhados, pista, ordem_correta, with_answers=False, iscas=iscas)
        make_pdf_cartas(p2, titulo, elementos, embaralhados, pista, ordem_correta, with_answers=True, iscas=iscas)
        print(f"[{p}] OK: '{titulo}' -> {p1} e {p2} (verificado: {len(ordem_correta)} itens da sequência certa, {len(iscas)} isca(s))")


if __name__ == "__main__":
    main()
