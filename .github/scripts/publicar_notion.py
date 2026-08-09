import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

NOTION_VERSION = "2022-06-28"

def extract_page_id(raw):
    """Aceita um ID puro, um ID com hífens, ou a URL completa da página do
    Notion, e sempre devolve o ID no formato UUID com hífens que a API espera."""
    raw = raw.strip()
    match = re.search(
        r"([0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?"
        r"[0-9a-fA-F]{4}-?[0-9a-fA-F]{12})(?:[?#].*)?$",
        raw,
    )
    if not match:
        print(
            f"ERRO: não foi possível extrair um ID válido de NOTION_PARENT_PAGE_ID: {raw}",
            file=sys.stderr,
        )
        sys.exit(1)
    hexid = match.group(1).replace("-", "")
    return f"{hexid[0:8]}-{hexid[8:12]}-{hexid[12:16]}-{hexid[16:20]}-{hexid[20:32]}"

def notion_request(token, method, path, body=None):
    url = f"https://api.notion.com/v1{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERRO Notion API {e.code}: {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def rich_text(text):
    parts = []
    pattern = re.compile(r"\*\*(.+?)\*\*")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            parts.append({"type": "text", "text": {"content": text[pos:m.start()]}})
        parts.append(
            {
                "type": "text",
                "text": {"content": m.group(1)},
                "annotations": {"bold": True},
            }
        )
        pos = m.end()
    if pos < len(text):
        parts.append({"type": "text", "text": {"content": text[pos:]}})
    if not parts:
        parts = [{"type": "text", "text": {"content": text or " "}}]
    for p in parts:
        if len(p["text"]["content"]) > 1900:
            p["text"]["content"] = p["text"]["content"][:1900] + "…"
    return parts


def paragraph_block(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(text)}}


def heading_block(level, text):
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": rich_text(text)}}


def bullet_block(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text)},
    }


def quote_block(text):
    return {"object": "block", "type": "quote", "quote": {"rich_text": rich_text(text)}}


def code_block(text, language="plain text"):
    valid_langs = {
        "html", "json", "javascript", "python", "markdown", "plain text",
    }
    if language not in valid_langs:
        language = "plain text"
    return {
        "object": "block",
        "type": "code",
        "code": {"rich_text": rich_text(text or " "), "language": language},
    }


def divider_block():
    return {"object": "block", "type": "divider", "divider": {}}


def table_block(rows):
    width = max(len(r) for r in rows)
    table_rows = []
    for r in rows:
        cells = r + [""] * (width - len(r))
        table_rows.append(
            {
                "object": "block",
                "type": "table_row",
                "table_row": {"cells": [rich_text(c) for c in cells[:width]]},
            }
        )
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": True,
            "has_row_header": False,
            "children": table_rows,
        },
    }


def markdown_to_blocks(md_text):
    lines = md_text.split("\n")
    blocks = []
    i = 0
    in_code = False
    code_lines = []
    code_lang = "plain text"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = stripped[3:].strip() or "plain text"
                code_lines = []
            else:
                in_code = False
                blocks.append(code_block("\n".join(code_lines), code_lang))
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            level = max(1, min(level, 3))
            text = stripped.lstrip("#").strip()
            if text:
                blocks.append(heading_block(level, text))
            i += 1
            continue

        if stripped == "---":
            blocks.append(divider_block())
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = []
            for tl in table_lines:
                if re.match(r"^\|[\s:\-|]+\|$", tl):
                    continue
                cells = [c.strip() for c in tl.strip("|").split("|")]
                rows.append(cells)
            if rows:
                blocks.append(table_block(rows))
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append(bullet_block(stripped[2:].strip()))
            i += 1
            continue

        if stripped.startswith(">"):
            blocks.append(quote_block(stripped.lstrip(">").strip()))
            i += 1
            continue

        blocks.append(paragraph_block(stripped))
        i += 1

    return blocks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pasta", default="output", help="Pasta onde estão os JSONs/markdown (padrão: output)")
    args = parser.parse_args()

    token = os.environ.get("NOTION_TOKEN")
    parent_id_raw = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not token or not parent_id_raw:
        print("ERRO: NOTION_TOKEN e/ou NOTION_PARENT_PAGE_ID não definidos.", file=sys.stderr)
        sys.exit(1)
    parent_id = extract_page_id(parent_id_raw)

    md_path = os.path.join(args.pasta, "07-compilado.md")
    if not os.path.exists(md_path):
        print(f"ERRO: {md_path} não encontrado.", file=sys.stderr)
        sys.exit(1)
    with open(md_path, encoding="utf-8") as f:
        md_content = f.read()

    roteirista_path = os.path.join(args.pasta, "01-roteirista.json")
    titulo = "Oneshot Gerada"
    if os.path.exists(roteirista_path):
        with open(roteirista_path, encoding="utf-8") as f:
            roteirista = json.load(f)
        titulo = roteirista.get("metadados", {}).get("titulo", titulo)

    blocks = markdown_to_blocks(md_content)
    if not blocks:
        print("ERRO: nenhum bloco foi extraído do markdown.", file=sys.stderr)
        sys.exit(1)

    first_batch = blocks[:100]
    rest = blocks[100:]

    page = notion_request(
        token,
        "POST",
        "/pages",
        {
            "parent": {"page_id": parent_id},
            "properties": {"title": {"title": [{"text": {"content": titulo}}]}},
            "children": first_batch,
        },
    )
    page_id = page["id"]
    print(f"Página criada: {page.get('url')}")

    while rest:
        batch = rest[:100]
        rest = rest[100:]
        notion_request(token, "PATCH", f"/blocks/{page_id}/children", {"children": batch})
        print(f"Lote de {len(batch)} blocos adicionado.")
        time.sleep(0.4)

    print("Publicação no Notion concluída.")


if __name__ == "__main__":
    main()
