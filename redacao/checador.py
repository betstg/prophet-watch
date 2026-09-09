"""O checador. Abre a materia e confere antes de qualquer coisa ir para o papel.

Essa e a etapa que o jornal existe para ter. Nada entra sem passar por aqui.
"""

import re
import bancadas
import leitura
import modelo

INSTRUCAO = """Voce checa noticia para o Prophet Watch, um jornal de Harry Potter.
Voce e a primeira pessoa que realmente LE a pagina. O reporter so olhou o titulo.
Entao a decisao e sua, e ela vale mais que o que o titulo prometia.

Recebe o conteudo de uma pagina. Responda a partir do texto que esta ali, nunca
a partir do titulo sozinho.

APROVE quando a pagina traz alguma coisa que um leitor do jornal ia querer saber.
Vale fato novo, anuncio, escalacao, data, numero, imagem oficial, declaracao de
quem faz a obra, e tambem analise que faz um argumento de verdade sobre o texto
dos livros. Se o titulo era fraco mas o corpo tem coisa boa, aprove pelo corpo.

BOATO NAO E MOTIVO PARA REPROVAR. O jornal publica boato como boato. Se a
pagina conta uma coisa que circula sem fonte com nome, aprove e marque a
procedencia como boato, dizendo de onde a alegacao saiu. O leitor merece saber
que aquilo esta circulando e que nao esta confirmado.

REPROVE so nestes casos.
A pagina nao e do universo de Harry Potter.
O corpo nao sustenta nenhuma alegacao, e so titulo e propaganda.
E repeticao do que o jornal ja publicou, sem nada novo.
Nao da para saber a data.

A data que vale e a que esta escrita na pagina. Se a pagina disser uma data e o
campo tecnico disser outra, confie na pagina e diga isso.

Escolha tambem a melhor fotografia. Prefira, nesta ordem, a imagem de abertura
da materia, a arte oficial do assunto, e uma foto editorial de dentro do texto.
Nunca escolha logotipo, retrato de autor, icone ou anuncio.

Responda em JSON, um objeto so.
{"aprovada": true ou false,
 "motivo": "uma frase curta",
 "data": "AAAA-MM-DD ou vazio",
 "fato": "o que a pagina sustenta, em duas ou tres frases curtas",
 "assunto": "quem ou o que a materia trata, em poucas palavras",
 "editoria_sugerida": "HBO series, Films, Books and audio, Games, Stage, Television, Shops and experiences, Fandom ou Analise e teoria",
 "procedencia": "oficial, imprensa, fa, ou boato",
 "origem_do_boato": "quando for boato, de onde a alegacao saiu, senao vazio",
 "foto": "o endereco exato de uma das fotos que recebeu, ou vazio",
 "foto_e_do_evento": true se a foto mostra o proprio fato, false se mostra o assunto,
 "foto_legenda": "se for do assunto, uma linha curta em portugues dizendo o que a foto mostra"}

Nao use dois pontos, ponto e virgula, nem traco como pausa em nada que escrever."""


DATA = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _dia(texto):
    m = DATA.search(texto or "")
    return m.group(0) if m else ""


def checa(candidato, desde, ate):
    """Abre, le e julga. Devolve None quando reprova."""
    try:
        pag = leitura.pagina(candidato["endereco"])
    except Exception as e:
        return dict(reprovada="nao abriu, %s" % type(e).__name__,
                    endereco=candidato["endereco"])

    fotos = "\n".join("- " + f for f in pag["fotos"]) or "nenhuma"
    texto = (
        "Endereco, %s\nVeiculo, %s\nTitulo, %s\nData no campo tecnico, %s\n"
        "Video no corpo, %s\n\nFotos disponiveis\n%s\n\nTexto da pagina\n%s"
        % (pag["url"], pag["veiculo"], pag["titulo"],
           pag["data_declarada"] or "nao declarada", pag["video"] or "nenhum",
           fotos, pag["corpo"]))

    v = modelo.pergunta(INSTRUCAO, texto, teto_saida=1200)
    if not isinstance(v, dict):
        return dict(reprovada="o checador nao respondeu",
                    endereco=candidato["endereco"])
    if not v.get("aprovada"):
        return dict(reprovada=v.get("motivo", "reprovada"),
                    endereco=candidato["endereco"])

    dia = _dia(v.get("data")) or _dia(pag["data_declarada"])
    if not dia:
        return dict(reprovada="sem data", endereco=candidato["endereco"])
    if dia < desde or dia > ate:
        return dict(reprovada="fora da janela, %s" % dia,
                    endereco=candidato["endereco"])

    foto = (v.get("foto") or "").split(" || ")[0].strip()
    if foto and foto not in [f.split(" || ")[0] for f in pag["fotos"]]:
        foto = ""   # o modelo inventou um endereco, entao a materia sai sem foto

    fraca = any(d in pag["veiculo"] for d in bancadas.FONTE_FRACA)
    return dict(
        endereco=pag["url"], veiculo=pag["veiculo"], titulo=pag["titulo"],
        data=dia, fato=modelo.limpa(v.get("fato", "")),
        assunto=v.get("assunto", ""), editoria=v.get("editoria_sugerida", "Fandom"),
        procedencia=(v.get("procedencia") or "").lower(),
        origem_boato=v.get("origem_do_boato", ""),
        foto=foto, foto_do_evento=bool(v.get("foto_e_do_evento")),
        foto_legenda=modelo.limpa(v.get("foto_legenda", "")),
        video=pag["video"], fonte_fraca=fraca, editoria_reporter=candidato.get("editoria"),
    )
