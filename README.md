# Gerador de Oneshots de RPG — Automação via GitHub Actions

Encadeia agentes de IA (Gemini) e scripts determinísticos pra gerar uma oneshot
de RPG completa — roteiro, arte, NPCs, mapas, cutscenes, tabela de improviso,
som, documentos — e publicar tudo automaticamente numa página nova do Notion.

## Como o pipeline funciona hoje

| # | Passo | Motor | O que faz |
|---|---|---|---|
| 1 | Roteirista | Gemini (`gemini-3.5-flash-lite`) | Premissa, cenas, twists, finais (com texto de leitura de cada final) |
| 2 | Direção de Arte | Gemini (`gemini-3.5-flash-lite`) | Paleta de cores, estética, trilha sonora de referência |
| 3 | NPCs | Gemini (`gemini-3.5-flash-lite`) | Fichas de personagem, stat blocks, Carta Selvagem, armadura |
| 3b | Corrigir Resistência | **Script Python (sem IA)** | Calcula `resistencia` e `aparar` de cada NPC combatente pelas fórmulas oficiais |
| 4 | Cartógrafo | Gemini (`gemini-3.5-flash-lite`) | Decide áreas de cada mapa e como se conectam |
| 4c | Animador de Cutscenes | Gemini (`gemini-3.5-flash-lite`) | Identifica momentos cinematográficos (abertura, finais, cenas dramáticas) e gera prompts prontos pro Google Flow |
| 4d | Tabela de Improviso | Gemini (`gemini-3.5-flash-lite`) | Framework de modificadores, situações comuns de mesa, gatilhos específicos da aventura, e banco de falas por NPC |
| 5 | Sonoplastia | Gemini (`gemini-3.5-flash-lite`) | Sugestões de trilha sonora e efeitos sonoros por cena |
| 6 | Documentos | Gemini (`gemini-3.5-flash-lite`) | Cartas, diários, props — decide PDF ou mockup de imagem |
| — | Validação | **Script Python (sem IA)** | Confere formato, nomes de perícia, tipos de dano, campos obrigatórios, Carta Selvagem, referências cruzadas entre Animador/Improviso e o resto |
| 7a | Compilador — gerar markdown | **Script Python (sem IA)** | Monta o documento final a partir dos JSONs, sem chamar nenhuma IA |
| 7b | Compilador — publicar no Notion | **Script Python (sem IA)** | Cria a página no Notion via API REST direta |

Repara que boa parte do pipeline hoje **não usa IA nenhuma** — só os passos que
realmente exigem julgamento criativo (decidir o quê existe, não onde desenhar
ou como formatar) passam por modelo de linguagem.

> **Nota sobre as plantas dos mapas:** o pipeline não gera mais o desenho SVG
> das plantas automaticamente (o passo "Gerar Plantas" foi removido). O
> Cartógrafo continua decidindo a estrutura de cada mapa (áreas e conexões) —
> as plantas em si são desenhadas manualmente depois, conversando direto com o
> Claude fora do GitHub.

## Configuração (só precisa fazer uma vez)

### 1. Chave de API do Gemini
Vá em https://aistudio.google.com/apikey, gere uma chave.

### 2. Integração do Notion
1. Acesse **notion.so/my-integrations** → "+ New integration" → dê um nome, escolha
   o workspace, copie o "Internal Integration Secret"
2. No Notion, crie (ou escolha) uma página "recipiente" pra guardar as aventuras
   geradas (ex: "📚 Oneshots Geradas")
3. Nessa página, vá em **··· → Conexões → Adicionar conexões**, e conecte a
   integração que você acabou de criar
4. Copie o link dessa página — o ID está nos últimos 32 caracteres da URL

### 3. Cadastrar os segredos no GitHub
No repositório: **Settings → Secrets and variables → Actions → New repository secret**

| Nome | Valor |
|---|---|
| `GEMINI_API_KEY` | Chave do passo 1 |
| `NOTION_TOKEN` | Chave do passo 2 |
| `NOTION_PARENT_PAGE_ID` | ID da página do passo 2 (só o código, sem a URL na frente — o script tolera se você colar a URL inteira por engano, mas o ideal é só o ID) |

## Como gerar uma aventura nova

1. Vá na aba **Actions** do repositório
2. Clique em **Gerar Oneshot de RPG** → **Run workflow**
3. Descreva a aventura que você quer (gênero, tom, gancho, duração, número de cenas)
4. Espera terminar (leva alguns minutos)
5. Quando concluir:
   - Baixa o artefato `oneshot-gerada` (todos os JSONs + o markdown compilado)
   - Abre a página "📚 Oneshots Geradas" no Notion — a aventura nova já está lá
     dentro, publicada automaticamente, incluindo as seções de Cutscenes e
     Tabela de Improviso
6. Adiciona um bloco de Sumário na página manualmente (`/sumário` no Notion) —
   isso não é automatizado, é rápido de fazer na mão e mais confiável

## Estrutura do repositório

.github/
- agents/ — Instruções de cada agente de IA
  - 01-roteirista.md
  - 02-direcao-arte.md
  - 03-npcs.md
  - 04-cartografo.md
  - 05-sonoplastia.md
  - 06-documentos.md
  - 07-compilador.md — referência histórica; a lógica real do Compilador hoje está no script Python
  - 08-animador.md — cutscenes cinematográficas (prompts pro Google Flow)
  - 09-improviso.md — tabela de improviso e banco de falas
  - referencia-swade.md — perícias, fórmulas de Aparar/Resistência, dano de armas, Carta Selvagem
- scripts/ — Passos determinísticos, sem IA
  - corrigir_resistencia.py — calcula Aparar e Resistência
  - validar_json.py
  - compilador_gerar.py
  - publicar_notion.py
  - gerar_plantas.py — não é mais chamado pelo workflow (ver nota acima); mantido no repositório caso queira voltar a usar no futuro
- workflows/
  - gerar-oneshot.yml

## Cota gratuita — o que já aprendemos na prática

- A cota da API do Gemini é **por modelo, por projeto**, não por agente — todos os
  agentes que usam o mesmo modelo competem pela mesma cota diária.
- `gemini-3.5-flash-lite` teve cota observada variando bastante ao longo do
  desenvolvimento (de 20 a centenas por dia) — confira o número atual em
  **ai.dev/rate-limit** antes de assumir um valor fixo.
- A assinatura paga do app do Gemini (Gemini Pro/Advanced) **não** aumenta a cota
  da API — são produtos completamente separados.

## Se algo der errado

Todo passo imprime mensagens de erro claras no log da execução (aba Actions →
clica na execução → clica no passo que falhou). Os erros mais comuns já mapeados:

- **Cota excedida (429)**: espera resetar (geralmente meia-noite horário do
  Pacífico) ou troca o modelo do agente específico que falhou
- **JSON inválido entre passos**: o passo de Validação deve pegar isso antes de
  chegar no Compilador — confere o relatório dele primeiro
- **NPC sem Carta Selvagem, Aparar ou Resistência ausentes**: o Validador avisa
  ou bloqueia — geralmente sinal de que o "3b. Corrigir Resistência" não rodou
  antes desse NPC, ou o agente de NPCs esqueceu o campo
- **Cutscene ou banco de falas referenciando cena/NPC que não existe**: o
  Validador avisa (não bloqueia) — geralmente sinal de que o Animador ou o
  Improviso interpretaram um ID errado
- **Erro 400 do Notion sobre `page_id`**: confere se `NOTION_PARENT_PAGE_ID` tem
  só o ID, não a URL inteira (o script tenta extrair sozinho, mas vale conferir)
