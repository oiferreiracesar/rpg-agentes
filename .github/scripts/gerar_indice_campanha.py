import argparse
import json
import os
import sys


def read_json_opt(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def titulo_da_sessao(pasta_raiz, numero):
    """Tenta pegar o título real gerado pelo Roteirista daquela sessão;
    cai pro título do 00-campanha.json se a sessão ainda não foi gerada."""
    roteirista = read_json_opt(os.path.join(pasta_raiz, f"sessao_{numero}", "01-roteirista.json"))
    if roteirista:
        return roteirista.get("metadados", {}).get("titulo")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta raiz da campanha, onde está 00-campanha.json (padrão: output)")
    args = parser.parse_args()
    p = args.pasta

    campanha_path = os.path.join(p, "00-campanha.json")
    if not os.path.exists(campanha_path):
        print(f"ERRO: {campanha_path} não encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(campanha_path, encoding="utf-8") as f:
        data = json.load(f)

    c = data.get("campanha", {})
    md = []

    md.append(f"# {c.get('titulo', 'Campanha')}")
    md.append("")
    md.append(f"**Universo:** {c.get('universo', 'genérico')}  ")
    md.append(f"**Número de sessões:** {c.get('numero_de_sessoes', '?')}  ")
    md.append("")
    md.append("---")
    md.append("")

    vilao = c.get("vilao_da_campanha", {})
    if vilao:
        md.append("## 🎭 O Vilão da Campanha")
        md.append(f"**{vilao.get('nome', '')}**")
        md.append("")
        md.append(f"**Verdade por trás:** {vilao.get('verdade_por_tras', '')}")
        md.append("")
        md.append(f"**Revelação final:** {vilao.get('revelacao_final', '')}")
        md.append("")
        md.append(
            "> ⚠️ Esta seção é só pro mestre. A revelação final não deve ser "
            "compartilhada com o grupo antes da última sessão."
        )
        md.append("")
        md.append("---")
        md.append("")

    npcs = c.get("npcs_recorrentes", [])
    if npcs:
        md.append("## 🧑 NPCs Recorrentes")
        md.append("")
        md.append("| Nome | Papel | Arco (1ª → última sessão) |")
        md.append("| --- | --- | --- |")
        for n in npcs:
            md.append(f"| {n.get('nome', '')} | {n.get('papel', '')} | {n.get('arco', '')} |")
        md.append("")
        md.append("---")
        md.append("")

    sessoes = c.get("sessoes", [])
    md.append("## 📖 Sessões")
    md.append("")

    for s in sessoes:
        num = s.get("numero")
        pasta_sessao = os.path.join(p, f"sessao_{num}")
        compilado_path = os.path.join(pasta_sessao, "07-compilado.md")
        gerada = os.path.exists(compilado_path)

        titulo_real = titulo_da_sessao(p, num) or s.get("titulo", f"Sessão {num}")
        status = "✅ Gerada" if gerada else "⏳ Ainda não gerada"

        md.append(f"### Sessão {num}: {titulo_real}")
        md.append("")
        md.append(f"**Status:** {status}")
        md.append(f"**Papel no arco:** {s.get('papel_no_arco', '')}")
        md.append("")
        md.append(f"**Resumo:** {s.get('resumo', '')}")
        md.append("")
        if s.get("npcs_recorrentes_presentes"):
            md.append(f"**NPCs Recorrentes presentes:** {', '.join(s['npcs_recorrentes_presentes'])}")
            md.append("")
        md.append(f"**Verdade revelada nesta sessão:** {s.get('verdade_revelada_nesta_sessao', '')}")
        md.append("")
        if s.get("gancho_para_proxima"):
            md.append(f"**Gancho para a próxima:** {s['gancho_para_proxima']}")
            md.append("")
        if gerada:
            md.append(f"📄 [Abrir aventura completa desta sessão](sessao_{num}/07-compilado.md)")
        else:
            md.append(
                f"_Esta sessão ainda não foi gerada — rode o pipeline com "
                f"`--pasta output/sessao_{num}` pra gerar o conteúdo completo dela._"
            )
        md.append("")
        md.append("---")
        md.append("")

    text = "\n".join(md)
    saida = os.path.join(p, "00-indice-campanha.md")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(text)

    total = len(sessoes)
    geradas = sum(1 for s in sessoes if os.path.exists(os.path.join(p, f"sessao_{s.get('numero')}", "07-compilado.md")))
    print(f"Índice de campanha gerado — {saida} ({geradas}/{total} sessões já geradas).")


if __name__ == "__main__":
    main()
