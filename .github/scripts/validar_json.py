import argparse
import json
import os
import sys

OFFICIAL_SKILLS = {
    "Atirar", "Atletismo", "Cavalgar", "Ciência", "Ciência Estranha",
    "Conhecimento Acadêmico", "Conhecimento Batalha", "Conhecimento Geral",
    "Conjurar", "Consertar", "Curar", "Dirigir", "Eletrônica", "Fé", "Foco",
    "Furtividade", "Hackear", "Idiomas", "Intimidar", "Jogar", "Ladinagem",
    "Lutar", "Navegar", "Ocultismo", "Perceber", "Performance", "Persuadir",
    "Pesquisar", "Pilotar", "Provocar", "Psiônicos", "Sobrevivência",
}

KNOWN_WRONG_NAMES = {
    "Investigação": "use Pesquisar ou Perceber",
    "Investigar": "use Pesquisar ou Perceber",
    "Persuasão": "o nome oficial é Persuadir",
    "Intimidação": "o nome oficial é Intimidar",
    "Liderança": "isso é uma Vantagem, não uma perícia",
    "Notice": "nome em inglês — deveria ser Perceber",
    "Persuasion": "nome em inglês — deveria ser Persuadir",
    "Shooting": "nome em inglês — deveria ser Atirar",
    "Intimidation": "nome em inglês — deveria ser Intimidar",
}

RANGED_WEAPON_HINTS = (
    "pistola", "revólver", "revolver", "rifle", "espingarda", "arco",
    "besta", "colt", "winchester", "arma de fogo",
)

RACAS_OFICIAIS = {
    "Humano", "Elfo", "Meio-Elfo", "Aquariano", "Aviano", "Pequenino",
    "Rakashano", "Sáurio", "Androide",
}

UNIVERSOS_COM_ATAQUE_ELEMENTAL = {"pokemon", "digimon"}


class Validador:
    def __init__(self):
        self.erros = []
        self.avisos = []

    def erro(self, msg):
        self.erros.append(msg)

    def aviso(self, msg):
        self.avisos.append(msg)

    def ok(self):
        return len(self.erros) == 0


def carregar_json(v, path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        v.erro(f"{path}: JSON inválido — {e}")
        return None


def checar_pericia(v, origem, nome_pericia):
    if nome_pericia in KNOWN_WRONG_NAMES:
        v.erro(f"{origem}: perícia '{nome_pericia}' inválida — {KNOWN_WRONG_NAMES[nome_pericia]}")
    elif nome_pericia not in OFFICIAL_SKILLS:
        v.aviso(f"{origem}: perícia '{nome_pericia}' não está na lista oficial (pode ser erro de digitação)")


def validar_npcs_presentes_existem(v, roteirista, npcs_data, nome_roteirista, nome_npcs):
    if roteirista is None or npcs_data is None:
        return
    ids_existentes = {n["id"] for n in npcs_data.get("npcs", []) if "id" in n}
    for c in roteirista.get("cenas", []):
        for npc_id in c.get("npcs_presentes", []):
            if npc_id not in ids_existentes:
                v.erro(
                    f"{nome_roteirista}, Cena {c.get('numero')}: 'npcs_presentes' "
                    f"referencia '{npc_id}', que não existe em {nome_npcs} — "
                    f"o mestre não vai ter ficha nenhuma pra esse NPC"
                )


def validar_racas_pokemon(v, npcs_data, nome_arquivo, universo=None):
    """Todo Pokémon precisa usar uma das 7 raças que o referencia-pokemon.md
    mapeia — nunca 'Humano', que é reservado pro treinador/Tamer em si.
    Verifica dois casos: (1) qualquer NPC com 'treinador_id' (claramente um
    Pokémon de alguém), e (2) em universo "pokemon", QUALQUER NPC combatente
    com raça Humano — mesmo sem treinador_id, já que Pokémon selvagens sem
    dono também não deveriam ser 'Humano' (esse caso passava batido antes)."""
    if npcs_data is None:
        return
    for npc in npcs_data.get("npcs", []):
        eh_pokemon_com_dono = bool(npc.get("treinador_id"))
        eh_combatente_suspeito = universo == "pokemon" and npc.get("combatente") and npc.get("raca") == "Humano"

        if npc.get("raca") == "Humano" and (eh_pokemon_com_dono or eh_combatente_suspeito):
            motivo = "tem 'treinador_id'" if eh_pokemon_com_dono else "é combatente num universo Pokémon (raro um humano lutar diretamente)"
            v.aviso(
                f"{nome_arquivo}, NPC '{npc.get('nome_exibicao')}': {motivo} mas a "
                f"raça está como 'Humano' — confira se não deveria ser um Pokémon "
                f"com outra raça (Aviano/Aquariano/Pequenino/Sáurio/Elfo/Androide/Rakashano)"
            )


def validar_roteirista(v, data, nome_arquivo):
    if data is None:
        return
    for campo in ("metadados", "premissa", "twists", "cenas", "finais"):
        if campo not in data:
            v.erro(f"{nome_arquivo}: campo obrigatório '{campo}' ausente")

    if len(data.get("finais", [])) < 3:
        v.aviso(f"{nome_arquivo}: menos de 3 finais definidos")

    for f in data.get("finais", []):
        if not f.get("texto_leitura"):
            v.aviso(f"{nome_arquivo}: final '{f.get('nome','?')}' sem 'texto_leitura' (o fechamento narrado não vai aparecer no compilado)")

    numeros_cena = set()
    for c in data.get("cenas", []):
        num = c.get("numero")
        numeros_cena.add(num)
        origem = f"{nome_arquivo}, Cena {num}"

        for d in c.get("dificuldades", []):
            if "acao" not in d:
                v.erro(f"{origem}: dificuldade sem campo 'acao' (confira se não ficou 'action' em inglês)")
            if "pericia" in d:
                checar_pericia(v, origem, d["pericia"])
            mod = d.get("modificador")
            if isinstance(mod, str):
                v.erro(f"{origem}: 'modificador' veio como texto ('{mod}') em vez de número")

        transicao = c.get("transicao", {})
        gatilhos = transicao.get("gatilhos")
        if not isinstance(gatilhos, list):
            v.erro(f"{origem}: 'transicao.gatilhos' deveria ser uma lista, veio {type(gatilhos).__name__}")
        prox = transicao.get("proxima_cena")
        if prox is None:
            v.erro(f"{origem}: 'transicao.proxima_cena' ausente")
        elif prox != "finais" and not isinstance(prox, int):
            v.erro(f"{origem}: 'transicao.proxima_cena' inválido ({prox!r}) — deve ser número ou \"finais\"")

    identidades = data.get("identidades_ocultas", [])
    for io in identidades:
        npc_id = io.get("id")
        for ap in io.get("aparencias_por_cena", []):
            if ap.get("cena") not in numeros_cena:
                v.aviso(f"{nome_arquivo}: identidade oculta de '{npc_id}' referencia cena {ap.get('cena')} que não existe")


def validar_npcs(v, data, nome_arquivo, universo=None):
    if data is None:
        return

    ids_existentes = {n["id"]: n for n in data.get("npcs", []) if "id" in n}

    for npc in data.get("npcs", []):
        nome = npc.get("nome_exibicao", npc.get("id", "?"))
        origem = f"{nome_arquivo}, NPC '{nome}'"

        raca = npc.get("raca")
        if raca and raca not in RACAS_OFICIAIS:
            v.aviso(f"{origem}: raça '{raca}' não é uma das 9 raças oficiais")

        # Fix A: valida treinador_id / tamer_id (referências internas entre NPCs)
        for campo in ("treinador_id", "tamer_id"):
            ref_id = npc.get(campo)
            if ref_id is None:
                continue
            if ref_id not in ids_existentes:
                v.erro(f"{origem}: '{campo}' aponta para '{ref_id}', que não existe em {nome_arquivo}")
            else:
                dono = ids_existentes[ref_id]
                if dono.get("combatente"):
                    v.aviso(
                        f"{origem}: '{campo}' aponta para '{ref_id}', que está marcado "
                        f"como combatente — treinador/Tamer deveria ser sempre não-combatente"
                    )

        if npc.get("combatente"):
            atributos = npc.get("atributos", {})
            for attr in ("agilidade", "astucia", "espirito", "forca", "vigor"):
                if attr not in atributos:
                    v.erro(f"{origem}: combatente sem atributo '{attr}'")

            pc = npc.get("pericia_chave", {})
            if "nome" in pc:
                checar_pericia(v, origem, pc["nome"])

            arma = npc.get("arma", {})
            dano = arma.get("dano", "")
            nome_arma = (arma.get("nome") or "").lower()
            eh_a_distancia = any(h in nome_arma for h in RANGED_WEAPON_HINTS)
            if not dano or dano.strip() in ("", "-"):
                v.erro(f"{origem}: arma '{arma.get('nome','?')}' sem dano preenchido — nunca pode ficar vazio ou '-'")
            elif eh_a_distancia and "força+" in dano.lower().replace("forca+", "força+"):
                v.erro(
                    f"{origem}: arma '{arma.get('nome')}' parece ser à distância mas o dano "
                    f"usa 'Força+dX' ({dano}) — armas à distância devem ter dado fixo"
                )
            # Nesses universos, ataques "corpo a corpo no nome" costumam ser
            # elementais/energéticos por natureza (garra elétrica, rajada de
            # vento) — a heurística de "nome parece corpo a corpo" gera
            # falso positivo demais aqui, então pulamos esse aviso específico.
            elif not eh_a_distancia and dano and "+" not in dano and "força" not in dano.lower() and universo not in UNIVERSOS_COM_ATAQUE_ELEMENTAL:
                v.aviso(
                    f"{origem}: arma '{arma.get('nome')}' parece corpo a corpo mas o dano "
                    f"('{dano}') não segue o padrão Força+dX — confira manualmente"
                )

            if "carta_selvagem" not in npc:
                v.aviso(f"{origem}: campo 'carta_selvagem' ausente — combatente deveria sempre declarar true ou false")

            armadura = npc.get("armadura_bonus", 0) or 0
            if armadura and "armadura" not in (npc.get("descricao_curta") or "").lower():
                v.aviso(f"{origem}: tem 'armadura_bonus' ({armadura}) mas a descrição não menciona armadura — confira se não ficou inconsistente")

            aparar = npc.get("aparar")
            resistencia = npc.get("resistencia")
            if aparar is None or resistencia is None:
                v.erro(f"{origem}: falta 'aparar' ou 'resistencia' — o script de fórmulas (corrigir_resistencia.py) não parece ter rodado nesse NPC")
            elif aparar == 0 or resistencia == 0:
                v.aviso(f"{origem}: 'aparar' ou 'resistencia' está em 0 — valor mínimo esperado é 2 (destreinado); confira se o script de fórmulas rodou depois deste NPC ter sido gerado")
        else:
            if npc.get("tipo_token") != "retrato":
                v.aviso(f"{origem}: não-combatente com tipo_token diferente de 'retrato'")
            if not (npc.get("papel") or npc.get("diretriz_interpretacao")):
                v.aviso(f"{origem}: não-combatente sem 'papel' nem 'diretriz_interpretacao' — função narrativa não está clara pro mestre")


def validar_mapas_referenciados(v, roteirista, cartografo, nome_arquivo_roteirista, nome_arquivo_cartografo):
    # Fix B: todo local_ref citado numa cena precisa ter mapa correspondente
    if roteirista is None or cartografo is None:
        return
    locais_validos = {m["local_ref"] for m in cartografo.get("mapas", []) if "local_ref" in m}
    for c in roteirista.get("cenas", []):
        local_ref = c.get("local_ref")
        if local_ref and local_ref not in locais_validos:
            v.erro(
                f"{nome_arquivo_roteirista}, Cena {c.get('numero')}: local_ref "
                f"'{local_ref}' não tem mapa correspondente em {nome_arquivo_cartografo}"
            )


def validar_documentos_referenciados(v, roteirista, docs, nome_arquivo_docs):
    # Fix C: todo cena_onde_aparece de um documento precisa referenciar cena real
    if roteirista is None or docs is None:
        return
    cenas_validas = {c["numero"] for c in roteirista.get("cenas", [])}
    for d in docs.get("documentos", []):
        cena_ref = d.get("cena_onde_aparece")
        if cena_ref is not None and cena_ref not in cenas_validas:
            v.aviso(
                f"{nome_arquivo_docs}: documento '{d.get('nome','?')}' referencia "
                f"cena {cena_ref} que não existe — ele não vai aparecer em nenhuma cena do compilado"
            )


def validar_interrogatorios(v, roteirista, docs, nome_arquivo_roteirista, nome_arquivo_docs):
    """Universo L.A. Noire: toda pergunta marcada 'e_mentira': true precisa
    ter um 'documento_id_que_contradiz' válido, apontando pra um documento
    que existe de verdade em 06-documentos.json — senão o jogador nunca
    consegue usar essa prova, e a mecânica de Mentira fica impossível de
    jogar naquele ponto."""
    if roteirista is None:
        return
    ids_documentos = {d["id"] for d in (docs or {}).get("documentos", []) if "id" in d}
    cenas_por_numero = {c["numero"]: c for c in roteirista.get("cenas", []) if "numero" in c}

    for c in roteirista.get("cenas", []):
        interrogatorio = c.get("interrogatorio")
        if not interrogatorio:
            continue
        num_cena = c.get("numero")
        origem_base = f"{nome_arquivo_roteirista}, Cena {num_cena}, interrogatório"

        npc_id = interrogatorio.get("npc_id")
        if npc_id and npc_id not in c.get("npcs_presentes", []):
            v.aviso(
                f"{origem_base}: 'npc_id' ('{npc_id}') não está em 'npcs_presentes' "
                f"desta cena — confira se é o NPC certo"
            )

        for i, pergunta in enumerate(interrogatorio.get("perguntas", []), start=1):
            origem = f"{origem_base}, pergunta {i} ('{pergunta.get('topico','?')}')"
            if not pergunta.get("e_mentira"):
                continue

            doc_id = pergunta.get("documento_id_que_contradiz")
            if not doc_id:
                v.erro(
                    f"{origem}: marcada 'e_mentira': true mas sem "
                    f"'documento_id_que_contradiz' — a mentira não tem prova pra sustentar ela"
                )
                continue

            if docs is None:
                v.aviso(f"{origem}: cita documento '{doc_id}', mas {nome_arquivo_docs} ainda não foi gerado — confira depois")
                continue

            if doc_id not in ids_documentos:
                v.erro(
                    f"{origem}: referencia documento '{doc_id}', que não existe em "
                    f"{nome_arquivo_docs} — o jogador nunca vai conseguir usar essa prova"
                )
                continue

            doc = next((d for d in docs.get("documentos", []) if d.get("id") == doc_id), None)
            if doc:
                cena_doc = doc.get("cena_onde_aparece")
                if isinstance(cena_doc, int) and isinstance(num_cena, int) and cena_doc >= num_cena:
                    v.erro(
                        f"{origem}: a prova '{doc_id}' aparece na cena {cena_doc}, mas o "
                        f"interrogatório é na cena {num_cena} — a prova precisa ter sido "
                        f"encontrada ANTES, nunca na mesma cena ou depois"
                    )


def validar_sonoplastia(v, data, roteirista, nome_arquivo):
    if data is None or roteirista is None:
        return
    cenas_roteirista = {c["numero"] for c in roteirista.get("cenas", [])}
    cenas_sono = {s["cena"] for s in data.get("sonoplastia", [])}
    faltando = cenas_roteirista - cenas_sono
    if faltando:
        v.erro(f"{nome_arquivo}: faltam entradas para as cenas {sorted(faltando)}")


def validar_animador(v, data, roteirista, nome_arquivo):
    if data is None or roteirista is None:
        return
    cenas_validas = {c["numero"] for c in roteirista.get("cenas", [])}
    finais_validos = {f["nome"] for f in roteirista.get("finais", [])}
    for cs in data.get("cutscenes", []):
        cena_ref = cs.get("cena_ref")
        if cena_ref is not None and cena_ref not in cenas_validas:
            v.aviso(f"{nome_arquivo}: cutscene '{cs.get('momento','?')}' referencia cena {cena_ref} que não existe")
        final_ref = cs.get("final_ref")
        if final_ref and final_ref not in finais_validos:
            v.aviso(f"{nome_arquivo}: cutscene '{cs.get('momento','?')}' referencia final '{final_ref}' que não existe nos finais do roteirista")


def validar_improviso(v, data, npcs_data, nome_arquivo):
    if data is None or npcs_data is None:
        return
    ids_validos = {n["id"] for n in npcs_data.get("npcs", [])}
    for entry in data.get("banco_de_falas", []):
        npc_id = entry.get("npc_id")
        if npc_id not in ids_validos:
            v.aviso(f"{nome_arquivo}: banco de falas referencia npc_id '{npc_id}' que não existe em 03-npcs.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta onde estão os JSONs (padrão: output)")
    args = parser.parse_args()
    p = args.pasta

    def caminho(nome):
        return os.path.join(p, nome)

    v = Validador()

    universo_path = caminho("00-universo.txt")
    universo = None
    if os.path.exists(universo_path):
        with open(universo_path, encoding="utf-8") as f:
            universo = f.read().strip()

    roteirista = carregar_json(v, caminho("01-roteirista.json"))
    npcs = carregar_json(v, caminho("03-npcs.json"))
    cartografo = carregar_json(v, caminho("04-cartografo.json"))
    sonoplastia = carregar_json(v, caminho("05-sonoplastia.json"))
    documentos = carregar_json(v, caminho("06-documentos.json"))
    animador = carregar_json(v, caminho("08-animador.json"))
    improviso = carregar_json(v, caminho("09-improviso.json"))

    if roteirista is not None:
        validar_roteirista(v, roteirista, caminho("01-roteirista.json"))
    if npcs is not None:
        validar_npcs(v, npcs, caminho("03-npcs.json"), universo)
        validar_racas_pokemon(v, npcs, caminho("03-npcs.json"), universo)
    if roteirista is not None and npcs is not None:
        validar_npcs_presentes_existem(v, roteirista, npcs, caminho("01-roteirista.json"), caminho("03-npcs.json"))
    if roteirista is not None and cartografo is not None:
        validar_mapas_referenciados(v, roteirista, cartografo, caminho("01-roteirista.json"), caminho("04-cartografo.json"))
    if roteirista is not None and documentos is not None:
        validar_documentos_referenciados(v, roteirista, documentos, caminho("06-documentos.json"))
    if roteirista is not None:
        validar_interrogatorios(v, roteirista, documentos, caminho("01-roteirista.json"), caminho("06-documentos.json"))
    if sonoplastia is not None:
        validar_sonoplastia(v, sonoplastia, roteirista, caminho("05-sonoplastia.json"))
    if animador is not None:
        validar_animador(v, animador, roteirista, caminho("08-animador.json"))
    if improviso is not None:
        validar_improviso(v, improviso, npcs, caminho("09-improviso.json"))

    print("=" * 60)
    print(f"RELATÓRIO DE VALIDAÇÃO — {p}")
    print("=" * 60)

    if v.avisos:
        print(f"\n{len(v.avisos)} aviso(s) (não bloqueiam, mas vale conferir):")
        for a in v.avisos:
            print(f"  ⚠️  {a}")

    if v.erros:
        print(f"\n{len(v.erros)} ERRO(S) ENCONTRADO(S):")
        for e in v.erros:
            print(f"  ❌ {e}")
        print("\nCorrija os arquivos gerados antes de continuar.")
        sys.exit(1)

    print("\n✅ Nenhum erro encontrado. Pipeline pode continuar.")


if __name__ == "__main__":
    main()
