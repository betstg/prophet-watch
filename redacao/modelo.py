"""A conversa com o modelo, num lugar so.

Trocar de fornecedor depois e mexer aqui e em mais lugar nenhum. Hoje e o
Gemini, pela faixa gratuita, sem cartao. O Groq entra do lado sem reescrever
reporter, checador nem editor.
"""

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request

CHAVE = os.environ.get("GEMINI_API_KEY", "").strip()
RAIZ = "https://generativelanguage.googleapis.com/v1beta"

# tenta nesta ordem e fica com o primeiro que o Google aceitar. Assim uma
# troca de nome de modelo la fora nao derruba a redacao aqui.
CANDIDATOS = [
    os.environ.get("MODELO", "").strip(),
    "gemini-3-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]
_ESCOLHIDO = None
_MORTOS = set()
NOTAS = []          # o que aconteceu na escolha do modelo, para o relatorio


class SemModelo(Exception):
    pass


def _post(caminho, corpo, tempo=120):
    dados = json.dumps(corpo).encode("utf-8")
    pedido = urllib.request.Request(
        RAIZ + caminho + "?key=" + urllib.parse.quote(CHAVE),
        data=dados, headers={"Content-Type": "application/json"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(pedido, timeout=tempo, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


import urllib.parse  # noqa: E402  (fica aqui embaixo por causa do _post)


def modelos_disponiveis():
    try:
        pedido = urllib.request.Request(
            RAIZ + "/models?key=" + urllib.parse.quote(CHAVE))
        with urllib.request.urlopen(pedido, timeout=30,
                                    context=ssl.create_default_context()) as r:
            d = json.loads(r.read().decode("utf-8"))
        return [m["name"].split("/")[-1] for m in d.get("models", [])]
    except Exception:
        return []


def _escolhe():
    """Escolhe o modelo e conta em voz alta o que a conta oferece."""
    global _ESCOLHIDO
    if _ESCOLHIDO and _ESCOLHIDO not in _MORTOS:
        return _ESCOLHIDO
    if not CHAVE:
        raise SemModelo("falta a chave. Guarde GEMINI_API_KEY nos segredos do repositorio.")

    tem = [m for m in modelos_disponiveis() if m not in _MORTOS]
    if not NOTAS:
        NOTAS.append("a conta oferece %d modelos, %s"
                     % (len(tem), ", ".join(tem[:14]) if tem else "a listagem nao respondeu"))

    # primeiro os candidatos que a conta confirma que existem
    for nome in CANDIDATOS:
        if nome and nome in tem:
            _ESCOLHIDO = nome
            NOTAS.append("usando %s" % nome)
            return nome
    # depois qualquer flash que a conta tenha
    flash = [m for m in tem if "flash" in m and "thinking" not in m and "image" not in m
             and "tts" not in m and "live" not in m]
    if flash:
        _ESCOLHIDO = sorted(flash)[-1]
        NOTAS.append("nenhum candidato bateu, usando %s" % _ESCOLHIDO)
        return _ESCOLHIDO
    # por ultimo, tenta o candidato no escuro, porque a listagem pode ter falhado
    for nome in CANDIDATOS:
        if nome and nome not in _MORTOS:
            _ESCOLHIDO = nome
            NOTAS.append("a listagem nao ajudou, tentando %s no escuro" % nome)
            return nome
    raise SemModelo("nenhum modelo utilizavel. A conta ve estes, "
                    + (", ".join(sorted(tem)[:14]) or "nenhum"))


def pergunta(instrucao, texto, json_esperado=True, tentativas=3, teto_saida=4000):
    """Manda uma tarefa e devolve a resposta, ja como objeto quando e json."""
    modelo = _escolhe()
    corpo = {
        "systemInstruction": {"parts": [{"text": instrucao}]},
        "contents": [{"role": "user", "parts": [{"text": texto}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": teto_saida,
        },
    }
    if json_esperado:
        corpo["generationConfig"]["responseMimeType"] = "application/json"

    espera = 4
    for volta in range(tentativas + 2):
        try:
            resposta = _post("/models/%s:generateContent" % modelo, corpo)
            partes = resposta["candidates"][0]["content"]["parts"]
            bruto = "".join(p.get("text", "") for p in partes).strip()
        except urllib.error.HTTPError as e:
            codigo = e.code
            if codigo in (429, 500, 503) and volta < tentativas - 1:
                time.sleep(espera)
                espera *= 2
                continue
            detalhe = ""
            try:
                detalhe = e.read().decode("utf-8", "replace")[:400]
            except Exception:
                pass
            if codigo in (400, 403, 404):
                # esse modelo nao serve para essa chave. Marca como morto e
                # tenta o proximo, em vez de derrubar a rodada inteira.
                _MORTOS.add(modelo)
                NOTAS.append("%s recusou com HTTP %s, %s" % (modelo, codigo, detalhe[:160]))
                try:
                    modelo = _escolhe()
                except SemModelo:
                    raise SemModelo("todos os modelos recusaram. %s" % " | ".join(NOTAS[-3:]))
                corpo_novo = dict(corpo)
                corpo = corpo_novo
                continue
            raise SemModelo("o modelo respondeu HTTP %s. %s" % (codigo, detalhe))
        except (KeyError, IndexError):
            if volta < tentativas - 1:
                time.sleep(espera)
                continue
            return None

        if not json_esperado:
            return bruto
        try:
            return json.loads(bruto)
        except json.JSONDecodeError:
            m = re.search(r"[\[{].*[\]}]", bruto, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    pass
            if volta < tentativas - 1:
                time.sleep(2)
                continue
            return None
    return None


# ---- a regra de pontuacao da Betty, aplicada na marra ----
# Nenhum modelo obedece isso sempre. Entao o texto passa por aqui antes de
# entrar no jornal, e o que escapou e consertado sem pedir licenca.
def limpa(texto):
    if not texto:
        return texto
    t = texto.replace("—", ",").replace("–", ",")
    t = re.sub(r"\s+[-]\s+", ", ", t)          # traco usado como pausa
    t = re.sub(r"\s*;\s*", ". ", t)            # ponto e virgula vira ponto
    t = re.sub(r"\s*:\s*", ", ", t)            # dois pontos vira virgula
    t = re.sub(r",\s*,", ",", t)
    t = re.sub(r"\s+([.,])", r"\1", t)
    t = re.sub(r"\.\s*\.", ".", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    # o ponto que nasceu de um ponto e virgula deixa a frase seguinte minuscula
    t = re.sub(r"([.!?]\s+)([a-zà-ÿ])", lambda m: m.group(1) + m.group(2).upper(), t)
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t


def sujo(texto):
    return bool(texto) and bool(re.search(r"[;:—–]|\s-\s", texto))
