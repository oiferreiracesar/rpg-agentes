import argparse
import json
import os
import sys

# Cada categoria mapeia pra uma das 9 raças oficiais do referencia-swade.md.
# As palavras-chave procuram indícios da FORMA FÍSICA na descrição do
# Pokémon, na mesma lógica da tabela Espécie→Raça do referencia-pokemon.md.
# A ordem importa: categorias mais específicas vêm primeiro, pra "fumaça
# roxa flutuante" não cair errado em "quatro patas" só por acaso de outra
# palavra genérica.
CATEGORIAS = [
    ("Elfo", [
        "fantasma", "espectral", "espírito", "gasosa", "gasoso", "fumaça",
        "etéreo", "etérea", "psíquic", "flutuante", "flutua", "translúcid",
    ]),
    ("Androide", [
        "metálic", "mecânic", "robótic", "mineral", "engrenagem", "metal",
        "artificial", "construto",
    ]),
    ("Aviano", [
        "pássaro", "ave ", "asas", "asa ", "pena", "penas", "bico", "voando",
        "voa ", "plumagem",
    ]),
    ("Aquariano", [
        "aquátic", "peixe", "nadadeira", "guelra", "marinho", "concha",
        "escamas molhadas",
    ]),
    ("Sáurio", [
        "réptil", "serpente", "escamas", "escamoso", "dragão", "lagart",
        "cauda de réptil", "sibilando",
    ]),
    ("Pequenino", [
        "filhote pequeno", "minúsculo", "diminuto", "bolinha",
    ]),
    ("Rakashano", [
        "canino", "felino", "mamífero", "quatro patas", "pelos", "pelagem",
        "garras", "focinho", "cauda peluda", "rosnando", "rosnad",
    ]),
]

# Modificador de Resistência real de cada raça, do referencia-swade.md —
# usado pra manter "modificador_racial_resistencia" consistente com a raça
# corrigida (senão o corrigir_resistencia.py calcularia com o modificador
# da raça errada antiga).
MODIFICADOR_RESISTENCIA_POR_RACA = {
    "Humano": 0, "Elfo": 0, "Meio-Elfo": 0, "Aquariano": 1, "Aviano": -1,
    "Pequenino": -1, "Rakashano": 0, "Sáurio": 0, "Androide": 0,
}


def inferir_raca(npc):
    texto = " ".join([
        npc.get("nome_exibicao", ""),
        npc.get("descricao_curta", ""),
        npc.get("diretriz_interpretacao", ""),
    ]).lower()

    for raca, palavras_chave in CATEGORIAS:
        if any(p in texto for p in palavras_chave):
            return raca
    return None  # não conseguiu inferir com confiança


def eh_pokemon(npc, universo):
    if npc.get("treinador_id"):
        return True
    if universo == "pokemon" and npc.get("combatente"):
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta onde estão os JSONs (padrão: output)")
    args = parser.parse_args()
    p = args.pasta

    universo_path = os.path.join(p, "00-universo.txt")
    universo = None
    if os.path.exists(universo_path):
        with open(universo_path, encoding="utf-8") as f:
            universo = f.read().strip()

    if universo != "pokemon":
        print(f"[{p}] Universo não é 'pokemon' (é '{universo}') — nada a corrigir aqui.")
        return

    path = os.path.join(p, "03-npcs.json")
    if not os.path.exists(path):
        print(f"ERRO: {path} não encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    corrigidos = 0
    nao_inferidos = []

    for npc in data.get("npcs", []):
        if not eh_pokemon(npc, universo):
            continue
        if npc.get("raca") != "Humano":
            continue  # já não é o bug que estamos corrigindo

        nova_raca = inferir_raca(npc)
        if nova_raca:
            print(
                f"[{p}] Corrigido: '{npc.get('nome_exibicao')}' raça 'Humano' -> "
                f"'{nova_raca}' (inferido da descrição)"
            )
            npc["raca"] = nova_raca
            npc["modificador_racial_resistencia"] = MODIFICADOR_RESISTENCIA_POR_RACA.get(nova_raca, 0)
            corrigidos += 1
        else:
            nao_inferidos.append(npc.get("nome_exibicao", npc.get("id", "?")))

    if nao_inferidos:
        print(
            f"[{p}] AVISO: não consegui inferir raça pra: {', '.join(nao_inferidos)} "
            f"— ficaram como 'Humano' mesmo, confira manualmente (a descrição não "
            f"deu nenhuma pista clara de forma física).",
            file=sys.stderr,
        )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[{p}] Total: {corrigidos} raça(s) de Pokémon corrigida(s) automaticamente.")


if __name__ == "__main__":
    main()
