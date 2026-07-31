import json
import os
import sys

TABELA_RESISTENCIA = {"d4": 4, "d6": 5, "d8": 6, "d10": 7, "d12": 8}


def main():
    path = "output/03-npcs.json"
    if not os.path.exists(path):
        print("ERRO: output/03-npcs.json não encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    corrigidos = 0
    for npc in data.get("npcs", []):
        if not npc.get("combatente"):
            continue
        vigor = npc.get("atributos", {}).get("vigor")
        base = TABELA_RESISTENCIA.get(vigor)
        if base is None:
            print(f"AVISO: NPC '{npc.get('nome_exibicao')}' tem Vigor inválido ('{vigor}'), Resistência não recalculada.", file=sys.stderr)
            continue
        armadura = npc.get("armadura_bonus", 0) or 0
        nova_resistencia = base + armadura
        if npc.get("resistencia") != nova_resistencia:
            npc["resistencia"] = nova_resistencia
            corrigidos += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Resistência recalculada e corrigida em {corrigidos} NPC(s) combatente(s).")


if __name__ == "__main__":
    main()
