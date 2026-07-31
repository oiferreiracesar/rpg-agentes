import json
import math
import os
import sys

CANVAS_W = 680
MARGIN = 40


def size_for_area(area, max_connections):
    n_conn = len(area.get("conexoes", []))
    scale = 0.4 + 0.6 * (n_conn / max(max_connections, 1))
    w = int(130 + 140 * scale)
    h = int(90 + 90 * scale)
    return w, h


def layout_layer(areas, y_offset):
    """Posiciona as áreas de uma camada: a mais conectada vira hub central
    maior; as demais ficam distribuídas abaixo dela, quebrando linha quando
    necessário. Devolve as posições e o próximo y_offset livre."""
    if not areas:
        return {}, y_offset

    max_conn = max(len(a.get("conexoes", [])) for a in areas) or 1
    sorted_areas = sorted(areas, key=lambda a: -len(a.get("conexoes", [])))
    positions = {}

    hub = sorted_areas[0]
    others = sorted_areas[1:]
    hub_w, hub_h = size_for_area(hub, max_conn)
    hub_x = CANVAS_W // 2 - hub_w // 2
    hub_y = y_offset + 30
    positions[hub["nome"]] = {"x": hub_x, "y": hub_y, "w": hub_w, "h": hub_h}

    cur_x = MARGIN
    cur_y = hub_y + hub_h + 50
    row_h = 0
    max_x = CANVAS_W - MARGIN

    for a in others:
        w, h = size_for_area(a, max_conn)
        if cur_x + w > max_x and cur_x > MARGIN:
            cur_x = MARGIN
            cur_y += row_h + 30
            row_h = 0
        positions[a["nome"]] = {"x": cur_x, "y": cur_y, "w": w, "h": h}
        cur_x += w + 30
        row_h = max(row_h, h)

    max_bottom = max(p["y"] + p["h"] for p in positions.values())
    return positions, max_bottom + 30


def box_svg(pos, nome, descricao, fill, stroke, text_color):
    x, y, w, h = pos["x"], pos["y"], pos["w"], pos["h"]
    lines = []
    lines.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )
    lines.append(
        f'<rect x="{x+4}" y="{y+4}" width="{w-8}" height="{h-8}" rx="6" '
        f'fill="none" stroke="{stroke}" stroke-width="1" stroke-dasharray="4 3"/>'
    )
    cx, cy = x + w // 2, y + h // 2
    font_size = 15 if w >= 200 else 13
    label = nome if len(nome) < 22 else nome[:20] + "…"
    lines.append(
        f'<text x="{cx}" y="{cy}" text-anchor="middle" fill="{text_color}" '
        f'font-size="{font_size}">{escape_xml(label)}</text>'
    )
    return "\n".join(lines)


def door_svg(pos_a, pos_b, stroke):
    ax, ay = pos_a["x"] + pos_a["w"] // 2, pos_a["y"] + pos_a["h"] // 2
    bx, by = pos_b["x"] + pos_b["w"] // 2, pos_b["y"] + pos_b["h"] // 2

    def edge_point(src, dst):
        sx, sy, sw, sh = src["x"], src["y"], src["w"], src["h"]
        scx, scy = sx + sw / 2, sy + sh / 2
        dcx, dcy = dst["x"] + dst["w"] / 2, dst["y"] + dst["h"] / 2
        dx, dy = dcx - scx, dcy - scy
        if dx == 0 and dy == 0:
            return scx, scy
        if abs(dx) * sh > abs(dy) * sw:
            ex = scx + (sw / 2 if dx > 0 else -sw / 2)
            ey = scy + dy * (sw / 2) / abs(dx) if dx != 0 else scy
        else:
            ey = scy + (sh / 2 if dy > 0 else -sh / 2)
            ex = scx + dx * (sh / 2) / abs(dy) if dy != 0 else scx
        return ex, ey

    p1 = edge_point(pos_a, pos_b)
    p2 = edge_point(pos_b, pos_a)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy) or 1
    perp_x, perp_y = -dy / length * 8, dx / length * 8

    lines = [f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" stroke="{stroke}" stroke-width="1.5"/>']
    for t in (-6, 6):
        ox, oy = dx / length * t, dy / length * t
        lines.append(
            f'<line x1="{mx+ox-perp_x:.0f}" y1="{my+oy-perp_y:.0f}" '
            f'x2="{mx+ox+perp_x:.0f}" y2="{my+oy+perp_y:.0f}" stroke="{stroke}" stroke-width="2"/>'
        )
    return "\n".join(lines)


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def gerar_svg(mapa, paleta):
    pf = mapa.get("planta_funcional", {})
    camadas = pf.get("camadas", ["Térreo"])
    areas = pf.get("areas", [])

    fill = (paleta.get("primaria") or ["#1a1a1a"])[0]
    stroke = (paleta.get("secundaria") or paleta.get("acento") or ["#c79a4b"])[0]
    text_color = (paleta.get("acento") or ["#e8dcc0"])[0]

    all_boxes = []
    all_doors = []
    y_offset = 10
    layer_labels = []

    for camada_nome in camadas:
        areas_da_camada = [a for a in areas if a.get("camada") == camada_nome] or (
            areas if len(camadas) == 1 else []
        )
        if not areas_da_camada:
            continue
        layer_labels.append((camada_nome, y_offset))
        positions, y_offset = layout_layer(areas_da_camada, y_offset + 20)

        for a in areas_da_camada:
            pos = positions.get(a["nome"])
            if pos:
                all_boxes.append(box_svg(pos, a["nome"], a.get("descricao", ""), fill, stroke, text_color))
        for a in areas_da_camada:
            pos_a = positions.get(a["nome"])
            if not pos_a:
                continue
            for conexao in a.get("conexoes", []):
                pos_b = positions.get(conexao)
                if pos_b and conexao > a["nome"]:
                    all_doors.append(door_svg(pos_a, pos_b, stroke))
                elif pos_b and conexao <= a["nome"]:
                    pass  # evita desenhar a porta duas vezes (A->B e B->A)

    total_h = y_offset + 20

    svg_parts = [
        f'<svg viewBox="0 0 {CANVAS_W} {total_h}" xmlns="http://www.w3.org/2000/svg">',
        f"<title>Planta: {escape_xml(mapa.get('nome_local',''))}</title>",
        f"<desc>Planta gerada algoritmicamente a partir das conexões reais do mapa.</desc>",
    ]
    for nome_camada, y in layer_labels:
        svg_parts.append(
            f'<text x="{MARGIN}" y="{y+15}" fill="{stroke}" font-size="14" '
            f'font-weight="bold">Camada: {escape_xml(nome_camada)}</text>'
        )
    svg_parts.extend(all_doors)
    svg_parts.extend(all_boxes)
    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    cartografo_path = "output/04-cartografo.json"
    direcao_path = "output/02-direcao-arte.json"
    if not os.path.exists(cartografo_path):
        print("ERRO: output/04-cartografo.json não encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(cartografo_path, encoding="utf-8") as f:
        cartografo = json.load(f)

    paleta = {}
    if os.path.exists(direcao_path):
        with open(direcao_path, encoding="utf-8") as f:
            direcao = json.load(f)
        paleta = direcao.get("paleta_cores", {})

    os.makedirs("output/plantas", exist_ok=True)

    for mapa in cartografo.get("mapas", []):
        svg = gerar_svg(mapa, paleta)
        mapa["planta_svg"] = svg
        svg_path = os.path.join("output", "plantas", f"{mapa['local_ref']}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Planta gerada: {svg_path}")

    with open(cartografo_path, "w", encoding="utf-8") as f:
        json.dump(cartografo, f, ensure_ascii=False, indent=2)

    print("Plantas SVG inseridas de volta em output/04-cartografo.json.")


if __name__ == "__main__":
    main()
