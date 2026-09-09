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

Recebe uma lista de manchetes novas com o endereco de cada uma. Devolve so as
que valem a pena abrir e apurar.

Aceite: fato novo, anuncio, escalacao, data, trailer, imagem oficial, numero,
declaracao de quem faz a obra, ou analise que faz um argumento real sobre o
texto dos livros.

Recuse: recapitulacao do que ja saiu, lista do tipo dez momentos, questionario,
promocao, materia que so pergunta uma coisa no titulo sem responder, fofoca sem
fonte, e qualquer coisa que nao seja do mundo de Harry Potter.

Responda em JSON, um vetor com UM item para CADA manchete que recebeu, na mesma
ordem, sem pular nenhuma. Cada item assim.
{{"endereco": "...", "abrir": true ou false, "porque": "uma frase curta"}}
Quando abrir for true, o porque diz o fato que voce espera achar. Quando for
false, o porque diz por que descartou. Nao invente endereco, use exatamente os
que recebeu. No maximo 8 com abrir true, os mais fortes."""


def pauta(editoria, novidades, teto=45):
    if not novidades:
        return [], []
    lista = "\n".join(
        "%d. [%s] %s\n   %s" % (i + 1, n["bancada"], n["titulo"][:170], n["endereco"])
        for i, n in enumerate(novidades[:teto]))
    saida = modelo.pergunta(
        INSTRUCAO.format(pauta=PAUTA.get(editoria, "noticias de Harry Potter")),
        "Manchetes novas da sua area.\n\n" + lista,
        teto_saida=1500)
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
