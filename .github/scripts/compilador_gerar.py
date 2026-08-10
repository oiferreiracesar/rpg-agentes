import argparse
import json
import os
import sys


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_puzzle_slug(text):
    repl = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "AAAAAEEEEIIIIOOOOOUUUUC")
    return text.upper().translate(repl)


def slugify_puzzle(text):
    """Reproduz exatamente a lógica de slug usada pelos scripts
    gerar_caca_palavras.py, gerar_cifra.py, gerar_anagrama.py,
    gerar_sequencia_logica.py, gerar_palavras_cruzadas.py,
    gerar_cadeado_numerico.py e gerar_sudoku_tematico.py — é assim que
    calculamos o nome do PDF real pra linkar corretamente."""
    text = normalize_puzzle_slug(text).lower().replace("_", " ")
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def read_json_opt(path):
    return read_json(path) if os.path.exists(path) else None


def find_npc(npcs_data, npc_id):
    for n in npcs_data.get("npcs", []):
        if n["id"] == npc_id:
            return n
    return None


def find_mapa(cartografo, local_ref):
    for m in cartografo.get("mapas", []):
        if m["local_ref"] == local_ref:
            return m
    return None


def find_sonoplastia(sono, cena_num):
    for s in sono.get("sonoplastia", []):
        if s["cena"] == cena_num:
            return s
    return None


def find_documentos(docs, cena_num):
    if not docs:
        return []
    return [d for d in docs.get("documentos", []) if d.get("cena_onde_aparece") == cena_num]


def apresenta_identidade(roteirista, npc_id, cena_num):
    for io in roteirista.get("identidades_ocultas", []):
        if io["id"] == npc_id:
            for ap in io["aparencias_por_cena"]:
                if ap["cena"] == cena_num:
                    return ap
    return None


def attrs_str(attrs):
    return (
        f"Ag {attrs.get('agilidade', '-')}, As {attrs.get('astucia', '-')}, "
        f"Esp {attrs.get('espirito', '-')}, F {attrs.get('forca', '-')}, "
        f"V {attrs.get('vigor', '-')}"
    )


def cutscenes_por_cena(animador):
    mapa = {}
    if not animador:
        return mapa
    for cs in animador.get("cutscenes", []):
        ref = cs.get("cena_ref")
        if ref is not None and not cs.get("final_ref"):
            mapa.setdefault(ref, []).append(cs)
    return mapa


def cutscenes_por_final(animador):
    mapa = {}
    if not animador:
        return mapa
    for cs in animador.get("cutscenes", []):
        ref = cs.get("final_ref")
        if ref:
            mapa.setdefault(ref, []).append(cs)
    return mapa


def render_dados_puzzle_generico(md, dados):
    """Mostra qualquer estrutura de 'dados' de forma legível, sem depender
    de nome de campo fixo — usado pelos tipos de estrutura livre (texto
    pronto, geração externa, físico/social)."""
    for chave, valor in dados.items():
        chave_legivel = chave.replace("_", " ").capitalize()
        if isinstance(valor, list):
            md.append(f"- **{chave_legivel}:**")
            for item in valor:
                if isinstance(item, dict):
                    partes = " — ".join(f"{k.replace('_',' ')}: {v}" for k, v in item.items())
                    md.append(f"  - {partes}")
                else:
                    md.append(f"  - {item}")
        elif isinstance(valor, dict):
            md.append(f"- **{chave_legivel}:**")
            for k, v in valor.items():
                md.append(f"  - {k.replace('_',' ')}: {v}")
        else:
            md.append(f"- **{chave_legivel}:** {valor}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta onde estão os JSONs (padrão: output)")
    args = parser.parse_args()
    p = args.pasta

    def caminho(nome):
        return os.path.join(p, nome)

    roteirista_path = caminho("01-roteirista.json")
    if not os.path.exists(roteirista_path):
        print(f"ERRO: {roteirista_path} não encontrado.", file=sys.stderr)
        sys.exit(1)

    roteirista = read_json(roteirista_path)
    npcs_data = read_json_opt(caminho("03-npcs.json")) or {"npcs": []}
    cartografo = read_json_opt(caminho("04-cartografo.json")) or {"mapas": []}
    sono = read_json_opt(caminho("05-sonoplastia.json")) or {"sonoplastia": []}
    docs = read_json_opt(caminho("06-documentos.json"))
    animador = read_json_opt(caminho("08-animador.json"))
    improviso = read_json_opt(caminho("09-improviso.json"))
    puzzles = read_json_opt(caminho("10-puzzles.json"))

    cs_por_cena = cutscenes_por_cena(animador)
    cs_por_final = cutscenes_por_final(animador)

    md = []
    meta = roteirista["metadados"]
    md.append(f"**Sistema:** {meta.get('sistema', '')}  ")
    md.append(f"**Gênero:** {meta.get('genero', '')}  ")
    md.append(f"**Classificação:** {meta.get('classificacao', '')}  ")
    md.append(f"**Duração Estimada:** {meta.get('duracao_estimada', '')}  ")
    md.append(f"**Jogadores:** {meta.get('jogadores', '')}  ")
    md.append("")
    md.append("---")
    md.append("")

    md.append("## Aviso")
    classif = str(meta.get("classificacao", "")).lower()
    if "infant" in classif:
        md.append(
            "Conteúdo adequado para o público infanto-juvenil: apresenta conflitos "
            "dramáticos, mas sem violência gráfica ou temas sombrios inadequados."
        )
    else:
        md.append(
            "Esta aventura contém temas adultos, violência e dilemas morais. "
            "Converse com seu grupo antes de jogar."
        )
    md.append("")
    md.append("---")
    md.append("")

    premissa = roteirista["premissa"]
    md.append("## Premissa")
    md.append(f"> **Gancho Curto:** {premissa['gancho_curto']}")
    md.append("")
    md.append(f"**O que realmente está acontecendo:** {premissa['verdade_central']}")
    md.append("")
    md.append("---")
    md.append("")

    md.append("## Plot Twists")
    for i, t in enumerate(roteirista["twists"], 1):
        md.append(f"{i}. **{t['nome']}:** {t['revelacao']}")
    md.append("")
    md.append("---")
    md.append("")

    md.append("## Estrutura da Sessão")
    md.append("| Número | Nome da Cena | Duração |")
    md.append("| :---: | :--- | :---: |")
    for c in roteirista["cenas"]:
        md.append(f"| {c['numero']} | {c['nome']} | {c['duracao']} |")
    md.append("")
    md.append("---")
    md.append("")

    if animador and animador.get("cutscenes"):
        md.append("## 🎬 Cutscenes")
        md.append(
            "Momentos que valem uma pausa cinematográfica, montados reaproveitando o "
            "mapa e os tokens já gerados. Suba a imagem do mapa (e os tokens, quando "
            "houver) como referência no Google Flow, e cole o prompt correspondente."
        )
        md.append("")
        for i, cs in enumerate(animador["cutscenes"], 1):
            md.append(f"### {i}. {cs.get('momento', '')}")
            md.append("")
            md.append(f"**Quando mostrar:** {cs.get('gatilho_narrativo', '')}")
            md.append("")
            mapa_ref = cs.get("mapa_ref")
            tokens_ref = cs.get("tokens_ref") or []
            reaproveita = []
            if mapa_ref:
                reaproveita.append(f"Mapa `{mapa_ref}`")
            if tokens_ref:
                reaproveita.append("Tokens " + ", ".join(f"`{t}`" for t in tokens_ref))
            if reaproveita:
                md.append(f"**Reaproveita:** {' · '.join(reaproveita)}")
                md.append("")
            if cs.get("cena_do_momento"):
                md.append(f"**Cena:** {cs['cena_do_momento']}")
                md.append("")
            prompt = cs.get("prompt_montagem") or cs.get("prompt_animacao_flow")
            if prompt:
                md.append("**Prompt para o Flow:**")
                md.append("```")
                md.append(prompt)
                md.append("```")
            md.append("")
        md.append("---")
        md.append("")

    md.append("## Resumão de Mesa")
    md.append("### NPCs Combatentes")
    combat_npcs = [n for n in npcs_data["npcs"] if n.get("combatente")]
    if combat_npcs:
        md.append("| Nome | Raça | Carta Selvagem | Atributos | Perícia-Chave | Arma (Dano) | Aparar | Resistência |")
        md.append("| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :---: |")
        for n in combat_npcs:
            pc = n.get("pericia_chave", {})
            arma = n.get("arma", {})
            armadura = n.get("armadura_bonus", 0) or 0
            resistencia_str = f"{n.get('resistencia', '-')}" + (f" ({armadura})" if armadura else "")
            md.append(
                f"| {n['nome_exibicao']} | {n.get('raca', 'Humano')} | "
                f"{'⭐ Sim' if n.get('carta_selvagem') else 'Não'} | "
                f"{attrs_str(n.get('atributos', {}))} | "
                f"{pc.get('nome', '-')} ({pc.get('dado', '-')}) | "
                f"{arma.get('nome', '-')} ({arma.get('dano', '-')}) | "
                f"{n.get('aparar', '-')} | "
                f"{resistencia_str} |"
            )
        if any(n.get("carta_selvagem") for n in combat_npcs):
            md.append("")
            md.append(
                "> **Cartas Selvagens** aguentam 3 Ferimentos antes de ficar "
                "Incapacitadas, e rolam um Dado Selvagem (d6) extra em toda rolagem "
                "de Característica, usando o melhor resultado entre os dois dados."
            )
    else:
        md.append("Nenhum NPC combatente nesta aventura.")
    md.append("")

    md.append("### Dificuldades das Cenas")
    for c in roteirista["cenas"]:
        difs = "; ".join(
            f"{d['pericia']} (mod. {'+' if d['modificador'] > 0 else ''}{d['modificador']}) — {d['acao']}"
            for d in c["dificuldades"]
        )
        md.append(f"- **Cena {c['numero']}:** {difs}")
    md.append("")
    md.append(
        "> Modificador positivo = bônus (mais fácil). Modificador negativo = "
        "penalidade (mais difícil). Número Alvo padrão do SWADE é 4."
    )
    md.append("")

    md.append("### Twists")
    for t in roteirista["twists"]:
        md.append(f"- **{t['nome']}:** {t['revelacao']}")
    md.append("")

    md.append("### Finais")
    for f in roteirista["finais"]:
        md.append(f"- **{f['nome']}:** {f['consequencia']}")
    md.append("")
    md.append("---")
    md.append("")

    if improviso:
        md.append("## 🎲 Tabela de Improviso")
        md.append("Pra quando os jogadores fizerem algo que não está no roteiro.")
        md.append("")

        if improviso.get("framework_geral"):
            md.append("### Framework geral — como decidir na hora")
            md.append("| O jogador quer... | Modificador a aplicar |")
            md.append("| --- | --- |")
            for item in improviso["framework_geral"]:
                md.append(f"| {item.get('situacao', '')} | {item.get('modificador', '')} |")
            md.append("")

        if improviso.get("situacoes_comuns"):
            md.append("### Situações comuns")
            md.append("| O jogador quer... | Como resolver |")
            md.append("| --- | --- |")
            for item in improviso["situacoes_comuns"]:
                md.append(f"| {item.get('situacao', '')} | {item.get('como_resolver', '')} |")
            md.append("")

        if improviso.get("loot_ambiental"):
            md.append("### 🎒 Loot Ambiental")
            md.append(
                "Pra quando os jogadores xeretarem, quebrarem ou remexerem "
                "algo fora do roteiro. Role 1d10 ou escolha o que combina."
            )
            md.append("")
            md.append("| Item | Uso sugerido |")
            md.append("| --- | --- |")
            for item in improviso["loot_ambiental"]:
                md.append(f"| {item.get('item', '')} | {item.get('uso_sugerido', '')} |")
            md.append("")

        if improviso.get("gatilhos_especificos"):
            md.append(f"### Gatilhos específicos de \"{meta.get('titulo', 'esta aventura')}\"")
            md.append("| Se os jogadores... | Como lidar |")
            md.append("| --- | --- |")
            for item in improviso["gatilhos_especificos"]:
                md.append(f"| {item.get('situacao', '')} | {item.get('como_lidar', '')} |")
            md.append("")

        if improviso.get("banco_de_falas"):
            md.append("### 🗣️ Banco de Falas — improviso de diálogo")
            md.append("")
            for entry in improviso["banco_de_falas"]:
                npc = find_npc(npcs_data, entry.get("npc_id"))
                nome = npc["nome_exibicao"] if npc else entry.get("npc_id", "NPC")
                fase = f" — {entry['fase']}" if entry.get("fase") else ""
                md.append(f"**{nome}{fase}**")
                md.append("")
                if entry.get("frase_coringa"):
                    md.append(f"- **Frase-coringa:** *\"{entry['frase_coringa']}\"*")
                for r in entry.get("reacoes", []):
                    md.append(f"- Se {r.get('gatilho', '')}: *\"{r.get('fala', '')}\"*")
                md.append("")

        md.append("---")
        md.append("")

    if puzzles and puzzles.get("dinamicas"):
        SCRIPT_VERIFICAVEL = {
            "caca_palavras", "palavras_cruzadas", "anagrama", "sequencia_logica",
            "cifra", "cadeado_numerico", "sudoku_tematico",
        }
        TITULOS_TIPO = {
            "caca_palavras": "Caça-palavras", "palavras_cruzadas": "Palavras Cruzadas",
            "anagrama": "Anagrama", "sequencia_logica": "Sequência Lógica",
            "cifra": "Cifra", "cadeado_numerico": "Cadeado Numérico",
            "sudoku_tematico": "Sudoku Temático", "enigma": "Enigma",
            "trivia_em_cadeia": "Trivia em Cadeia",
            "fragmentos_para_ordenar": "Fragmentos pra Ordenar",
            "mensagem_espelhada": "Mensagem Espelhada", "labirinto": "Labirinto Visual",
            "sete_erros": "Jogo dos Sete Erros", "jigsaw": "Quebra-cabeça (Jigsaw)",
            "silhueta": "Silhueta", "sequencia_sonora": "Sequência Sonora",
            "mimica_ou_desenho": "Mímica ou Desenho Coletivo",
            "caixa_misteriosa": "Caixa Misteriosa", "desafio_fisico": "Desafio Físico",
        }

        md.append("## 🧩 Dinâmicas e Puzzles")
        md.append(
            "Pausas físicas/interativas pra dar ritmo diferente à mesa. Cada uma "
            "indica em qual cena encaixar."
        )
        md.append("")

        for d in puzzles["dinamicas"]:
            tipo = d.get("tipo", "")
            titulo = d.get("titulo", TITULOS_TIPO.get(tipo, tipo))
            categoria = d.get("categoria", "")
            cena_ref = d.get("cena_ref")
            contexto = d.get("contexto_narrativo", "")
            dados = d.get("dados", {})

            md.append(f"### {titulo}")
            md.append(f"**Tipo:** {TITULOS_TIPO.get(tipo, tipo)}")
            if cena_ref is not None:
                md.append(f"**Cena sugerida:** {cena_ref}")
            if contexto:
                md.append(f"**Contexto:** {contexto}")
            md.append("")

            if tipo in SCRIPT_VERIFICAVEL or categoria == "script_verificavel":
                slug = slugify_puzzle(titulo)
                md.append(
                    "📄 PDF verificado automaticamente — pronto pra imprimir:  \n"
                    f"[Versão dos jogadores](puzzles/{slug}_JOGADORES.pdf) · "
                    f"[Gabarito do mestre](puzzles/{slug}_GABARITO.pdf)"
                )
                md.append("")
                md.append(
                    "> Se algum link acima não abrir: ou o script ainda não rodou "
                    "nessa pasta, ou ele detectou algo inconsistente nos dados "
                    "gerados e pulou este puzzle de propósito (nunca falha "
                    "silenciosamente) — confira o log do pipeline pra saber qual "
                    "dos dois foi."
                )
            elif categoria == "precisa_geracao_externa":
                md.append(
                    "🎨 **Precisa de geração externa** (imagem ou áudio) — este "
                    "conceito ainda não vira PDF sozinho. Gere manualmente no Flow, "
                    "Nano Banana ou similar, usando os dados abaixo como base."
                )
                md.append("")
                render_dados_puzzle_generico(md, dados)
            elif categoria == "fisico_social":
                md.append("🎭 **Dinâmica física/social** — não precisa de nenhum material impresso.")
                md.append("")
                render_dados_puzzle_generico(md, dados)
            else:
                md.append("📋 **Pronto pra usar direto** — sem necessidade de PDF.")
                md.append("")
                render_dados_puzzle_generico(md, dados)

            md.append("")
            md.append("---")
            md.append("")

    npcs_ja_apresentados = {}
    mapas_ja_apresentados = {}

    for c in roteirista["cenas"]:
        num = c["numero"]
        md.append(f"## Cena {num}: {c['nome'].upper()}")
        md.append("")

        md.append("**Resumão da Cena**")
        md.append(f"- Onde: {c.get('local_ref', '')}")
        nomes_npcs = []
        for npc_id in c.get("npcs_presentes", []):
            npc = find_npc(npcs_data, npc_id)
            ident = apresenta_identidade(roteirista, npc_id, num)
            nome_mostrar = (
                ident["nome_aparente"] if ident else (npc["nome_exibicao"] if npc else npc_id)
            )
            nomes_npcs.append(nome_mostrar)
        md.append(f"- NPCs Presentes: {', '.join(nomes_npcs) if nomes_npcs else 'Nenhum'}")
        md.append(f"- Objetivo: {c.get('objetivo', '')}")
        gatilhos = "; ".join(c["transicao"]["gatilhos"])
        md.append(f"- Gatilho de Saída: {gatilhos}")
        cenas_cs = cs_por_cena.get(num, [])
        for cs in cenas_cs:
            md.append(f"- 🎬 Cutscene desta cena: **{cs.get('momento', '')}** (ver seção Cutscenes acima)")
        md.append("")

        md.append("**NPCs Desta Cena**")
        for npc_id in c.get("npcs_presentes", []):
            npc = find_npc(npcs_data, npc_id)
            if not npc:
                continue
            if npc_id in npcs_ja_apresentados:
                ident = apresenta_identidade(roteirista, npc_id, num)
                extra = (
                    f" (Identidade nesta cena: {ident['nome_aparente']}, "
                    f"revelada: {'Sim' if ident['identidade_revelada'] else 'Não'})"
                    if ident
                    else ""
                )
                md.append(
                    f"- {npc['nome_exibicao']} — já apresentado na "
                    f"Cena {npcs_ja_apresentados[npc_id]}.{extra}"
                )
            else:
                npcs_ja_apresentados[npc_id] = num
                md.append(f"- **{npc['nome_exibicao']}** ({npc.get('papel', '')})")
                md.append(f"  - Descrição: {npc.get('descricao_curta', '')}")
                if npc.get("combatente"):
                    md.append(f"  - Raça: {npc.get('raca', 'Humano')}")
                    md.append(f"  - Atributos: {attrs_str(npc.get('atributos', {}))}")
                    pc = npc.get("pericia_chave", {})
                    md.append(f"  - Perícia-Chave: {pc.get('nome', '-')} ({pc.get('dado', '-')})")
                    arma = npc.get("arma", {})
                    md.append(f"  - Arma: {arma.get('nome', '-')} (Dano: {arma.get('dano', '-')})")
                    md.append(f"  - Aparar: {npc.get('aparar', '-')}")
                    armadura = npc.get("armadura_bonus", 0) or 0
                    resistencia_str = f"{npc.get('resistencia', '-')}" + (f" ({armadura})" if armadura else "")
                    md.append(f"  - Resistência: {resistencia_str}")
                    if npc.get("carta_selvagem"):
                        md.append(
                            "  - **⭐ Carta Selvagem** — 3 Ferimentos antes de "
                            "Incapacitado, rola Dado Selvagem (d6) extra."
                        )
                md.append(f"  - Tipo de Token: {npc.get('tipo_token', '')}")
                md.append(f"  - Prompt de Imagem: `{npc.get('prompt_imagem', '')}`")
        md.append("")

        md.append("**Mapa**")
        local_ref = c.get("local_ref")
        mapa = find_mapa(cartografo, local_ref)
        if mapa:
            if local_ref in mapas_ja_apresentados:
                md.append(
                    f"Reaproveita o mapa {mapa['nome_local']}, já descrito na "
                    f"Cena {mapas_ja_apresentados[local_ref]}."
                )
            else:
                mapas_ja_apresentados[local_ref] = num
                md.append(f"- Nome: {mapa['nome_local']} ({mapa.get('tipo', '')})")
                pf = mapa.get("planta_funcional", {})
                for area in pf.get("areas", []):
                    conexoes = ", ".join(area.get("conexoes", []))
                    md.append(f"  - {area['nome']}: {area.get('descricao', '')} (Conexões: {conexoes})")
                if pf.get("elementos_especiais"):
                    md.append(f"  - Elementos Especiais: {', '.join(pf['elementos_especiais'])}")
                if mapa.get("planta_svg"):
                    md.append("")
                    md.append(
                        "Planta em SVG — copie este código e abra em um navegador ou "
                        "editor de SVG para visualizar renderizado (o Notion não exibe "
                        "SVG colado como imagem)."
                    )
                    md.append("```html")
                    md.append(mapa["planta_svg"])
                    md.append("```")
                md.append(f"  - Prompt Arte Estática: `{mapa.get('prompt_arte_estatica', '')}`")
                if mapa.get("prompt_arte_animada"):
                    md.append(f"  - Prompt Arte Animada: `{mapa['prompt_arte_animada']}`")
        else:
            md.append("Nenhum mapa definido para esta cena.")
        md.append("")

        md.append("**Documentos**")
        cena_docs = find_documentos(docs, num)
        if cena_docs:
            for d in cena_docs:
                md.append(f"- **{d['nome']}**")
                if d.get("tipo_saida") == "pdf":
                    md.append(f"  - Conteúdo: {d.get('conteudo_texto', '')}")
                else:
                    md.append(f"  - Prompt Mockup: `{d.get('prompt_mockup', '')}`")
        else:
            md.append("Nenhum documento nesta cena.")
        md.append("")

        md.append("**Trilha Sonora e Efeitos Sonoros**")
        s = find_sonoplastia(sono, num)
        if s:
            for t in s.get("trilha_sonora", []):
                md.append(f"- {t['momento']}: `{t['busca_youtube']}`")
            if s.get("efeitos_sonoros"):
                md.append(f"- Efeitos: {', '.join(s['efeitos_sonoros'])}")
        md.append("")

        md.append("**Texto de Leitura**")
        md.append(f"> {c.get('texto_leitura', '')}")
        md.append("")

        md.append("**Dificuldades**")
        for d in c.get("dificuldades", []):
            sinal = "+" if d["modificador"] > 0 else ""
            md.append(f"- {d['acao']} — Perícia: {d['pericia']} | Modificador: {sinal}{d['modificador']}")
        md.append("")

        md.append("**Transição**")
        prox = c["transicao"]["proxima_cena"]
        prox_str = "Finais Possíveis" if prox == "finais" else f"Cena {prox}"
        md.append(f"- Gatilhos: {'; '.join(c['transicao']['gatilhos'])}")
        md.append(f"- Próxima Cena: {prox_str}")
        md.append("")
        md.append("---")
        md.append("")

    md.append("## Finais Possíveis")
    for i, f in enumerate(roteirista["finais"], 1):
        md.append(f"{i}. **{f['nome']}**")
        md.append("")
        md.append(f"- Consequência: {f['consequencia']}")
        for cs in cs_por_final.get(f["nome"], []):
            md.append(f"- 🎬 Cutscene: **{cs.get('momento', '')}** (ver seção Cutscenes acima)")
        if f.get("texto_leitura"):
            md.append("")
            md.append("**Texto de Leitura (final)**")
            md.append(f"> {f['texto_leitura']}")
        md.append("")
    md.append("---")
    md.append("")

    md.append("## Avanço ao Final da Sessão")
    md.append("Regra padrão: 1 Avanço por sessão jogada, independente do final escolhido.")
    md.append("")
    for f in roteirista["finais"]:
        md.append(
            f"- **Para o final \"{f['nome']}\":** considere um bônus temático que reflita "
            "a consequência acima (uma nova Vantagem, um Contato, uma penalidade "
            "narrativa, ou nenhum bônus mecânico e apenas peso narrativo futuro) — "
            "a critério do mestre."
        )
    md.append("")

    text = "\n".join(md)
    saida = caminho("07-compilado.md")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Markdown gerado sem uso de IA — {saida} ({len(text)} caracteres).")


if __name__ == "__main__":
    main()
