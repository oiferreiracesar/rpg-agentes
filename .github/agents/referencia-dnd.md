# Referência de Universo — Dungeons & Dragons / Fantasia Clássica (para uso com SWADE)

Use isto como camada TEMÁTICA sobre o referencia-swade.md — a mecânica nunca
muda, só o nome e a narrativa de cada elemento. Nunca invente mecânica nova
aqui; sempre aponte pra fórmula/regra já definida em referencia-swade.md.

Este documento cobre o gênero como um todo, em nível de arquétipo e conceito
— nunca reproduza diálogo, texto ou trecho exato de nenhuma campanha, módulo
ou cenário publicado específico. Trabalhe sempre com nomes, papéis e temas
gerais de fantasia medieval clássica.

> **Por que este documento existe:** pedir só "fantasia medieval" como gênero
> tende a gerar drama de corte, intriga política ou horror religioso — sem
> nenhum monstro ou raça não-humana envolvida. Esta referência existe
> especificamente pra garantir o oposto: aventura, exploração de masmorra, e
> combate real contra criaturas e povos não-humanos, no estilo consagrado por
> Dungeons & Dragons.

## Sobre o campo "Cenário de Referência"
Diferente de Zelda/Final Fantasy (que têm jogos específicos), D&D tem
CENÁRIOS DE CAMPANHA como âncora de tom. Use a tabela abaixo. Elementos
atemporais (masmorras, guildas de aventureiros, dragões, mortos-vivos) valem
independente do cenário escolhido.

| Cenário de referência | Tom/Tecnologia | Notas de ambientação |
|---|---|---|
| Forgotten Realms / genérico | Clássico, "high fantasy" padrão | O cenário mais abrangente e neutro — reinos humanos, florestas élficas, montanhas anãs, sem torção temática forte |
| Eberron | Noir de guerra recente, magia como tecnologia | Trens e faróis mágicos, detetives, corporações, moralmente mais cinzento que o padrão |
| Dragonlance | Épico, guerra entre ordens divinas | Dragões como força central do conflito, era de heróis lendários, bem e mal mais definidos |
| Dark Sun | Deserto pós-apocalíptico, escassez extrema | Água e metal são recursos preciosos, magia arcana é vista com temor, sobrevivência acima de heroísmo |
| Ravenloft | Terror gótico | Névoa constante, vilões amaldiçoados e trágicos, isolamento, tom mais sombrio e lento que o padrão |
| Greyhawk | Clássico tradicional, sandbox | Cenário "original" do gênero, ênfase em exploração livre e facções locais |
| Sem preferência específica | — | Use o "consenso geral" do gênero (ver DNA temático abaixo), sem puxar pra nenhum cenário em particular |

> Nota de confiança: conhecimento sólido do conceito geral de cada cenário
> (tom, ameaças típicas, estética). Menos profundidade em lore específica de
> módulos, romances ou campanhas publicadas de cada um — trate como ponto de
> partida temático, nunca reproduza enredo específico de nenhum.

## Sobre o campo "Momento Temporal"
Menos crítico aqui do que em universos com uma linha do tempo fixa (tipo
Zelda) — D&D não tem "eventos centrais" canônicos que a aventura precise
evitar contradizer. Pode tratar como "sem preferência" na maioria dos casos,
ou usar livremente pra indicar o estágio de uma ameaça regional (ex: "antes"
= o bando de monstros ainda não tomou a região; "durante" = já tomou e a
aventura é a retomada; "depois" = a ameaça foi derrotada e a aventura lida
com as consequências).

## Povos jogáveis (mapeamento oficial — SEMPRE use estes nomes)

| Raça mecânica (SWADE) | Nome do povo em D&D | Nota de sabor |
|---|---|---|
| Humano | Humano | Povo mais numeroso e adaptável, presente em toda região |
| Elfo | Elfo | Vida longa, afinidade natural com magia e floresta |
| Meio-Elfo | Meio-Elfo | Descendência mista humano-élfica, comum em regiões fronteiriças |
| Pequenino | Halfling | Pequeno, ágil, sortudo — comunidades pacíficas e itinerantes |
| Aquariano | Tritão | Povo do fundo do mar, guardião de costas e recifes |
| Aviano | Aarakocra | Povo alado de penhascos e picos altos |
| Rakashano | Tabaxi | Exploradores felinos nômades, movidos por curiosidade e instinto |
| Sáurio | Draconato | Sangue dracônico, escamas resistentes, honra como código de vida |
| Androide | Warforged | Constructo vivo forjado pra guerra, sem infância nem família biológica |

**Anão e Meio-Orc** — extremamente comuns em D&D, mas nenhum dos 9 traços
mecânicos do referencia-swade.md encaixa bem com o arquétipo deles (robusto e
sem penalidade não é o mesmo que qualquer um dos 9). Trate ambos como
mecanicamente **Humano** (raça = "Humano" na ficha, sem traço racial extra) —
a diferença entre Anão, Meio-Orc e Humano fica inteiramente na descrição
física, `diretriz_interpretacao` e `prompt_imagem`, nunca na mecânica. Isso
já é a convenção usada nas fichas reais desta mesa.

## Criaturas e monstros (mapeamento — SEMPRE escolha uma destas 9 raças)
Diferente de povos jogáveis, monstros/criaturas hostis quase nunca têm forma
humanoide civilizada — mas o schema do referencia-swade.md exige uma das 9
raças oficiais mesmo assim (nunca deixe em branco, nunca invente uma décima).
Escolha pela SILHUETA e pelo TRAÇO MECÂNICO mais parecido, não pelo nome:

> ⚠️ **"Humano" nunca é o padrão de segurança pra criatura não-humana.** Se o
> `nome_exibicao`, a `descricao_curta` ou o `papel` de um NPC diz "orc",
> "goblin", "morto-vivo" ou qualquer criatura da tabela abaixo, a `raca`
> DEVE ser a mapeada — nunca "Humano". Um NPC chamado "Sentinela Orc" ou
> "Chefe Grom, o orc" com `raca: "Humano"` é uma contradição direta entre
> nome e ficha, e anula o propósito inteiro desta referência.

| Tipo de criatura | Raça mecânica mais próxima | Por quê |
|---|---|---|
| Goblin, Kobold, criatura pequena e numerosa | Pequenino | Pequeno, ágil, aparece em grupo |
| Orc raso, hobgoblin, bugbear (capanga genérico, não um chefe nomeado) | Rakashano | Força bruta, mordida/garra natural já embutida no traço |
| **Orc, goblin ou hobgoblin CHEFE/NOMEADO (chefe de cena)** | **A mesma raça do capanga da mesma espécie** (ex: chefe orc também é Rakashano) | O chefe é mecanicamente mais forte (atributos maiores, Carta Selvagem), nunca de espécie/raça diferente dos próprios capangas que lidera |
| Lobo, urso, criatura selvagem grande | Rakashano | Mesma lógica — ataque natural e agressividade |
| Esqueleto, zumbi, morto-vivo em geral | Androide | Reaproveita o traço "Construto" (não respira, imune a veneno/doença, ignora 1 nível de Ferimento) — encaixe mecânico natural pra um corpo sem vida própria |
| Aranha gigante, criatura com casca ou pele grossa | Sáurio | Armadura +2 natural e mordida já embutidas |
| Troll, ogro, gigante menor | Sáurio | Pele resistente, força implacável |
| Dragão (sempre chefe de cena raro e épico, nunca capanga) | Sáurio | Armadura +2 natural, mordida, e a "Fraqueza Ambiental" pode virar a fraqueza elemental clássica do tipo de dragão escolhido (ex: dragão de gelo teme fogo) |
| Elemental, fantasma, espírito sem corpo físico | Androide | Reaproveita "Construto" pra representar "não é feito de carne", mesmo sem ser literalmente mecânico |

Se a mesa quiser uma criatura que não se encaixa em nenhuma linha acima,
escolha a raça cujo TRAÇO mecânico (não o nome) melhor representa a
capacidade dela em combate, e documente a escolha na descrição do NPC.

## Instrução obrigatória: combate real contra monstros e outras raças
Esta é a regra mais importante desta referência, porque é o motivo dela
existir. Toda aventura gerada neste universo PRECISA incluir:
- **Pelo menos 2 cenas com uma dificuldade EXPLICITAMENTE testada com a
  perícia Lutar ou Atirar** (campo "pericia" da dificuldade tem que ser
  literalmente "Lutar" ou "Atirar"), contra criaturas não-humanas. Não
  basta a cena TER um NPC combatente presente — a dificuldade de combate
  real precisa estar escrita no campo "dificuldades" daquela cena. Ter
  Furtividade pra evitar a briga, ou Persuadir pra negociar em vez de
  lutar, NÃO conta pra esse mínimo, mesmo que o mesmo NPC apareça na cena.
  Nuance moral (ver "Arquétipos de antagonista" abaixo) muda o MOTIVO do
  combate, nunca substitui ele — dê ao grupo a opção narrativa de negociar
  SE quiser, mas a cena ainda precisa ter combate testável de verdade pra
  quem preferir resolver assim.
- **Pelo menos UM povo/raça não-humana como força antagonista organizada**
  (um bando de orcs, uma tribo de goblins, um culto de mortos-vivos) — não
  apenas um monstro solitário.
- **Opcionalmente, uma criatura de bestiário genuína** (não-humanoide: aranha
  gigante, morto-vivo, criatura elemental) em pelo menos uma cena, pra
  reforçar que a ameaça não é só "humanos disfarçados de monstros".
- Todo NPC combatente — incluindo capangas genéricos de monstro/raça — precisa
  de ficha própria, seguindo a regra já existente do referencia-swade.md
  (nunca referencie uma dificuldade de combate sem NPC correspondente).
- **Grupos de inimigos idênticos** (2-3 goblins, um bando de orcs) são muito
  mais comuns aqui do que em outros universos deste projeto — quando quiser
  vários inimigos do mesmo tipo numa cena, liste o id UMA ÚNICA VEZ em
  "npcs_presentes" (ex: só "batedor_goblin", nunca "batedor_goblin_1" +
  "batedor_goblin_2" como entradas separadas) e deixe explícito no campo
  "papel" da ficha que o mestre pode reaproveitá-la pra quantas cópias
  quiser em combate. Uma ficha, várias cópias na mesa — nunca uma ficha por
  cópia.
- Isso não impede nuance moral (um antagonista não-humano pode ter motivo
  compreensível, ver "Arquétipos de antagonista" abaixo) — só impede que a
  aventura vire inteiramente social/investigativa/furtiva sem nenhum
  confronto físico testável contra algo além de humanos.

## Locais recorrentes
Uma masmorra ou ruína antiga (caverna, torre desmoronada, fortaleza tomada —
o "Bloco 4" natural), uma vila ou posto fronteiriço ameaçado (Vila de Apoio),
uma guilda de aventureiros ou taverna que despacha contratos (Convocação),
uma floresta, pântano ou passagem de montanha perigosa entre a vila e a
masmorra (Travessia), o covil/trono do antagonista central no fundo da
masmorra (Clímax).

## Artefatos e papéis narrativos recorrentes
- **Arma ou armadura lendária**: item que só o dono legítimo empunha bem, ou
  que carrega uma maldição/preço junto do poder — reimaginação livre de
  qualquer arma icônica de fantasia
- **Artefato selado**: objeto ou local que mantém uma ameaça maior contida,
  bom gancho pra um antagonista que "protege" algo terrível sem ser
  puramente vilão
- **Mapa ou pergaminho de masmorra**: gancho de Documentos clássico, aponta
  o caminho ou revela um segredo da ruína
- **Tesouro com história**: recompensa material que também carrega lore —
  nunca só "número de moedas", sempre um objeto com nome e passado

## Arquétipos de antagonista
Nem todo antagonista precisa ser puramente maligno — um bando de orcs
refugiados de uma ameaça pior, um dragão defendendo o próprio ninho, um culto
de mortos-vivos tentando reverter uma tragédia pessoal, todos são mais
interessantes que "mal porque sim". Dito isso, DIFERENTE de universos mais
sociais/investigativos deste projeto, aqui é totalmente aceitável (e
esperado) que parte da resolução envolva combate direto mesmo quando o
antagonista tem motivo compreensível — a nuance mora na justificativa, não
na ausência de luta.

## DNA temático (arquétipos e motivos recorrentes)
Aventura como jornada física: partir de um ponto seguro, atravessar perigo
real, chegar a um local hostil, enfrentar algo mais forte que qualquer
desafio anterior. Grupo heterogêneo de aventureiros (várias raças, várias
classes/papéis de combate) unidos por contrato ou causa comum. Tesouro e
progressão material importam tanto quanto a resolução narrativa — sempre dê
um gancho de recompensa tangível, não só resolução emocional. Tom: heroico e
aventureiro por padrão, com espaço pra momentos sombrios ou mais táticos,
mas sem o peso constantemente cinzento de universos como Ordem Paranormal.

## Referência estrutural obrigatória
Siga a mesma estrutura de 6 blocos de referencia-hyrule.md, com estas
adaptações:
- **Bloco 0 (Introdução):** notícia ou boato sobre a ameaça (queda de uma
  fortaleza, avanço de um bando, desaparecimento de uma vila) chegando até
  uma guilda de aventureiros ou autoridade local — nunca uma cena jogável,
  só prosa de contexto
- **Bloco 1 (Convocação):** briefing formal — uma guilda, um nobre local, ou
  um conselho de vila explica a missão e entrega o contrato/gancho físico
- **Bloco 2 (Vila de Apoio):** posto fronteiriço ou vila próxima da ameaça,
  onde um NPC guia/informante oferece orientação — bom lugar pra revelar
  pistas sobre a raça/criatura antagonista antes do confronto direto
- **Bloco 3 (Travessia):** trecho de perigo natural (floresta, pântano,
  passagem de montanha) com uma emboscada de capangas não-humanos comuns
  (nunca Carta Selvagem aqui) — este é o primeiro combate real da aventura,
  não pule ele
- **Bloco 4 (Dungeon):** a masmorra/ruína/covil propriamente dita, com as
  mesmas 4-5 partes internas do padrão Hyrule (vestíbulo, 2 puzzles/desafios
  temáticos, mini-prova de combate contra um segundo grupo de capangas
  não-humanos, câmara final) — pelo menos UM desses desafios internos deve
  ser combate direto contra a raça/criatura antagonista, não só puzzle
- **Bloco 5 (Clímax):** confronto final com o antagonista central (chefe de
  cena, sempre Carta Selvagem) — pode ser resolvido por combate, negociação,
  ou uma mistura dos dois, mas a OPÇÃO de resolver via combate real precisa
  estar mecanicamente presente (ficha de combate completa do antagonista),
  mesmo que a mesa prefira negociar
