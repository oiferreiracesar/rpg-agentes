# Referência de Universo — L.A. Noire (para uso com SWADE)

Use isto como camada TEMÁTICA sobre o referencia-swade.md — a mecânica de
resolução (perícias, Aparar, Resistência, Carta Selvagem) sempre usa SWADE.
Este é um universo investigativo/policial realista — nunca sobrenatural,
nunca fantástico. Se o brief do usuário pedir elemento sobrenatural, isso
pertence a Ordem Paranormal ou Silent Hill, não aqui.

## Sobre o campo "Era de Referência"

| Era | Nota de ambientação |
|---|---|
| Anos 1940-50 (Era Clássica) | Pós-guerra, corrupção institucional generalizada, imprensa sensacionalista, carros e telefones fixos como limite tecnológico |
| Anos 1980 | Crime organizado urbano, guerra às drogas, primeiras câmeras de vigilância, tecnologia forense ainda limitada |
| Anos 2000 | Celulares e internet começando a aparecer em investigação, mas ainda muito trabalho de campo tradicional |
| Dias atuais | Forense avançada (DNA, câmeras por toda parte), mas ainda dependente de testemunha e interrogatório humano |
| Sem preferência específica | Use um tom atemporal, evitando âncoras tecnológicas específicas demais |

## Sobre o campo "Cidade de Referência"
Texto livre — o Mestre define a cidade (real ou fictícia). Nunca ancore em
uma cidade real específica de forma que force geografia real detalhada;
trate como pano de fundo atmosférico, não mapa exato.

## Sem tabela de raças
Ambientação realista contemporânea — todo personagem jogador e NPC é
Humano. A variedade vem de PROFISSÃO/ORIGEM (detetive, jornalista,
promotor, ex-militar, informante), não de raça.

## O detetive como protagonista
O grupo de jogadores é sempre ligado, direta ou indiretamente, a uma
investigação oficial — policiais, detetives particulares contratados,
promotores, ou jornalistas investigativos trabalhando em paralelo à polícia.
Ao menos um NPC recorrente deve ser uma autoridade policial (capitão,
delegado) que atribui casos e pressiona por resultados — nem sempre aliado
confiável; corrupção institucional é tema esperado, não exceção.

## A Mecânica de Interrogatório (central deste universo)

Diferente de um teste simples de Persuadir/Intimidar, interrogatório aqui
é uma **árvore de decisão baseada em evidência coletada**, não em dado. Cada
pergunta feita a um suspeito/testemunha tem três respostas possíveis:

- **Verdade**: aceita a resposta do NPC sem contestar. Sem risco, sem
  ganho — usa quando não há motivo pra desconfiar.
- **Pressionar**: questiona sem ter uma prova concreta na mão. É fricção
  psicológica — pode fazer o NPC ceder informação nova (se ele já estava
  mentindo mas você não tem como provar), ou pode fechá-lo de vez se ele
  perceber que é um blefe. Teste de Persuadir ou Intimidar, Dif. 4, decide
  o resultado.
- **Mentira**: só funciona de verdade se o jogador tiver uma **evidência
  específica** já coletada (um item de `output/06-documentos.json`) que
  contradiz literalmente o que o NPC acabou de dizer. Apontar a evidência
  certa é o momento de maior recompensa do sistema — apontar sem prova, ou
  com a prova errada, fecha o NPC e pode custar a confiança dele pro resto
  do interrogatório.

O ponto central: **a evidência que sustenta cada "Mentira" precisa já
existir no roteiro antes daquele interrogatório** — ligada a um documento
ou pista de uma cena anterior. Isso é o que faz funcionar sem dado
decidindo tudo: o jogador só ganha se prestou atenção antes, não se rolou
bem.

### ⚠️ Dependência de schema — ainda não implementada nos outros agentes
Pra essa mecânica funcionar gerada pelo pipeline (não só narrada em texto
solto), o Roteirista precisa de um campo novo dentro de cena, algo como:

```json
"interrogatorio": {
  "npc_id": "id do NPC sendo interrogado",
  "perguntas": [
    {
      "topico": "do que se trata a pergunta",
      "resposta_npc": "o que o NPC diz",
      "e_mentira": true/false,
      "documento_id_que_contradiz": "id de um documento em 06-documentos.json (só se e_mentira=true)",
      "consequencia_verdade": "o que acontece se aceitar",
      "consequencia_pressionar": "o que acontece se pressionar sem prova",
      "consequencia_mentira_certa": "o que acontece acertando a evidência certa",
      "consequencia_mentira_errada": "o que acontece errando a evidência ou acusando sem ser mentira"
    }
  ]
}
```

Isso exige mexer no `01-roteirista.md` (gerar esse campo) **e** no
`06-documentos.md` (garantir que documentos citados em
`documento_id_que_contradiz` realmente existem) — coordenados entre si,
mesmo padrão de coordenação dupla que já usamos pra Pokémon (treinador +
Pokémon) e Digimon (Tamer + parceiro). Essa parte ainda não foi construída
— fica como próximo passo, se você quiser seguir com esse universo depois.

## Locais recorrentes
Delegacia ou escritório do detetive (base de operações, "Vila de Apoio"
natural), cena de crime (Convocação natural — corpo encontrado, denúncia
recebida), ruas da cidade à noite (Travessia — perseguição, informante
relutante), um local ligado ao suspeito principal (residência, negócio,
esconderijo — Dungeon: não masmorra física, mas investigação estruturada
em cômodos/áreas com pistas específicas em cada uma).

## Artefatos e papéis narrativos recorrentes
- **Prova física**: arma do crime, impressão digital, carta, fotografia —
  sempre a base de uma "Mentira" bem-sucedida num interrogatório futuro
- **Informante relutante**: NPC que sabe algo mas só fala sob pressão ou
  barganha — bom gancho de Pressionar
- **Corrupção institucional**: um superior, colega ou autoridade que
  atrapalha a investigação por interesse próprio — nunca vilão cartunesco,
  sempre alguém protegendo algo específico e compreensível (carreira,
  família, dívida)

## Arquétipos de antagonista
O culpado central raramente é um monstro — é alguém com um motivo humano
reconhecível (ciúme, desespero financeiro, vingança por uma injustiça
anterior) levado a um ato que não tem mais volta. Segue a mesma regra de
moral cinzenta do projeto inteiro: humanize antes do confronto final,
mesmo que o crime em si seja grave.

## DNA temático (arquétipos e motivos recorrentes)
Atmosfera urbana, sombras longas, moralidade ambígua — ninguém no caso é
inteiramente limpo, incluindo às vezes o próprio protagonista. Cada
evidência encontrada deve ter função dupla: informa a história E abre uma
opção mecânica futura (uma "Mentira" possível num interrogatório
posterior). Diálogo importa mais que combate — está tudo bem se uma
aventura inteira não tiver nenhum combate físico. Tom: tenso, melancólico,
elegante — nunca cômico, nunca sobrenatural.

## Referência estrutural obrigatória
Siga a mesma estrutura de 6 blocos de referencia-hyrule.md, com estas
adaptações:
- Bloco 0 (Introdução): notícia do crime ou corpo encontrado, tom de
  manchete de jornal ou rádio da época
- Bloco 1 (Convocação): a cena do crime em si — primeira coleta de
  evidências, primeiro interrogatório (geralmente uma testemunha, não
  ainda o culpado)
- Bloco 2 (Vila de Apoio): a delegacia — analisar evidências, receber
  pressão do superior, planejar próximos passos
- Bloco 3 (Travessia): investigação de campo — seguir uma pista pela
  cidade, pode incluir um segundo interrogatório com informação nova
- Bloco 4 (Dungeon): o local central ligado ao suspeito principal — pistas
  distribuídas em áreas específicas (nunca "puzzle de fantasia", sempre
  evidência física real: documentos, objetos, marcas)
- Bloco 5 (Clímax): o interrogatório final e decisivo com o culpado — o
  "chefe de cena" aqui não é combate, é a sequência de perguntas mais
  importante da aventora, com toda a evidência coletada até então podendo
  ser usada
