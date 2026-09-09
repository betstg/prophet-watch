"""Baixa a foto, corta no tamanho do jornal e guarda nas duas medidas."""

import os
import ssl
import urllib.request

from PIL import Image

NAVEGADOR = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# a foto do castelo ja ficou em oito materias ao mesmo tempo. Nunca mais.
PROIBIDA = "hogwarts-night"


def guarda(url, ident, raiz):
    """Devolve o caminho relativo da foto, ou vazio quando nao deu."""
    if not url or PROIBIDA in url:
        return ""
    grande = os.path.join(raiz, "assets", "thumbs", ident + ".jpg")
    pequena = os.path.join(raiz, "assets", "thumbs", "small", ident + ".jpg")
    os.makedirs(os.path.dirname(grande), exist_ok=True)
    os.makedirs(os.path.dirname(pequena), exist_ok=True)
    try:
        pedido = urllib.request.Request(url, headers={"User-Agent": NAVEGADOR})
        with urllib.request.urlopen(pedido, timeout=30,
                                    context=ssl.create_default_context()) as r:
            bruto = r.read(12000000)
        if len(bruto) < 6000:
            return ""
        with open(grande, "wb") as f:
            f.write(bruto)
        im = Image.open(grande)
        im.load()
        if im.width < 380 or im.height < 220:
            os.remove(grande)
            return ""
        im = im.convert("RGB")
        if im.width > 900:
            im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
        im.save(grande, "JPEG", quality=76, optimize=True, progressive=True)
        im = Image.open(grande)
        im.resize((380, round(im.height * 380 / im.width)),
                  Image.LANCZOS).save(pequena, "JPEG", quality=58, optimize=True)
        return "assets/thumbs/%s.jpg" % ident
    except Exception:
        for caminho in (grande, pequena):
            try:
                os.remove(caminho)
            except OSError:
                pass
        return ""
