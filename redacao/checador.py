"""O checador. Abre a materia e confere antes de qualquer coisa ir para o papel.

Essa e a etapa que o jornal existe para ter. Nada entra sem passar por aqui.
"""

import re
import bancadas
import leitura
import modelo

INSTRUCAO = """Voce checa noticia para o Prophet Watch. Voce e chato de proposito.

Recebe o conteudo de uma pagina. Diz se aquilo e uma noticia de verdade, nova,
e sustentada pelo proprio texto da pagina.

Reprove quando:
o corpo da pagina nao sustenta o que o titulo promete;
e recapitulacao de coisa antiga, lista, questionario ou promocao;
a origem e conta de rede social, conta de piada, agregador ou boato sem fonte
com nome;
a alegacao aparece so no titulo e nunca no texto;
a materia trata do filme antigo e nao de fato novo;
o texto nao deixa claro nenhuma data.

A data que vale e a que esta escrita na pagina. Se a pagina disser uma data e o
campo tecnico disser outra, confie na pagina e diga isso.

Escolha tambem a melhor fotografia. Prefira, nesta ordem, a imagem de abertura
da materia, a arte oficial do assunto, e uma foto editorial de dentro do texto.
Nunca escolha logotipo, retrato de autor, icone ou anuncio.

Responda em JSON, um objeto so.
{"aprovada": true ou false,
 "motivo": "uma frase curta",
 "data": "AAAA-MM-DD ou vazio",
 "fato": "o fato novo em duas ou tres frases curtas, so o que a pagina sustenta",
 "assunto": "quem ou o que a materia trata, em poucas palavras",
 "editoria_sugerida": "HBO series, Films, Books and audio, Games, Stage, Television, Shops and experiences, Fandom ou Analise e teoria",
 "procedencia": "oficial, imprensa, fa, agregador ou boato",
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
    if (v.get("procedencia") or "").lower() in ("agregador", "boato"):
        return dict(reprovada="procedencia, %s" % v.get("procedencia"),
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
        foto=foto, foto_do_evento=bool(v.get("foto_e_do_evento")),
        foto_legenda=modelo.limpa(v.get("foto_legenda", "")),
        video=pag["video"], fonte_fraca=fraca, editoria_reporter=candidato.get("editoria"),
    )
