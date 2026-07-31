import json
import os
import sys
import urllib.request
import urllib.error


def read_file(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def main():
    instructions = read_file(".github/agents/07-compilador.md")
    reference = read_file(".github/agents/referencia-swade.md")

    if not instructions:
        print("ERRO: .github/agents/07-compilador.md não encontrado.", file=sys.stderr)
        sys.exit(1)

    input_files = [
        "01-roteirista.json",
        "02-direcao-arte.json",
        "03-npcs.json",
        "04-cartografo.json",
        "05-sonoplastia.json",
        "06-documentos.json",
    ]

    prompt_parts = [
        "Você deve seguir estas instruções de sistema rigorosamente:\n\n" + instructions
    ]
    if reference:
        prompt_parts.append("\n\nReferência oficial de regras SWADE:\n\n" + reference)

    found_any = False
    for name in input_files:
        content = read_file(os.path.join("output", name))
        if content:
            found_any = True
            prompt_parts.append(f"\n\nArquivo {name}:\n```json\n{content}\n```")

    if not found_any:
        print("ERRO: nenhum arquivo de entrada encontrado em output/.", file=sys.stderr)
        sys.exit(1)

    prompt_parts.append(
        "\n\nGere APENAS o documento markdown final pedido nas instruções acima. "
        "Não inclua nenhum comentário seu antes ou depois, nem blocos de código "
        "markdown envolvendo o resultado inteiro — a resposta deve ser o markdown puro."
    )
    full_prompt = "".join(prompt_parts)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: variável de ambiente GEMINI_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("COMPILADOR_MODEL", "gemini-3.5-flash")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    body = json.dumps({"contents": [{"parts": [{"text": full_prompt}]}]}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERRO na chamada à API Gemini: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print("ERRO: resposta da API não trouxe o texto esperado.", file=sys.stderr)
        print(json.dumps(data, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", "07-compilado.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Markdown salvo em {out_path} ({len(text)} caracteres).")


if __name__ == "__main__":
    main()
