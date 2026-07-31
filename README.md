# Gerador de Oneshots de RPG — Automação via GitHub Actions

Encadeia agentes de IA (Gemini + Claude) e scripts determinísticos pra gerar uma
oneshot de RPG completa — roteiro, arte, NPCs, mapas, som, documentos — e publicar
tudo automaticamente numa página nova do Notion.

## Como o pipeline funciona hoje

| # | Passo | Motor | O que faz |
|---|---|---|---|
| 1 | Roteirista | Gemini (`gemini-3.5-flash-lite`) | Premissa, cenas, twists, finais |
| 2 | Direção de Arte | Gemini (`gemini-3.5-flash-lite`) | Paleta de cores, estética, trilha sonora de referência |
| 3 | NPCs | Gemini (`gemini-3.5-flash-lite`) | Fichas de personagem, stat blocks |
| 3b | Corrigir Resistência | **Script Python (sem IA)** | Recalcula `resistencia` de cada NPC combatente a partir da fórmula oficial |
| 4 | Cartógrafo | Gemini (`gemini-3.5-flash-lite`) | Decide áreas de cada mapa e como se conectam |
| 4b | Gerar Plantas | **Script Python (sem IA)** | Desenha o SVG da planta a partir das conexões — layout calculado, não copiado |
| 5 | Sonoplastia | Gemini (`gemini-3.5-flash-lite`) | Sugestões de trilha sonora e efeitos sonoros por cena |
| 6 | Documentos | Gemini (`gemini-3.5-flash-lite`) | Cartas, diários, props — decide PDF ou mockup de imagem |
| — | Validação | **Script Python (sem IA)** | Confere formato, nomes de perícia, tipos de dano, campos obrigatórios |
| 7a | Compilador — gerar markdown | **Script Python (sem IA)** | Monta o documento final a partir dos JSONs, sem chamar nenhuma IA |
| 7b | Compilador — publicar no Notion | **Script Python (sem IA)** | Cria a página no Notion via API REST direta |

Repara que boa parte do pipeline hoje **não usa IA nenhuma** — só os passos que
realmente exigem julgamento criativo (decidir o quê existe, não onde desenhar ou
como formatar) passam por modelo de linguagem.

## Configuração (só precisa fazer uma vez)

### 1. Chave de API do Gemini
Vá em https://aistudio.google.com/apikey, gere uma chave.

### 2. Chave de API da Anthropic (usada pelo Cartógrafo... "papel histórico", ver nota)
Vá em https://console.anthropic.com → API Keys → Create Key.
> Nota: o Cartógrafo hoje roda no Gemini de novo (voltou depois de simplificarmos
> o que ele precisa fazer). A chave da Anthropic fica configurada caso você queira
> usar Claude em algum agente específico no futuro — não é obrigatória pro fluxo
> padrão atual, mas o `ANTHROPIC_API_KEY` precisa existir como segredo se algum
> passo do workflow ainda referenciar `anthropics/claude-code-action`.

### 3. Integração do Notion
1. Acesse **notion.so/my-integrations** → "+ New integration" → dê um nome, escolha
   o workspace, copie o "Internal Integration Secret"
2. No Notion, crie (ou escolha) uma página "recipiente" pra guardar as aventuras
   geradas (ex: "📚 Oneshots Geradas")
3. Nessa página, vá em **··· → Conexões → Adicionar conexões**, e conecte a
   integração que você acabou de criar
4. Copie o link dessa página — o ID está nos últimos 32 caracteres da URL

### 4. Cadastrar os segredos no GitHub
No repositório: **Settings → Secrets and variables → Actions → New repository secret**

| Nome | Valor |
|---|---|
| `GEMINI_API_KEY` | Chave do passo 1 |
| `ANTHROPIC_API_KEY` | Chave do passo 2 (ver nota acima) |
| `NOTION_TOKEN` | Chave do passo 3 |
| `NOTION_PARENT_PAGE_ID` | ID da página do passo 3 (só o código, sem a URL na frente — o script tolera se você colar a URL inteira por engano, mas o ideal é só o ID) |

## Como gerar uma aventura nova

1. Vá na aba **Actions** do repositório
2. Clique em **Gerar Oneshot de RPG** → **Run workflow**
3. Descreva a aventura que você quer (gênero, tom, gancho, duração, número de cenas)
4. Espera terminar (leva alguns minutos)
5. Quando concluir:
   - Baixa o artefato `oneshot-gerada` (todos os JSONs + o markdown + as plantas
     `.svg` separadas, em `output/plantas/`)
   - Abre a página "📚 Oneshots Geradas" no Notion — a aventura nova já está lá
     dentro, publicada automaticamente
6. Adiciona um bloco de Sumário na página manualmente (`/sumário` no Notion) —
   isso não é automatizado, é rápido de fazer na mão e mais confiável

## Estrutura do repositório
.github/
├── agents/ # Instruções de cada agente de IA
│ ├── 01-roteirista.md
│ ├── 02-direcao-arte.md
│ ├── 03-npcs.md
│ ├── 04-cartografo.md
│ ├── 05-sonoplastia.md
│ ├── 06-documentos.md
│ ├── 07-compilador.md # Mantido como referência histórica; a lógica
│ │ real do Compilador hoje está no script Python
│ └── referencia-swade.md # Fórmulas e lista oficial de perícias do sistema
├── scripts/ # Passos determinísticos, sem IA
│ ├── corrigir_resistencia.py
│ ├── gerar_plantas.py
│ ├── validar_json.py
│ ├── compilador_gerar.py
│ └── publicar_notion.py
└── workflows/
└── gerar-oneshot.yml

## Cota gratuita — o que já aprendemos na prática

- A cota da API do Gemini é **por modelo, por projeto**, não por agente — todos os
  agentes que usam o mesmo modelo competem pela mesma cota diária.
- `gemini-3.5-flash-lite` teve cota observada variando bastante ao longo do
  desenvolvimento (de 20 a centenas por dia) — confira o número atual em
  **ai.dev/rate-limit** antes de assumir um valor fixo.
- A assinatura paga do app do Gemini (Gemini Pro/Advanced) **não** aumenta a cota
  da API — são produtos completamente separados.
- A API da Anthropic não tem cota gratuita contínua, só um crédito único de teste
  pra contas novas — depois disso é pago por token.

## Se algo der errado

Todo passo imprime mensagens de erro claras no log da execução (aba Actions →
clica na execução → clica no passo que falhou). Os erros mais comuns já mapeados:

- **Cota excedida (429)**: espera resetar (geralmente meia-noite horário do
  Pacífico) ou troca o modelo do agente específico que falhou
- **JSON inválido entre passos**: o passo de Validação deve pegar isso antes de
  chegar no Compilador — confere o relatório dele primeiro
- **Erro 400 do Notion sobre `page_id`**: confere se `NOTION_PARENT_PAGE_ID` tem
  só o ID, não a URL inteira (o script tenta extrair sozinho, mas vale conferir)
