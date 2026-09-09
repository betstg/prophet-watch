#!/usr/bin/env python3
"""A redacao inteira, do vigia ao fechamento da edicao.

Ordem do dia.
1. O vigia passa nas quarenta bancadas e separa o que e novo. Sem IA.
2. Os reporteres olham os titulos da area deles e dizem o que vale abrir.
3. O checador abre cada um e reprova o que nao se sustenta.
4. O editor escreve manchete e resumo e fecha a edicao.
5. As fotos entram, o jornal e remontado e o commit sai.

Roda no GitHub Actions. Nao depende de maquina nenhuma da Betty.
"""

import datetime
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import bancadas          # noqa: E402
import checador          # noqa: E402
import editor            # noqa: E402
import fotos             # noqa: E402
import modelo            # noqa: E402
import reporter          # noqa: E402
import vigia             # noqa: E402

PAGINA = os.path.join(RAIZ, "index.html")
JANELA = 4          # quantos dias para tras uma materia ainda e nova
TETO_EDICAO = 6     # quantas materias no maximo por rodada


LINHAS = []
DESFECHO = ["a rodada terminou sem dizer o motivo, isso e defeito da redacao"]


def diz(*a):
    texto = " ".join(str(x) for x in a)
    LINHAS.append(texto)
    print(texto, flush=True)


def fecha_relatorio(desfecho):
    """Escreve o que aconteceu num lugar legivel sem abrir log de Actions."""
    import io
    corpo = ("# Ultima rodada da redacao\n\n"
             "**Desfecho**, %s\n\n"
             "**Quando**, %s\n\n```\n%s\n```\n"
             % (desfecho,
                datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC"),
                "\n".join(LINHAS)[-14000:]))
    if os.environ.get("GITHUB_ACTIONS"):
        with io.open(os.path.join(AQUI, "ultima-rodada.md"), "w", encoding="utf-8") as f:
            f.write(corpo)
    resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumo:
        with io.open(resumo, "a", encoding="utf-8") as f:
            f.write(corpo)


def ja_publicado():
    with open(PAGINA, encoding="utf-8") as f:
        pagina = f.read()
    bloco = re.search(r'id="news-data">(.*?)</script>', pagina, re.S)
    dados = json.loads(bloco.group(1))
    ids = [s["id"] for s in dados["stories"]]
    manchetes = [s["headline"] for s in dados["stories"]]
    enderecos = {s.get("url", "") for s in dados["stories"]}
    return ids, manchetes, enderecos


def nome_bonito(dominio):
    for b in bancadas.BANCADAS:
        alvo = b.get("url") or ""
        if alvo and dominio.split(".")[0] in alvo:
            return b["nome"]
    partes = dominio.replace(".com", "").replace(".co.uk", "").replace(".net", "")
    return partes.replace(".", " ").replace("-", " ").title()


def _corpo():
    hoje = datetime.date.today()
    ate = hoje.isoformat()
    desde = (hoje - datetime.timedelta(days=JANELA)).isoformat()
    diz("Prophet Watch, redacao de %s. Janela de %s ate %s." % (ate, desde, ate))

    ids, manchetes, enderecos = ja_publicado()
    diz("Ja no jornal, %d materias." % len(ids))
    diz("Chave do modelo, %s." % ("presente" if modelo.CHAVE else "AUSENTE"))

    diz("\n== VIGIA ==")
    novidades, relatorio = vigia.ronda(bancadas.BANCADAS)
    for nome, estado in relatorio:
        diz("  %-30s %s" % (nome, estado))
    novidades = [n for n in novidades if n["endereco"] not in enderecos]
    diz("Novidades para olhar, %d." % len(novidades))
    if not novidades:
        DESFECHO[0] = "nada novo nas bancadas"
        diz("\nNada novo nas bancadas. A edicao de hoje fica como esta.")
        return 0

    if not modelo.CHAVE:
        DESFECHO[0] = "falta a chave do modelo"
        diz("\nO vigia achou coisa nova, mas falta a chave do modelo.")
        diz("Guarde GEMINI_API_KEY nos segredos do repositorio.")
        return 1

    diz("\n== MODELO ==")
    try:
        diz("  " + modelo._escolhe())
    except modelo.SemModelo as e:
        DESFECHO[0] = "o modelo nao pode ser escolhido, %s" % e
        diz("  PAROU AQUI, %s" % e)
        for n in modelo.NOTAS:
            diz("  nota, %s" % n)
        return 1
    for n in modelo.NOTAS:
        diz("  nota, %s" % n)

    diz("\n== REPORTERES ==")
    por_area = {}
    for n in novidades:
        por_area.setdefault(n["editoria"], []).append(n)
    candidatos = []
    for area, lista in sorted(por_area.items()):
        try:
            escolhidos = reporter.pauta(area, lista)
        except modelo.SemModelo as e:
            DESFECHO[0] = "o modelo nao respondeu, %s" % e
            diz("  PAROU AQUI, %s" % e)
            for n in modelo.NOTAS:
                diz("  nota, %s" % n)
            return 1
        diz("  %-9s olhou %2d titulos, quer abrir %d" % (area, len(lista), len(escolhidos)))
        for c in escolhidos:
            diz("      %s" % c["endereco"])
        candidatos.extend(escolhidos)

    if not candidatos:
        DESFECHO[0] = "os reporteres viram %d titulos e nenhum valia abrir" % len(novidades)
        diz("\nOs reporteres nao acharam nada que valesse abrir.")
        return 0

    diz("\n== CHECAGEM ==")
    aprovadas = []
    for c in candidatos[:14]:
        v = checador.checa(c, desde, ate)
        if v.get("reprovada"):
            diz("  reprovada, %-42s %s" % (v["reprovada"][:42], c["endereco"][:70]))
            continue
        diz("  passou,    %-10s %-22s %s" % (v["data"], v["veiculo"][:22], v["titulo"][:60]))
        aprovadas.append(v)

    # a regra das duas fontes. Veiculo fraco so entra se outro contar o mesmo.
    firmes = []
    for a in aprovadas:
        if not a["fonte_fraca"]:
            firmes.append(a)
            continue
        outros = [o for o in aprovadas if o is not a and not o["fonte_fraca"]
                  and o["assunto"][:24].lower() == a["assunto"][:24].lower()]
        if outros:
            firmes.append(a)
        else:
            diz("  fora,      fonte unica e fraca, %s" % a["veiculo"])
    aprovadas = firmes[:TETO_EDICAO]

    if not aprovadas:
        DESFECHO[0] = "%d materias abertas e nenhuma passou na checagem" % len(candidatos[:14])
        diz("\nNada passou na checagem. A edicao de hoje fica como esta.")
        return 0

    diz("\n== EDITOR ==")
    prontas = editor.fecha(aprovadas, manchetes)
    prontas = [p for p in prontas if p["id"] not in ids]
    if not prontas:
        DESFECHO[0] = "o editor nao aproveitou nenhuma das aprovadas"
        diz("O editor nao aproveitou nenhuma.")
        return 0

    diz("\n== FOTOS ==")
    saida = []
    for p in prontas:
        caminho = fotos.guarda(p.pop("_foto", ""), p["id"], RAIZ)
        legenda = p.pop("_legenda", "")
        video = p.pop("_video", "")
        if caminho:
            p["image"] = caminho
            if legenda:
                p["imagemIlustrativa"] = legenda
            diz("  %s, foto ok" % p["id"])
        else:
            diz("  %s, sem foto, a pagina desenha a chapa" % p["id"])
        if video:
            p["video"] = video
        p["source"] = nome_bonito(p["source"])
        saida.append(p)

    caminho_json = os.path.join(AQUI, "novas.json")
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    diz("\n== FECHAMENTO ==")
    for etapa in (["python3", "add-news.py", "index.html", caminho_json, ate],
                  ["python3", "build-artifact.py", "index.html", "artifact.html"]):
        r = subprocess.run(etapa, cwd=RAIZ, capture_output=True, text=True)
        diz(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
        if r.returncode:
            diz("FALHOU, %s" % r.stderr.strip()[:500])
            return 1

    DESFECHO[0] = "edicao fechada com %d materias novas" % len(saida)
    diz("\nEdicao fechada com %d materias novas." % len(saida))
    for p in saida:
        diz("  [%s] %s" % (p["status"], p["headline"]))
    return 0


def main():
    try:
        codigo = _corpo()
        desfecho = DESFECHO[0]
    except modelo.SemModelo as e:
        diz("\nPAROU, %s" % e)
        codigo, desfecho = 1, "parou, %s" % e
    except Exception as e:
        diz("\nQUEBROU, %s, %s" % (type(e).__name__, e))
        codigo, desfecho = 1, "quebrou, %s" % type(e).__name__
    fecha_relatorio(desfecho)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
