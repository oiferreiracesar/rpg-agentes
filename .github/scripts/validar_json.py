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


def validar_roteirista(v, data):
    if data is None:
        return
    for campo in ("metadados", "premissa", "twists", "cenas", "finais"):
        if campo not in data:
            v.erro(f"01-roteirista.json: campo obrigatório '{campo}' ausente")

    if len(data.get("finais", [])) < 3:
        v.aviso("01-roteirista.json: menos de 3 finais definidos")

    for f in data.get("finais", []):
        if not f.get("texto_leitura"):
            v.aviso(f"01-roteirista.json: final '{f.get('nome','?')}' sem 'texto_leitura' (o fechamento narrado não vai aparecer no compilado)")

    numeros_cena = set()
    for c in data.get("cenas", []):
        num = c.get("numero")
        numeros_cena.add(num)
        origem = f"01-roteirista.json, Cena {num}"

        for d in c.get("dificuldades", []):
            if "acao" not in d:
                v.erro(f"{origem}: dificuldade sem campo 'acao' (confira se não ficou 'action' em inglês)")
            if "pericia" in d:
                checar_pericia(v, origem, d["pericia"])
            mod = d.get("modificador")
            if isinstance(mod, str):
                v.erro(f"{origem}: 'modificador' veio como texto ('{mod}') em vez de número")
            # nota: modificador negativo é válido de propósito (penalidade) — não é erro

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
                v.aviso(f"01-roteirista.json: identidade oculta de '{npc_id}' referencia cena {ap.get('cena')} que não existe")


def validar_npcs(v, data):
    if data is None:
        return
    for npc in data.get("npcs", []):
        nome = npc.get("nome_exibicao", npc.get("id", "?"))
        origem = f"03-npcs.json, NPC '{nome}'"

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


def validar_sonoplastia(v, data, roteirista):
    if data is None or roteirista is None:
        return
    cenas_roteirista = {c["numero"] for c in roteirista.get("cenas", [])}
    cenas_sono = {s["cena"] for s in data.get("sonoplastia", [])}
    faltando = cenas_roteirista - cenas_sono
    if faltando:
        v.erro(f"05-sonoplastia.json: faltam entradas para as cenas {sorted(faltando)}")


def validar_animador(v, data, roteirista):
    if data is None or roteirista is None:
        return
    cenas_validas = {c["numero"] for c in roteirista.get("cenas", [])}
    finais_validos = {f["nome"] for f in roteirista.get("finais", [])}
    for cs in data.get("cutscenes", []):
        cena_ref = cs.get("cena_ref")
        if cena_ref is not None and cena_ref not in cenas_validas:
            v.aviso(f"08-animador.json: cutscene '{cs.get('momento','?')}' referencia cena {cena_ref} que não existe")
        final_ref = cs.get("final_ref")
        if final_ref and final_ref not in finais_validos:
            v.aviso(f"08-animador.json: cutscene '{cs.get('momento','?')}' referencia final '{final_ref}' que não existe nos finais do roteirista")


def validar_improviso(v, data, npcs_data):
    if data is None or npcs_data is None:
        return
    ids_validos = {n["id"] for n in npcs_data.get("npcs", [])}
    for entry in data.get("banco_de_falas", []):
        npc_id = entry.get("npc_id")
        if npc_id not in ids_validos:
            v.aviso(f"09-improviso.json: banco de falas referencia npc_id '{npc_id}' que não existe em 03-npcs.json")


def main():
    v = Validador()

    roteirista = carregar_json(v, "output/01-roteirista.json")
    npcs = carregar_json(v, "output/03-npcs.json")
    cartografo = carregar_json(v, "output/04-cartografo.json")
    sonoplastia = carregar_json(v, "output/05-sonoplastia.json")
    animador = carregar_json(v, "output/08-animador.json")
    improviso = carregar_json(v, "output/09-improviso.json")

    if roteirista is not None:
        validar_roteirista(v, roteirista)
    if npcs is not None:
        validar_npcs(v, npcs)
    if sonoplastia is not None:
        validar_sonoplastia(v, sonoplastia, roteirista)
    if animador is not None:
        validar_animador(v, animador, roteirista)
    if improviso is not None:
        validar_improviso(v, improviso, npcs)
    _ = cartografo

    print("=" * 60)
    print("RELATÓRIO DE VALIDAÇÃO")
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
