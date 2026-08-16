import argparse
import json
import os
import sys

TABELA_RESISTENCIA = {"d4": 4, "d6": 5, "d8": 6, "d10": 7, "d12": 8}
TABELA_APARAR_BASE = {"d4": 2, "d6": 3, "d8": 4, "d10": 5, "d12": 6}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta onde estão os JSONs (padrão: output)")
    args = parser.parse_args()

    path = os.path.join(args.pasta, "03-npcs.json")
    if not os.path.exists(path):
        print(f"ERRO: {path} não encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    corrigidos_resistencia = 0
    corrigidos_aparar = 0
    corrigidos_dano = 0
    corrigidos_atributo = 0

    for npc in data.get("npcs", []):
        if not npc.get("combatente"):
            continue

        # Se algum dos 5 atributos ficou faltando (a IA esqueceu de gerar),
        # preenche com d6 (o "meio-termo" razoável) em vez de travar o
        # pipeline inteiro — mas avisa bem alto, porque um NPC importante
        # (chefe de cena, vilão nomeado) merece ficha revisada à mão depois.
        atributos = npc.setdefault("atributos", {})
        for attr in ("agilidade", "astucia", "espirito", "forca", "vigor"):
            if attr not in atributos or not atributos[attr]:
                atributos[attr] = "d6"
                corrigidos_atributo += 1
                print(
                    f"AVISO: NPC '{npc.get('nome_exibicao')}' estava sem o atributo "
                    f"'{attr}' — preenchido com d6 (padrão). Confira manualmente se "
                    f"esse NPC é importante pra narrativa.",
                    file=sys.stderr,
                )

        # "dado" x "dano" são parecidos, e a IA já confundiu os dois —
        # normaliza antes de qualquer outra coisa, senão o dano fica vazio
        # mesmo com o valor certo presente, só no campo errado.
        arma = npc.get("arma")
        if isinstance(arma, dict) and not arma.get("dano") and arma.get("dado"):
            arma["dano"] = arma.pop("dado")
            corrigidos_dano += 1

        vigor = npc.get("atributos", {}).get("vigor")
        base = TABELA_RESISTENCIA.get(vigor)
        if base is None:
            print(f"AVISO: NPC '{npc.get('nome_exibicao')}' tem Vigor inválido ('{vigor}'), Resistência não recalculada.", file=sys.stderr)
        else:
            armadura = npc.get("armadura_bonus", 0) or 0
            modificador_racial = npc.get("modificador_racial_resistencia", 0) or 0
            nova_resistencia = base + armadura + modificador_racial
            if npc.get("resistencia") != nova_resistencia:
                npc["resistencia"] = nova_resistencia
                corrigidos_resistencia += 1

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

    print(f"[{args.pasta}] Resistência recalculada em {corrigidos_resistencia} NPC(s) combatente(s).")
    print(f"[{args.pasta}] Aparar calculado em {corrigidos_aparar} NPC(s) combatente(s).")
    print(f"[{args.pasta}] Campo 'dano' da arma corrigido (de 'dado') em {corrigidos_dano} NPC(s) combatente(s).")
    print(f"[{args.pasta}] Atributo(s) faltando preenchido(s) com d6 em {corrigidos_atributo} caso(s).")


if __name__ == "__main__":
    main()
