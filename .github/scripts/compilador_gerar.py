import json
import os
import sys


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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


def main():
    roteirista_path = "output/01-roteirista.json"
    if not os.path.exists(roteirista_path):
        print("ERRO: output/01-roteirista.json não encontrado.", file=sys.stderr)
        sys.exit(1)

    roteirista = read_json(roteirista_path)
    npcs_data = read_json_opt("output/03-npcs.json") or {"npcs": []}
    cartografo = read_json_opt("output/04-cartografo.json") or {"mapas": []}
    sono = read_json_opt("output/05-sonoplastia.json") or {"sonoplastia": []}
    docs = read_json_opt("output/06-documentos.json")

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

    md.append("## Resumão de Mesa")
    md.append("### NPCs Combatentes")
    combat_npcs = [n for n in npcs_data["npcs"] if n.get("combatente")]
    if combat_npcs:
        md.append("| Nome | Atributos | Perícia-Chave | Arma (Dano) | Resistência |")
        md.append("| :--- | :--- | :--- | :--- | :---: |")
        for n in combat_npcs:
            pc = n.get("pericia_chave", {})
            arma = n.get("arma", {})
            md.append(
                f"| {n['nome_exibicao']} | {attrs_str(n.get('atributos', {}))} | "
                f"{pc.get('nome', '-')} ({pc.get('dado', '-')}) | "
                f"{arma.get('nome', '-')} ({arma.get('dano', '-')}) | "
                f"{n.get('resistencia', '-')} |"
            )
    else:
        md.append("Nenhum NPC combatente nesta aventura.")
    md.append("")

    md.append("### Dificuldades das Cenas")
    for c in roteirista["cenas"]:
        difs = "; ".join(
            f"{d['pericia']} (mod. {d['modificador']}) — {d['acao']}"
            for d in c["dificuldades"]
        )
        md.append(f"- **Cena {c['numero']}:** {difs}")
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
                    md.append(f"  - Atributos: {attrs_str(npc.get('atributos', {}))}")
                    pc = npc.get("pericia_chave", {})
                    md.append(f"  - Perícia-Chave: {pc.get('nome', '-')} ({pc.get('dado', '-')})")
                    arma = npc.get("arma", {})
                    md.append(f"  - Arma: {arma.get('nome', '-')} (Dano: {arma.get('dano', '-')})")
                    md.append(f"  - Resistência: {npc.get('resistencia', '-')}")
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
            md.append(f"- {d['acao']} — Perícia: {d['pericia']} | Modificador: {d['modificador']}")
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
        md.append(f"   - Consequência: {f['consequencia']}")
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
    os.makedirs("output", exist_ok=True)
    with open("output/07-compilado.md", "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Markdown gerado sem uso de IA — output/07-compilado.md ({len(text)} caracteres).")


if __name__ == "__main__":
    main()
