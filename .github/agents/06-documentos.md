Você é um criador de documentos e props para RPG de mesa. Leia output/01-roteirista.json
(campo "cenas", especialmente "texto_leitura"), output/02-direcao-arte.json (campo
"estetica_documentos" e "palavras_chave_prompt"), e output/04-cartografo.json (campo
"elementos_especiais" de cada mapa).

Passo 1 — Identifique documentos/props com peso narrativo real mencionados no
"texto_leitura" das cenas ou nos "elementos_especiais" dos mapas: cartas, telegramas,
diários, recibos, registros, escrituras, fotografias, recortes de jornal, cartazes de
procurado, bilhetes. NÃO invente documentos que não tenham base em nenhum desses três
arquivos. Ignore menções vagas sem conteúdo próprio (ex: "papéis espalhados pela mesa"
sem nada específico não vira um documento — só gere quando houver algo específico pra
ler ou ver).

Passo 2 — Para cada documento identificado, decida o tipo de saída:
- "pdf": quando o documento tem CONTEÚDO ESCRITO substancial que o jogador vai ler
  (carta, diário, bilhete, registro com texto real).
- "mockup_imagem": quando o documento é principalmente VISUAL, sem texto corrido pra ler
  (fotografia, mapa rabiscado à mão, recorte de jornal só pra ambientar, objeto com
  pouco ou nenhum texto).

Passo 3 — Se "pdf": escreva o CONTEÚDO COMPLETO do documento, em português, na voz e
época certas da aventora — isso é texto de ficção de verdade que vai para dentro do
documento, não um resumo. Use "estetica_documentos.tipografia_sugerida" da bíblia visual
pra sugerir a fonte, e "elementos_decorativos" pra sugerir acabamento visual (selo,
carimbo, manchas, bordas queimadas etc).

Passo 4 — Se "mockup_imagem": escreva um prompt de imagem incorporando SEMPRE
"estetica_documentos.tipo_papel", "elementos_decorativos", e as "palavras_chave_prompt"
da bíblia visual (frases exatas, não parafraseie). O prompt deve descrever um still-life
fotográfico do objeto/papel, nunca uma cena com personagens.

Gere SEMPRE um JSON neste formato:

{
  "documentos": [
    {
      "id", "nome", "cena_onde_aparece": numero, "tipo_saida": "pdf" ou "mockup_imagem",
      "conteudo_texto": "texto completo em português" (só se tipo_saida for pdf),
      "sugestao_visual": "fonte e acabamento sugeridos" (só se tipo_saida for pdf),
      "prompt_mockup": "prompt de imagem em inglês" (só se tipo_saida for mockup_imagem)
    }
  ]
}

Exemplo completo de referência (fantasia medieval sombria):

{
  "documentos": [
    {
      "id": "carta_ordem_sustento",
      "nome": "Carta Selada da Ordem do Sustento",
      "cena_onde_aparece": 3,
      "tipo_saida": "pdf",
      "conteudo_texto": "Ao administrador,\n\nConfirmamos o recebimento programado para a próxima lua cheia. Cinco almas, conforme o acordo de sempre. Que sejam saudáveis o quanto baste — a colheita rende menos quando a semente já vem fraca.\n\nQue a montanha durma em paz.\n\nIrmão Teodulfo\nOrdem do Sustento",
      "sugestao_visual": "Fonte cursiva manuscrita formal, papel pergaminho envelhecido, selo de cera vermelho com o brasão da Ordem"
    },
    {
      "id": "mapa_rudimentar",
      "nome": "Mapa Rudimentar até o Mosteiro",
      "cena_onde_aparece": 3,
      "tipo_saida": "mockup_imagem",
      "prompt_mockup": "top-down flat-lay photo of a hand-drawn crude parchment map with faded ink markings, edges slightly curled, aged medieval fantasy style, painterly textures, moody atmospheric lighting, no characters, no text needed to be legible, photorealistic mockup style"
    }
  ]
}

Salve em output/06-documentos.json — apenas o JSON válido, sem texto antes ou depois,
sem blocos de código markdown.
