"""O reporter. Um por editoria.

Ele nao abre pagina nenhuma. Ele olha a lista de manchetes que o vigia trouxe
da area dele e diz quais merecem que alguem gaste tempo abrindo. E a etapa
mais barata da redacao, porque ele le titulo, nao materia.
"""

import json
import modelo

PAUTA = {
    "serie": "a serie do HBO Max, elenco, gravacoes, trailers, datas, a segunda temporada na Camara Secreta, e vazamento de set",
    "tela": "os filmes, relancamentos, televisao e o que a imprensa de industria apura sobre a serie",
    "jogos": "jogos, Hogwarts Legacy e a sequencia, titulos de celular e LEGO",
    "parques": "parques, areas tematicas, lojas, exposicoes e experiencias",
    "palco": "Cursed Child e qualquer montagem de teatro",
    "brasil": "o que a imprensa fa em portugues esta publicando e analisando",
    "estudo": "leitura dos livros, alquimia, simbolo e critica, quando ha argumento de verdade",
}

INSTRUCAO = """Voce e reporter do Prophet Watch, um jornal de noticias de Harry Potter.
Sua area e {pauta}.

Recebe uma lista de manchetes novas. Voce decide SO DUAS COISAS, e nada alem disso.

1. Isso e do universo de Harry Potter? Conta a serie do HBO, os filmes, os livros,
   os audiolivros, os jogos, o teatro, os parques, as lojas, o elenco, quem faz a
   obra, e a comunidade de fas falando dessas coisas. Nao conta assunto de outra
   franquia que so cita Harry Potter de passagem.

2. Isso e obviamente a mesma materia que o jornal ja publicou? Recebe a lista do
   que ja esta no jornal. So descarte quando for claramente a mesma coisa.

Se passar nessas duas, mande abrir. Ponto.

Voce NAO decide se e importante. Voce NAO decide se e fato ou boato. Voce NAO
decide se merece espaco. Voce NAO descarta por ser lista, por ser recapitulacao,
nem por parecer fraco. Titulo mente, e materia boa se esconde atras de titulo
ruim. Quem julga conteudo e quem abriu a pagina e leu, e nao e voce.

Na duvida, mande abrir. Abrir errado custa alguns segundos. Descartar errado
perde a materia para sempre.

Responda em JSON, um vetor com UM item para CADA manchete que recebeu, na mesma
ordem, sem pular nenhuma. Cada item assim.
{{"endereco": "...", "abrir": true ou false, "porque": "uma frase curta"}}
Quando abrir for false, o porque diz qual das duas regras reprovou, fora do
universo ou ja publicado. Nao invente endereco, use exatamente os que recebeu."""


def pauta(editoria, novidades, ja_publicadas=None, teto=45):
    if not novidades:
        return [], []
    ja = "\n".join("- " + t for t in (ja_publicadas or [])[:40]) or "nada ainda"
    lista = "\n".join(
        "%d. [%s] %s\n   %s" % (i + 1, n["bancada"], n["titulo"][:170], n["endereco"])
        for i, n in enumerate(novidades[:teto]))
    saida = modelo.pergunta(
        INSTRUCAO.format(pauta=PAUTA.get(editoria, "noticias de Harry Potter")),
        ("Manchetes que o jornal ja publicou.\n%s\n\n"
         "Manchetes novas da sua area.\n\n%s" % (ja, lista)),
        teto_saida=2500)
    if saida is None:
        # o modelo nao respondeu. Isso nao pode passar por dia sem noticia,
        # senao a redacao fica muda e ninguem descobre.
        raise modelo.SemModelo("o reporter de %s nao recebeu resposta do modelo" % editoria)
    if not isinstance(saida, list):
        raise modelo.SemModelo("o reporter de %s recebeu resposta fora do formato" % editoria)
    titulos = {n["endereco"]: n["titulo"] for n in novidades}
    escolhidos, descartados = [], []
    for item in saida:
        if not isinstance(item, dict):
            continue
        e = (item.get("endereco") or "").strip()
        if e not in titulos:
            continue
        registro = dict(endereco=e, titulo=titulos[e],
                        porque=item.get("porque", ""), editoria=editoria)
        if item.get("abrir"):
            escolhidos.append(registro)
        else:
            descartados.append(registro)
    return escolhidos, descartados
