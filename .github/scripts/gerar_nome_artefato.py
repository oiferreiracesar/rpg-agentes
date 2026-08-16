import argparse
import json
import os
import re
import sys


def normalize(text):
    repl = str.maketrans(
        "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇáàâãäéèêëíìîïóòôõöúùûüç",
        "AAAAAEEEEIIIIOOOOOUUUUCaaaaaeeeeiiiiooooouuuuc",
    )
    return text.translate(repl)


def slugify(titulo, fallback):
    if not titulo:
        return fallback
    limpo = normalize(titulo)
    limpo = re.sub(r"[^a-zA-Z0-9\s-]", "", limpo)
    limpo = re.sub(r"\s+", "-", limpo.strip())
    return limpo[:80] if limpo else fallback


def get_by_path(data, path):
    """Navega um dict usando um caminho tipo 'metadados.titulo'."""
    atual = data
    for chave in path.split("."):
        if not isinstance(atual, dict) or chave not in atual:
            return None
        atual = atual[chave]
    return atual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output")
    parser.add_argument("--arquivo", required=True, help="Nome do JSON a ler, ex: 01-roteirista.json")
    parser.add_argument("--campo", required=True, help="Caminho até o título, ex: metadados.titulo")
    parser.add_argument("--fallback", required=True, help="Nome padrão se o arquivo/campo não existir")
    args = parser.parse_args()

    caminho = os.path.join(args.pasta, args.arquivo)
    titulo = None
    if os.path.exists(caminho):
        try:
            with open(caminho, encoding="utf-8") as f:
                data = json.load(f)
            titulo = get_by_path(data, args.campo)
        except (json.JSONDecodeError, OSError):
            titulo = None

    print(slugify(titulo, args.fallback))


if __name__ == "__main__":
    main()
