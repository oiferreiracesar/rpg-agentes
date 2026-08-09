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


def validar_npcs(v, data, nome_arquivo):
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
            elif not eh_a_distancia and dano and "+" not in dano and "força" not in dano.lower():
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
        validar_npcs(v, npcs, caminho("03-npcs.json"))
    if roteirista is not None and cartografo is not None:
        validar_mapas_referenciados(v, roteirista, cartografo, caminho("01-roteirista.json"), caminho("04-cartografo.json"))
    if roteirista is not None and documentos is not None:
        validar_documentos_referenciados(v, roteirista, documentos, caminho("06-documentos.json"))
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
