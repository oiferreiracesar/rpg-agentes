# Estado do Projeto — Gerador de Oneshots/Campanhas de RPG (SWADE)

> Documento de handoff. Se você está lendo isso numa conversa nova, cole
> esse documento inteiro no início pra recuperar o contexto do projeto sem
> precisar reconstruir tudo do zero.

## O que é o projeto

Pipeline automatizado (GitHub Actions + Gemini) que gera aventuras
completas de RPG de mesa no sistema **SWADE** — roteiro, NPCs, mapas,
cutscenes, trilha sonora, documentos/props, puzzles físicos impressos, e
publica tudo automaticamente numa página do Notion. Suporta oneshot
(sessão única) e campanha (múltiplas sessões com continuidade real de
NPC/enredo entre elas).

Repositório: `rpg-agentes` (nome real do repo do usuário, confirmar).

---

## Arquitetura — visão geral

```
.github/
  agents/
    referencia-swade.md          — base mecânica: raças, perícias, fórmulas
    00-campanha.md                — Arquiteto de Campanha (só workflow de campanha)
    01-roteirista.md              — gera premissa, cenas, twists, finais
    02-direcao-arte.md            — paleta visual, estética
    03-npcs.md                    — fichas de NPC (raça, atributos, combate)
    04-cartografo.md              — estrutura de mapas (áreas, conexões)
    05-sonoplastia.md             — trilha sonora e efeitos por cena
    06-documentos.md               — cartas, diários, props
    07-compilador.md              — HISTÓRICO, não usado pelo workflow real
    08-animador.md                — cutscenes cinematográficas (prompts Flow)
    09-improviso.md               — tabela de improviso, banco de falas, loot ambiental
    10-puzzles.md                 — 19 tipos de dinâmica física (puzzles impressos)
    referencia-hyrule.md
    referencia-finalfantasy.md
    referencia-scifi-nintendo.md  — Metroid + Star Fox
    referencia-pokemon.md         — modo treinador OU mystery_dungeon
    referencia-digimon.md
    referencia-ordemparanormal.md
    referencia-starwars.md
    referencia-naruto.md
    referencia-dc.md
    referencia-marvel-hq.md
    referencia-marvel-cinematico.md
    referencia-silenthill.md
    referencia-residentevil.md
    referencia-slasher.md
    referencia-lanoire.md         — investigação/interrogatório (recém-criado, nunca testado)

  scripts/
    corrigir_resistencia.py       — calcula Aparar/Resistência, normaliza dado→dano,
                                     preenche atributo faltando, aplica modificador racial
    corrigir_raca_pokemon.py      — corrige raça "Humano" indevida em Pokémon (heurística por palavra-chave)
    validar_json.py               — ~12 checagens cruzadas entre todos os JSONs gerados
    compilador_gerar.py           — monta o 07-compilado.md final (sem IA)
    gerar_caca_palavras.py
    gerar_cifra.py                — suporta substituição por símbolo E Cifra de César
    gerar_anagrama.py
    gerar_sequencia_logica.py     — suporta cartas-isca (distratores)
    gerar_palavras_cruzadas.py    — cruzadinha real, com interseção verificada
    gerar_cadeado_numerico.py     — modo estrito (verificado) + modo de segurança (sem verificação, avisa)
    gerar_sudoku_tematico.py      — sudoku 4x4 temático
    gerar_roleta.py               — roleta de decisão pra momentos narrativos grandes
    gerar_indice_campanha.py      — índice mestre de campanha (linka pras sessões)
    gerar_nome_artefato.py        — nome dinâmico do artefato de download (título da aventura)
    publicar_notion.py            — publica markdown no Notion; suporta --parent-id
                                     pra criar subpáginas (usado pra campanha: página-mãe + sessões)
    gerar_plantas.py              — ÓRFÃO, não chamado por nenhum workflow

  workflows/
    gerar-oneshot.yml             — 23 passos, gera 1 aventura
    gerar-campanha.yml            — 66 passos, gera N sessões (até 3) + índice + Notion multi-página
```

### Princípio de design central (aprendido com muita dor)

**Nunca confie que a IA (Gemini) vai seguir um schema exato, mesmo com
exemplo explícito no prompt.** Em praticamente todo universo novo testado,
o Gemini variou nome de campo, estrutura de dado, ou formato de alguma
forma inesperada. A solução que funcionou de verdade, repetidamente: fazer
os **scripts** (não os prompts) tolerantes — busca de campo por padrão
textual (`buscar_campo_lista`, `buscar_campo_texto`), múltiplos formatos
aceitos, modo de segurança com aviso em vez de falha total, normalização
de nomes de campo parecidos (`dado`↔`dano`). Reforçar instrução no prompt
uma terceira vez raramente resolve — mudar o código do script quase
sempre resolve.

---

## O que já foi testado de verdade (com Gemini real) e está confirmado sólido

- **Oneshot, universo `generico`**: múltiplas rodadas, pipeline completo
  incluindo puzzles, sem erro bloqueante nas últimas execuções.
- **Pokémon** (modo treinador): expansão treinador→3 Pokémon, raça
  Espécie→Raça, correção automática de raça "Humano" via
  `corrigir_raca_pokemon.py` — convergiu depois de várias rodadas.
- **Digimon**: expansão Tamer→1 parceiro, `tamer_id`, normalização
  `dado`→`dano` — convergiu.
- **Todos os 8 tipos de puzzle "script_verificavel"**: testados contra
  dado real gerado pelo Gemini em pelo menos 2 universos diferentes cada,
  incluindo casos extremos (cartas-isca, Cifra de César com deslocamento
  embutido em frase, rótulo curto em vez de texto completo).

## O que está pendente — nunca confirmado de ponta a ponta

- **Campanha, publicação multi-página no Notion**: o código existe e foi
  testado isoladamente (conversão markdown→blocos, argumentos do script),
  mas o teste real end-to-end nunca completou — sempre travou antes
  (arquivo desatualizado no repo, permissão da página no Notion, cota da
  API). **Este é o item de maior prioridade pro próximo teste.**
- **L.A. Noire**: universo inteiro (referência + mecânica de interrogatório
  Verdade/Pressionar/Mentira + validação) construído mas **nunca rodou com
  Gemini nem uma vez**. Espere variação de schema na primeira tentativa,
  mesmo padrão de todo universo novo.
- **Universos "sem tabela de raça"** (Naruto, Star Wars, DC, Marvel,
  Silent Hill, Resident Evil, Slasher, Ordem Paranormal): nunca testados
  com Gemini real, só revisados em teoria.
- **`00-indice-campanha.md`**: gerado e testado localmente, mas nunca visto
  num teste end-to-end real com sessões geradas por Gemini de verdade.

---

## Problema recorrente a observar

**Sincronização entre "arquivo confirmado correto nesta conversa" e
"arquivo realmente aplicado no repositório do usuário".** Aconteceu
repetidas vezes: um script era corrigido e confirmado aqui, mas o teste
seguinte revelava que a versão antiga ainda estava rodando no GitHub. Não é
erro de lógica — é só o usuário não ter colado o arquivo atualizado antes
de disparar o próximo teste. Vale sempre confirmar visualmente (ex: "essa
função existe no seu arquivo?") antes de gastar uma rodada de teste.

### Regra permanente, a partir de agora

**Antes de editar qualquer arquivo já existente (agente, script,
referência, workflow), sempre pedir pro usuário mandar o conteúdo atual
real dele primeiro — nunca editar de memória ou a partir de uma cópia
antiga guardada nesta conversa.** Só nesse caso está liberado pular esse
passo: quando o próprio arquivo acabou de ser criado do zero nesta mesma
conversa (nunca existiu antes, então não tem "versão desatualizada" possível).

## Bloqueio atual

Cota diária gratuita da API Gemini (`generativelanguage.googleapis.com`,
modelo `gemini-3.5-flash-lite`, limite 500 requisições/dia) esgotada.
Reseta diariamente (~meia-noite horário do Pacífico dos EUA). Sem solução
do lado do código — só esperar.

## Próximo passo recomendado, assim que a cota voltar

Rodar `gerar-campanha.yml` do zero, universo `generico`, 2 sessões — é o
único caminho que ainda não tem confirmação real de funcionar de ponta a
ponta (a publicação multi-página no Notion).
