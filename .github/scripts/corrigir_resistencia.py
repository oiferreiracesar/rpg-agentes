import json
import os
import sys

TABELA_RESISTENCIA = {"d4": 4, "d6": 5, "d8": 6, "d10": 7, "d12": 8}
TABELA_APARAR_BASE = {"d4": 2, "d6": 3, "d8": 4, "d10": 5, "d12": 6}


def main():
    path = "output/03-npcs.json"
    if not os.path.exists(path):
        print("ERRO: output/03-npcs.json não encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    corrigidos_resistencia = 0
    corrigidos_aparar = 0

    for npc in data.get("npcs", []):
        if not npc.get("combatente"):
            continue

        # --- Resistência = 2 + metade do dado de Vigor + armadura ---
        vigor = npc.get("atributos", {}).get("vigor")
        base = TABELA_RESISTENCIA.get(vigor)
        if base is None:
            print(f"AVISO: NPC '{npc.get('nome_exibicao')}' tem Vigor inválido ('{vigor}'), Resistência não recalculada.", file=sys.stderr)
        else:
            armadura = npc.get("armadura_bonus", 0) or 0
            nova_resistencia = base + armadura
            if npc.get("resistencia") != nova_resistencia:
                npc["resistencia"] = nova_resistencia
                corrigidos_resistencia += 1

        # --- Aparar = 2 + metade do dado de Lutar (2 se não tiver Lutar treinado) ---
        pericia_chave = npc.get("pericia_chave", {})
        if pericia_chave.get("nome") == "Lutar":
            lutar_dado = pericia_chave.get("dado")
            base_aparar = TABELA_APARAR_BASE.get(lutar_dado)
            if base_aparar is None:
                print(f"AVISO: NPC '{npc.get('nome_exibicao')}' tem dado de Lutar inválido ('{lutar_dado}'), Aparar não calculado.", file=sys.stderr)
                nova_aparar = 2
            else:
                nova_aparar = 2 + base_aparar
        else:
            nova_aparar = 2

        if npc.get("aparar") != nova_aparar:
            npc["aparar"] = nova_aparar
            corrigidos_aparar += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Resistência recalculada em {corrigidos_resistencia} NPC(s) combatente(s).")
    print(f"Aparar calculado em {corrigidos_aparar} NPC(s) combatente(s).")


if __name__ == "__main__":
    main()
