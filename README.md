# Gerador de Oneshots de RPG — Automação via GitHub Actions

Encadeia 5 agentes de IA (Roteirista → Direção de Arte → NPCs → Cartógrafo → Sonoplastia)
usando o Gemini CLI dentro do GitHub Actions. Gratuito com conta pessoal.

## Configuração (só precisa fazer uma vez)

### 1. Crie um repositório no GitHub
Pode ser privado. Suba todos os arquivos desta pasta pra ele, mantendo a estrutura
de pastas exatamente como está (`.github/agents/`, `.github/workflows/`).

### 2. Pegue sua chave de API do Gemini
Vá em https://aistudio.google.com/apikey e gere uma chave — tem cota gratuita generosa.

### 3. Cadastre a chave como segredo do repositório
No seu repositório: **Settings → Secrets and variables → Actions → New repository secret**
- Nome: `GEMINI_API_KEY`
- Valor: a chave que você gerou no passo 2

### 4. Pronto — já pode rodar

## Como gerar uma aventura nova

1. Vá na aba **Actions** do seu repositório
2. Clique em **Gerar Oneshot de RPG** na lista à esquerda
3. Clique em **Run workflow**
4. No campo de texto, descreva o que você quer, por exemplo:
   `Faroeste visceral, moral cinzenta, tom de vingança, 3-4 horas, 3-5 jogadores`
5. Clique em **Run workflow** de novo pra confirmar
6. Espere o fluxo rodar (alguns minutos — ele executa os 5 agentes em sequência)
7. Quando terminar, entra na execução concluída e baixa o arquivo `oneshot-gerada`
   no final da página — vem com os 5 JSONs prontos (`01-roteirista.json` até
   `05-sonoplastia.json`)

## Observações importantes

- **Isso não inclui os agentes de Documentos e Compilador ainda** — só os 5 que já
  validamos juntos. Dá pra adicionar depois seguindo o mesmo padrão dos outros passos
  no arquivo `.github/workflows/gerar-oneshot.yml`.
- **Cada execução conta como várias chamadas de API** (uma por agente). A cota gratuita
  do Gemini é generosa, mas se você rodar muitas aventuras seguidas no mesmo dia pode
  esbarrar no limite diário — nesse caso, é só esperar o dia seguinte.
- **Se algum agente sair com formato errado** (como aconteceu nas primeiras tentativas
  do Roteirista), o JSON daquele passo específico pode sair malformado. Vale sempre
  conferir os arquivos antes de usar — a automação não valida o formato sozinha ainda.
- Os arquivos de instrução de cada agente estão em `.github/agents/` — se quiser ajustar
  alguma regra (como fizemos várias vezes durante os testes), edite o arquivo `.md`
  correspondente direto no repositório.
