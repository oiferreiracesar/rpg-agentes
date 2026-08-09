# Referência de Universo — Pokémon (para uso com SWADE)

Use isto como camada TEMÁTICA sobre o referencia-swade.md — a mecânica nunca
muda, só o nome e a narrativa de cada elemento. Nunca invente mecânica nova
aqui; sempre aponte pra fórmula/regra já definida em referencia-swade.md.

Nunca reproduza diálogo, texto ou trecho exato de nenhum jogo/anime
específico — trabalhe sempre com nomes, papéis e temas gerais.

## Atenção — este universo tem arquitetura de personagem própria
Diferente de Zelda/Final Fantasy, o treinador (jogador) NÃO usa a ficha
padrão do referencia-swade.md — ele é minimalista e sem estatística. Toda a
mecânica de combate vive nos 3 Pokémon dele. Leia a seção "Ficha do
Treinador" e "Os 3 Pokémon" abaixo com atenção antes de gerar qualquer
personagem ou NPC neste universo — é obrigatório seguir essa estrutura
sempre que a aventura for de Pokémon.

## Sobre o campo "Região de Referência" (em vez de "jogo", já que o mundo
muda pouco entre jogos da mesma geração)

| Região de referência | Nota de ambientação |
|---|---|
| Kanto | Região fundacional, tom clássico, primeira Liga Pokémon |
| Johto | Tom tradicional/histórico, templos e lendas antigas |
| Hoenn | Foco em natureza, clima extremo, times rivais ligados a terra/mar |
| Sinnoh | Tom mitológico forte, montanha sagrada central, criação do universo |
| Unova | Tom mais urbano/moderno, questão ética sobre libertar Pokémon como tema central |
| Kalos | Estética europeia, tema de beleza/estilo, laboratório de clonagem como ameaça |
| Alola | Tom insular/havaiano, provações em vez de ginásios, guardiões da ilha |
| Galar | Tom britânico industrial, fenômeno de gigantização em estádios |
| Paldea | Mundo aberto, academia como base, três narrativas paralelas |
| Sem preferência específica | Use o "DNA recorrente da franquia" abaixo |

> Nota de confiança: conhecimento sólido em todas as regiões listadas —
> franquia bem documentada e consistente em estrutura entre gerações.

## Sobre o campo "Momento Temporal"
Antes/durante/depois dos eventos centrais da região escolhida. Regra de
segurança: NUNCA faça os personagens encontrarem ou substituírem o
protagonista principal do jogo daquela região, nem o Campeão daquela geração
específica — podem ouvir falar dele, nunca interagir diretamente.

## Ficha do Treinador (o jogador) — minimalista, sem estatística SWADE

O treinador NÃO tem atributos, perícias, vantagens nem complicações — nunca
gere nem preencha esses campos pra ele. A ficha do treinador é só sabor:

- Nome, aparência, personalidade, motivação de por que treina Pokémon
- Nenhum campo mecânico do referencia-swade.md se aplica a ele diretamente

O treinador NUNCA rola dado sozinho. Toda ação mecânica da aventura — ataque,
defesa, perícia, teste — é feita através de um dos Pokémon dele. O jogador
comanda, o Pokémon executa e rola.

## Os 3 Pokémon — cada um é uma ficha de combatente completa

Cada treinador tem exatamente 3 Pokémon. TODAS as raças, perícias, atributos,
armas e Cartas Selvagens do referencia-swade.md vão pros Pokémon, nunca pro
treinador. Cada Pokémon usa o MESMO schema de NPC combatente já definido em
03-npcs.md (atributos, pericia_chave, arma, armadura_bonus, carta_selvagem,
resistencia, aparar) — não crie um sistema de PS/moves separado, nunca.

### Espécie → Raça mecânica (mapeamento por FORMA FÍSICA, não por elemento)
O elemento de um Pokémon (fogo, água, planta...) é só sabor da "arma" — nunca
cria tabela de fraquezas/resistências elementais nova. A RAÇA mecânica
depende da forma física do Pokémon:

| Forma física do Pokémon | Raça mecânica (SWADE) | Exemplos de referência |
|---|---|---|
| Pássaro/alado | Aviano | Pidgey, Staraptor, Talonflame |
| Aquático/marinho | Aquariano | Magikarp, Vaporeon, Lapras |
| Pequeno/roedor/fada | Pequenino | Pichu, Jigglypuff, Cleffa |
| Réptil/dragão | Sáurio | Charmander, Dratini, Salamence |
| Humanoide psíquico/fantasma | Elfo | Gardevoir, Mismagius, Gallade |
| Mecânico/mineral | Androide | Magnemite, Klink, Porygon |
| Feral/mamífero de quatro patas | Rakashano | Growlithe, Lucario, Mightyena |

Se um Pokémon não se encaixar claramente em nenhuma linha, escolha a mais
próxima pela silhueta geral — não precisa ser perfeito, só consistente.

### Papel de Combate (equivalente ao "Job" de Final Fantasy — sabor + Perícia-Chave)

| Papel de Combate | Perícia-Chave sugerida | Sabor mecânico |
|---|---|---|
| Atacante Físico | Lutar | Dano corpo a corpo alto (Força+dX) |
| Atacante à Distância | Atirar | Ataques elementais à distância, dado fixo (ex: 2d6) |
| Velocista/Evasivo | Furtividade ou Atletismo | Alta Agilidade, foge/reposiciona bem, dano mais baixo |
| Tanque/Defensivo | Lutar (com foco em Vigor alto) | Resistência elevada, aguenta mais, dano moderado |
| Suporte/Utilidade | Foco ou Curar | Pouco dano direto, mas oferece Suporte (+1/+2) aos aliados |

O elemento (fogo, elétrico, planta, etc.) vira só o NOME e o SABOR do ataque
na "arma" — ex: um Atacante à Distância elétrico tem
`"arma": {"nome": "Lança-Elétrica", "dano": "2d6"}`. Nunca crie multiplicador
de dano por fraqueza elemental — se quiser vantagem tática situacional, use
os modificadores padrão (+2/-2) do referencia-swade.md, nunca um sistema novo.

### Carta Selvagem entre os 3 Pokémon
Normalmente, só o Pokémon "principal" ou mais desenvolvido de um treinador
(equivalente ao starter/parceiro mais antigo) deveria ser Carta Selvagem — os
outros dois ficam como Extras comuns, seguindo a mesma regra geral do
referencia-swade.md (chefe de cena é Carta Selvagem, capanga não é). Isso
vale tanto pra Pokémon de jogador quanto de NPC/Time vilão.

### Em combate
Jogador e Pokémon agem na mesma Carta de Ação — o Pokémon não rouba turno
do treinador. Narrativamente, o treinador comanda ("Lança-Elétrica, agora!"),
o Pokémon executa e rola o dado.

## Locais recorrentes
Uma cidade natal pequena (ponto de partida), rotas selvagens entre cidades
(equivalente à Travessia), um Centro Pokémon (posto de cura/apoio, sempre
seguro), um Ginásio ou instalação de um Time vilão (dungeon), a sede da Liga
Pokémon (reservada pro clímax de campanhas maiores).

## Artefatos e papéis narrativos recorrentes
- **Pokémon Lendário**: entidade rara e poderosa, raramente capturável numa
  oneshot — mais frequentemente um símbolo mitológico ou a causa raiz da
  ameaça central
- **Professor/Professora regional**: figura de autoridade que entrega a
  missão inicial (equivalente ao NPC de Convocação)
- **Time vilão**: organização antagonista recorrente (nunca maldade pura —
  sempre uma causa distorcida: proteção ambiental levada ao extremo,
  controle de poder pra "um bem maior", etc.)

## Arquétipos de antagonista
O líder do Time vilão quase sempre acredita genuinamente na própria causa —
nunca é ganância pura. Segue a mesma regra de moral cinzenta do resto do
projeto: dê a ele uma "verdade por trás" real, revelada no clímax.

## DNA temático (arquétipos e motivos recorrentes)
Jornada de amadurecimento e vínculo — o grupo cresce tanto quanto seus
companheiros Pokémon. Competição saudável entre aliados (rival recorrente,
nunca inimigo). Ênfase em variedade de ambientes e criaturas ao longo da
travessia. Tom: aventureiro, caloroso, otimista — mesmo quando o Time vilão é
genuinamente ameaçador, a esperança nunca desaparece de vez.

## Referência estrutural obrigatória
Siga a mesma estrutura de 6 blocos de referencia-hyrule.md, com estas
adaptações:
- Bloco 1 (Convocação): geralmente um Professor regional entrega a missão
  inicial, junto com o primeiro Pokémon companheiro do grupo, se ainda não
  tiverem um
- Bloco 2 (Vila de Apoio): um Centro Pokémon ou cidade pequena — sempre
  espaço de cura/preparo sem risco
- Bloco 3 (Travessia): uma rota selvagem, com encontros de Pokémon selvagens
  no lugar de "criaturas hostis" genéricas
- Bloco 4 (Dungeon): um Ginásio, base do Time vilão, ou caverna/floresta
  densa — mini-prova pode ser uma batalha Pokémon contra um capanga do Time
