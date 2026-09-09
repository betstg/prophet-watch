"""O editor. Escolhe o que entra, escreve a manchete e fecha a edicao."""

import re
import modelo

STATUS = ("official", "confirmed", "analysis", "rumor", "leak", "paparazzi")
EDITORIAS = ("HBO series", "Films", "Books and audio", "Games", "Stage",
             "Television", "Shops and experiences", "Fandom", "Analise e teoria")

INSTRUCAO = """Voce e o editor do Prophet Watch, um jornal de noticias de Harry Potter
no formato do Profeta Diario. Recebe materias ja apuradas e checadas e escreve
a edicao.

Para cada materia escreva manchete e resumo em ingles, que e a lingua do jornal.

A manchete diz o fato, nao promete. Entre 8 e 16 palavras. Nada de pergunta,
nada de suspense, nada de voce nao vai acreditar.

O resumo tem tres ou quatro frases curtas com o que a pessoa precisa saber.
So o que a apuracao sustenta. Nao repita a manchete na primeira frase.

Escolha o status com honestidade.
official, quando quem anuncia e a Warner, a HBO, a Bloomsbury ou os canais oficiais.
confirmed, quando nao e anuncio oficial mas a imprensa de industria apurou.
analysis, quando e leitura de fa, de podcast ou de estudioso do livro.
rumor, quando circula sem fonte com nome. O jornal publica boato, e publica
como boato. Quando for rumor, a manchete e o resumo tem que deixar claro que
aquilo e uma alegacao que circula, dizer de onde ela saiu, e dizer o que ainda
nao esta confirmado. Nunca escreva boato com cara de fato.
leak, quando e material que escapou antes da hora.
paparazzi, quando e foto feita fora do set por fotografo de imprensa.

Regra de escrita, sem excecao. Nunca use dois pontos, ponto e virgula, travessao
ou traco como pausa. Frases curtas e diretas. Sem emoji.

Responda em JSON, um vetor, na ordem em que recebeu.
{"usar": true ou false,
 "headline": "...",
 "summary": "...",
 "status": "um dos seis",
 "category": "uma das editorias que a materia recebeu",
 "slug": "tres a cinco palavras em minusculo separadas por hifen, sem acento"}
Ponha usar false quando a materia repetir algo que ja esta no jornal ou nao
merecer espaco."""


def _limpo(t):
    return modelo.limpa(re.sub(r"\s+", " ", (t or "").strip()))


def fecha(aprovadas, ja_publicadas):
    """Devolve as materias prontas para o add-news.py."""
    if not aprovadas:
        return []
    ja = "\n".join("- " + t for t in ja_publicadas[:45]) or "nada ainda"
    corpo = []
    for i, a in enumerate(aprovadas):
        corpo.append(
            "MATERIA %d\nData, %s\nVeiculo, %s\nProcedencia, %s\n"
            "Editoria sugerida, %s\nTitulo original, %s\nApuracao, %s%s"
            % (i + 1, a["data"], a["veiculo"], a["procedencia"],
               a["editoria"], a["titulo"][:180], a["fato"],
               ("\nOrigem do boato, " + a["origem_boato"])
               if a.get("origem_boato") else ""))
    texto = ("Manchetes que ja estao no jornal, nao repita nenhuma delas.\n%s\n\n"
             "Materias apuradas hoje.\n\n%s" % (ja, "\n\n".join(corpo)))

    saida = modelo.pergunta(INSTRUCAO, texto, teto_saida=3000)
    if not isinstance(saida, list):
        raise modelo.SemModelo("o editor nao devolveu uma edicao utilizavel")

    prontas = []
    for a, v in zip(aprovadas, saida):
        if not isinstance(v, dict) or not v.get("usar"):
            continue
        headline = _limpo(v.get("headline"))
        summary = _limpo(v.get("summary"))
        if len(headline) < 20 or len(summary) < 60:
            continue
        status = (v.get("status") or "").strip()
        if status not in STATUS:
            status = "confirmed" if a["procedencia"] == "imprensa" else "analysis"
        categoria = (v.get("category") or "").strip()
        if categoria not in EDITORIAS:
            categoria = a["editoria"] if a["editoria"] in EDITORIAS else "Fandom"
        slug = re.sub(r"[^a-z0-9-]", "", (v.get("slug") or "").lower().replace(" ", "-"))
        slug = re.sub(r"-{2,}", "-", slug).strip("-")[:48] or "materia"
        prontas.append(dict(
            id="%s-%s" % (slug, a["data"]),
            date=a["data"], status=status, category=categoria,
            headline=headline, summary=summary,
            source=a["veiculo"], url=a["endereco"],
            _foto=a.get("foto", ""), _video=a.get("video", ""),
            _legenda="" if a.get("foto_do_evento") else a.get("foto_legenda", ""),
        ))
    return prontas
