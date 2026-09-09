# A redacao

O jornal se atualiza sozinho pelo GitHub Actions. Nada disso depende do Mac.

## Quem faz o que

| arquivo | papel |
|---|---|
| `bancadas.py` | as 40 fontes que o jornal le, com editoria e feed |
| `vigia.py` | passa nas bancadas e separa o que e novo. Nao usa IA, nao gasta token |
| `reporter.py` | um por editoria. Le so os titulos e diz o que vale abrir |
| `leitura.py` | abre a pagina e tira dela o texto, a data e as fotos |
| `checador.py` | confere cada materia contra a propria pagina e reprova o que nao se sustenta |
| `editor.py` | escreve manchete e resumo, da status e editoria, fecha a edicao |
| `fotos.py` | baixa a foto e guarda nos dois tamanhos |
| `redacao.py` | o maestro, roda tudo na ordem |
| `visto.json` | a memoria do vigia, os enderecos que ele ja viu |

## Por que e barato

O vigia e a peneira. Em dia parado ele le as quarenta bancadas, nao acha link
novo e o dia acaba ali, sem uma unica chamada ao modelo. O modelo so entra
quando aparece materia nova de verdade.

## O que precisa estar configurado

Um segredo no repositorio chamado `GEMINI_API_KEY`, em Settings, Secrets and
variables, Actions. A chave sai de graca em aistudio.google.com, sem cartao.

Para trocar de modelo, mexa so em `modelo.py`. O resto da redacao nao sabe
qual fornecedor esta atendendo.

## Como rodar na mao

Na aba Actions, workflow Redacao do Prophet Watch, botao Run workflow.
