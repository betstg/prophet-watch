"""O vigia. Le as bancadas e devolve so o que e novo.

Isso aqui nao usa inteligencia nenhuma e nao gasta um token. E a peneira que
faz a redacao inteira caber de graca. Em dia parado ele olha as quarenta
bancadas, nao acha nada e o dia acaba ali.
"""

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
VISTO = os.path.join(AQUI, "visto.json")

NAVEGADOR = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# o assunto do jornal. Quem nao fala disso nao passa daqui.
ASSUNTO = re.compile(
    r"harry.?potter|hogwarts|wizarding|dumbledore|voldemort|hermione|"
    r"weasley|snape|grindelwald|fantastic.?beasts|animais.?fant|"
    r"cursed.?child|crian[cç]a.?amaldi|beco.?diagonal|diagon.?alley|"
    r"quadribol|quidditch|sonserina|grifin[oó]ria|corvinal|lufa|"
    r"slytherin|gryffindor|ravenclaw|hufflepuff", re.I)

# bancadas que so falam de Harry Potter, entao nao precisam da peneira
SO_DISSO = ("potterish", "mugglenet", "leaky-cauldron", "ordemdafenix",
            "mundobruxo", "hogwartsprofessor", "hp-lexicon", "rowlinglibrary",
            "criticalmagictheory", "mugglecast", "wizardingworlddirect",
            "harrypotter", "snitchseeker", "HarryPotter")

TEMPO = 20


def _abre(url, tempo=TEMPO, teto=600000):
    pedido = urllib.request.Request(url, headers={
        "User-Agent": NAVEGADOR,
        "Accept": "application/rss+xml, application/atom+xml, text/html, */*",
        "Accept-Language": "en,pt;q=0.8",
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(pedido, timeout=tempo, context=ctx) as r:
        bruto = r.read(teto)
    return bruto.decode("utf-8", "replace")


def _texto(no):
    return "".join(no.itertext()).strip() if no is not None else ""


def _do_feed(xml):
    """titulo e endereco de cada item, seja RSS, Atom ou RDF"""
    saida = []
    try:
        raiz = ET.fromstring(xml.encode("utf-8", "replace"))
    except ET.ParseError:
        return saida
    for item in raiz.iter():
        etiqueta = item.tag.split("}")[-1]
        if etiqueta not in ("item", "entry"):
            continue
        titulo = endereco = ""
        for filho in item:
            f = filho.tag.split("}")[-1]
            if f == "title" and not titulo:
                titulo = _texto(filho)
            elif f == "link":
                if filho.get("href"):
                    if filho.get("rel") in (None, "alternate") and not endereco:
                        endereco = filho.get("href")
                elif not endereco:
                    endereco = _texto(filho)
        if endereco:
            saida.append((titulo, endereco))
    return saida


def _do_indice(html, base):
    """links de materia numa pagina que nao tem feed.

    A janela do miolo da ancora precisa ser larga. Site moderno embrulha a
    materia inteira dentro do <a>, com <picture>, srcset e varios <span>,
    e isso passa de dois mil caracteres. Com a janela curta que estava
    aqui antes, essas ancoras nao casavam com a expressao e a fonte ficava
    cega. O harrypotter.com achava 1 link, que era item de menu, em vez
    das 12 materias que estao na pagina.
    """
    vistos, saida = set(), []
    for m in re.finditer(r'<a\b[^>]*href="([^"#?]+)"[^>]*>(.{0,4000}?)</a>',
                         html, re.I | re.S):
        endereco = urllib.parse.urljoin(base, m.group(1))
        titulo = re.sub(r"<[^>]+>", " ", m.group(2))
        titulo = re.sub(r"\s+", " ", titulo).strip()
        if endereco in vistos:
            continue
        if urllib.parse.urlparse(endereco).netloc != urllib.parse.urlparse(base).netloc:
            continue
        # link de materia tem caminho, titulo, e nao e menu
        caminho = urllib.parse.urlparse(endereco).path.strip("/")
        if len(caminho) < 12 or caminho.count("/") > 6:
            continue
        if len(titulo) < 18:
            continue
        vistos.add(endereco)
        saida.append((titulo, endereco))
    return saida[:60]


def _canal_do_handle(handle):
    """o YouTube so da feed por id de canal, entao resolve o arroba primeiro"""
    arroba = "@" + handle.lstrip("@")
    # a pagina do YouTube e enorme e o id do canal aparece la no fundo
    html = _abre("https://www.youtube.com/" + arroba + "/videos", teto=4000000)
    m = re.search(r'"(?:channelId|externalId)":"(UC[\w-]{20,})"', html)
    if m:
        return m.group(1)
    m = re.search(r'channel/(UC[\w-]{20,})', html)
    return m.group(1) if m else None


def _feed_do_canal(banca):
    canal = banca.get("canal")
    if not canal and banca.get("handle"):
        canal = _canal_do_handle(banca["handle"])
        if canal:
            banca["canal"] = canal
    if not canal:
        return None
    return "https://www.youtube.com/feeds/videos.xml?channel_id=" + canal


def carrega_visto():
    try:
        with open(VISTO, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"enderecos": [], "atualizado": ""}


def grava_visto(estado):
    # a memoria nao cresce para sempre, guarda os mil e duzentos mais recentes
    estado["enderecos"] = estado["enderecos"][-1200:]
    estado["atualizado"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(VISTO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=1)


def ronda(bancadas, limite_por_banca=25):
    """Passa em todas as bancadas e devolve o que ainda nao foi visto.

    Devolve (novidades, relatorio). Cada novidade tem titulo, endereco,
    bancada e editoria. O relatorio diz o que cada bancada rendeu, para
    aparecer no log do Actions quando alguma parar de responder.
    """
    estado = carrega_visto()
    conhecidos = set(estado["enderecos"])
    # bancada que o vigia nunca leu antes so aprende, senao ela despejaria o
    # arquivo inteiro dela no jornal no dia em que entrasse na lista
    ja_lidas = set(estado.get("bancadas", []))
    novidades, relatorio = [], []

    for banca in bancadas:
        nome = banca["nome"]
        try:
            if banca["tipo"] == "youtube":
                endereco = _feed_do_canal(banca)
                if not endereco:
                    relatorio.append((nome, "sem canal"))
                    continue
                itens = _do_feed(_abre(endereco))
            elif banca["tipo"] == "feed":
                itens = _do_feed(_abre(banca["url"]))
            else:
                itens = _do_indice(_abre(banca["url"]), banca["url"])
        except urllib.error.HTTPError as e:
            relatorio.append((nome, "HTTP %s" % e.code))
            continue
        except Exception as e:
            relatorio.append((nome, type(e).__name__))
            continue

        itens = itens[:limite_por_banca]
        estreia = nome not in ja_lidas
        ja_lidas.add(nome)
        so_disso = any(s in (banca.get("url") or banca.get("handle") or
                             banca.get("canal") or "") for s in SO_DISSO)
        achados = 0
        for titulo, endereco in itens:
            endereco = endereco.split("#")[0].strip()
            if not endereco.startswith("http"):
                continue
            if endereco in conhecidos:
                continue
            conhecidos.add(endereco)
            estado["enderecos"].append(endereco)
            if not so_disso and not ASSUNTO.search(titulo + " " + endereco):
                continue
            if estreia:
                continue
            achados += 1
            novidades.append(dict(titulo=titulo, endereco=endereco,
                                  bancada=nome, editoria=banca["editoria"]))
        relatorio.append((nome, ("estreia, so aprendendo, %d itens" % len(itens))
                          if estreia else ("%d de %d" % (achados, len(itens)))))
        # o Reddit devolve 429 quando a gente corre demais, entao ele espera mais
        time.sleep(4.0 if "reddit.com" in (banca.get("url") or "") else 0.6)

    estado["bancadas"] = sorted(ja_lidas)
    grava_visto(estado)
    return novidades, relatorio


if __name__ == "__main__":
    import bancadas
    novas, rel = ronda(bancadas.BANCADAS)
    for nome, estado in rel:
        print("%-30s %s" % (nome, estado))
    print("\nnovidades: %d" % len(novas))
    for n in novas[:40]:
        print(" [%s] %s\n     %s" % (n["bancada"], n["titulo"][:90], n["endereco"]))
