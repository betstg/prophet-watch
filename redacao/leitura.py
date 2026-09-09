"""Ler uma pagina e entregar so o que interessa.

O modelo nao precisa do menu, do rodape nem do banner de cookie. Ele precisa
do texto da materia, da data e das fotos. Cortar aqui e o que faz a conta
caber na faixa gratuita.
"""

import re
import ssl
import urllib.parse
import urllib.request

NAVEGADOR = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")

LIXO = re.compile(r"<(script|style|nav|footer|header|aside|form|svg|noscript)\b.*?</\1>",
                  re.I | re.S)

# fotos que nunca sao a materia
FOTO_LIXO = re.compile(r"logo|avatar|icon|sprite|placeholder|1x1|pixel|badge|"
                       r"share|gravatar|amp-|advert|sponsor", re.I)


def busca(url, teto=900000, tempo=25):
    pedido = urllib.request.Request(url, headers={
        "User-Agent": NAVEGADOR,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en,pt;q=0.8",
    })
    with urllib.request.urlopen(pedido, timeout=tempo,
                                context=ssl.create_default_context()) as r:
        return r.read(teto).decode("utf-8", "replace")


def _meta(html, chaves):
    for chave in chaves:
        m = re.search(
            r'<meta[^>]+(?:property|name|itemprop)=["\']%s["\'][^>]*content=["\']([^"\']+)'
            % re.escape(chave), html, re.I)
        if m:
            return m.group(1).strip()
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name|itemprop)=["\']%s["\']'
            % re.escape(chave), html, re.I)
        if m:
            return m.group(1).strip()
    return ""


def _fotos(html, base):
    saida, vistas = [], set()
    og = _meta(html, ["og:image", "twitter:image", "og:image:secure_url"])
    if og:
        saida.append(urllib.parse.urljoin(base, og))
        vistas.add(saida[0])
    for m in re.finditer(r"<img\b[^>]*>", html, re.I):
        tag = m.group(0)
        src = re.search(r'(?:data-src|data-original|src)=["\']([^"\']+)', tag, re.I)
        if not src:
            continue
        endereco = urllib.parse.urljoin(base, src.group(1))
        if endereco in vistas or FOTO_LIXO.search(endereco):
            continue
        larg = re.search(r'width=["\']?(\d+)', tag, re.I)
        if larg and int(larg.group(1)) < 320:
            continue
        alt = re.search(r'alt=["\']([^"\']{0,140})', tag, re.I)
        vistas.add(endereco)
        saida.append(endereco if not alt else endereco + " || " + alt.group(1))
        if len(saida) >= 12:
            break
    return saida


def _video(html):
    for pad in (r"youtube(?:-nocookie)?\.com/embed/([\w-]{11})",
                r"youtu\.be/([\w-]{11})",
                r"youtube\.com/watch\?v=([\w-]{11})"):
        m = re.search(pad, html)
        if m:
            return m.group(1)
    return ""


def _data(html):
    return _meta(html, ["article:published_time", "datePublished",
                        "publishdate", "date", "DC.date.issued",
                        "og:published_time", "article:modified_time"])


def _corpo(html, teto=6000):
    t = LIXO.sub(" ", html)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = (t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8217;", "'")
          .replace("&quot;", '"').replace("&#039;", "'").replace("&rsquo;", "'")
          .replace("&ldquo;", '"').replace("&rdquo;", '"').replace("&#8211;", ","))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:teto]


def pagina(url):
    """Devolve o dossie de uma materia, pronto para o modelo ler."""
    html = busca(url)
    return dict(
        url=url,
        titulo=_meta(html, ["og:title", "twitter:title"]) or (
            (re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S) or
             [None, ""])[1].strip()[:220]),
        data_declarada=_data(html),
        corpo=_corpo(html),
        fotos=_fotos(html, url),
        video=_video(html),
        veiculo=urllib.parse.urlparse(url).netloc.replace("www.", ""),
    )
