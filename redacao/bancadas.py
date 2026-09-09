"""As bancadas, quem o jornal le todo dia.

Cada bancada tem um apelido, o endereco do feed quando existe, a pagina de
indice para quem nao tem feed, e a editoria do reporter que cuida dela.
O vigia le isso, nao a inteligencia. Ler e de graca.
"""

# editorias, uma por reporter
SERIE = "serie"
TELA = "tela"
JOGOS = "jogos"
PARQUES = "parques"
PALCO = "palco"
BRASIL = "brasil"
ESTUDO = "estudo"

BANCADAS = [
    # ---- oficial ----
    dict(nome="Wizarding World", editoria=SERIE, tipo="indice",
         url="https://www.harrypotter.com/news"),
    dict(nome="WBD Pressroom", editoria=SERIE, tipo="indice",
         url="https://press.wbd.com/us/property/harry-potter/media-releases"),
    dict(nome="Harry Potter no YouTube", editoria=SERIE, tipo="youtube",
         handle="@harrypotter", canal="UChPRO1CB_Hvd0TvKRU62iSQ"),

    # ---- imprensa ----
    dict(nome="Variety", editoria=TELA, tipo="feed",
         url="https://variety.com/t/harry-potter/feed/"),
    dict(nome="Deadline", editoria=TELA, tipo="feed",
         url="https://deadline.com/tag/harry-potter/feed/"),
    dict(nome="The Hollywood Reporter", editoria=TELA, tipo="feed",
         url="https://www.hollywoodreporter.com/t/harry-potter/feed/"),
    dict(nome="TVLine", editoria=TELA, tipo="feed",
         url="https://www.tvline.com/feed/"),
    dict(nome="ScreenRant", editoria=TELA, tipo="feed",
         url="https://screenrant.com/feed/"),
    dict(nome="Collider", editoria=TELA, tipo="feed",
         url="https://collider.com/feed/"),

    # ---- fa em portugues, a camada que a Betty pediu ----
    dict(nome="Potterish", editoria=BRASIL, tipo="feed",
         url="https://potterish.com/feed/"),
    dict(nome="Ordem da Fenix Brasileira", editoria=BRASIL, tipo="feed",
         url="https://www.ordemdafenixbrasileira.com/feeds/posts/default?alt=rss"),
    dict(nome="Mundo Bruxo", editoria=BRASIL, tipo="feed",
         url="https://mundobruxo.com.br/feed/"),
    dict(nome="Caldeirao Furado", editoria=BRASIL, tipo="youtube",
         canal="UCkhfuyQUD5GNulpQRJOqrGg"),
    dict(nome="Observatorio Potter", editoria=BRASIL, tipo="youtube",
         handle="@observpotter", canal="UCHhvVVo562d4zx-rEnwnV7w"),
    dict(nome="Wizarding Bruno", editoria=BRASIL, tipo="youtube",
         handle="@WizardingBruno", canal="UCe974dgFmXBLdllq7UlwcHg"),
    dict(nome="O Expresso de Hogwarts", editoria=BRASIL, tipo="youtube",
         handle="@OExpressodeHogwarts", canal="UCBtgk9ifEsJBpADAwvtnGEQ"),

    # ---- fa em ingles ----
    dict(nome="The Leaky Cauldron", editoria=SERIE, tipo="indice",
         url="https://www.the-leaky-cauldron.org/"),
    dict(nome="MuggleNet", editoria=SERIE, tipo="feed",
         url="https://mugglenet.com/feed/"),
    dict(nome="Wizarding World Direct", editoria=SERIE, tipo="feed",
         url="https://wizardingworlddirect.com/feed/"),
    dict(nome="SnitchSeeker", editoria=PALCO, tipo="indice",
         url="https://www.snitchseeker.com/harry-potter-news/"),
    dict(nome="Harry Potter Theory", editoria=ESTUDO, tipo="youtube",
         handle="@HarryPotterTheory", canal="UCVqoigIqNacy9xMnEDZzN_Q"),

    # ---- estudo do livro e teoria ----
    dict(nome="Hogwarts Professor", editoria=ESTUDO, tipo="feed",
         url="https://www.hogwartsprofessor.com/feed/"),
    dict(nome="HP Lexicon", editoria=ESTUDO, tipo="feed",
         url="https://www.hp-lexicon.org/feed/"),
    dict(nome="The Rowling Library", editoria=ESTUDO, tipo="indice",
         url="https://www.therowlinglibrary.com/category/news/"),
    dict(nome="Critical Magic Theory", editoria=ESTUDO, tipo="indice",
         url="https://www.criticalmagictheory.com/"),
    dict(nome="MuggleCast", editoria=ESTUDO, tipo="feed",
         url="https://www.mugglecast.com/feed/"),
    dict(nome="Super Carlin Brothers", editoria=ESTUDO, tipo="youtube",
         handle="@SuperCarlinBrothers", canal="UCKZo4N0lVPccBkSiuyVh4yg"),

    # ---- bastidores, vazamento e set ----
    dict(nome="r/HarryPotteronHBO", editoria=SERIE, tipo="feed",
         url="https://www.reddit.com/r/HarryPotteronHBO/new/.rss"),
    dict(nome="r/harrypotter", editoria=SERIE, tipo="feed",
         url="https://www.reddit.com/r/harrypotter/new/.rss"),
    dict(nome="Watford Observer", editoria=SERIE, tipo="feed",
         url="https://www.watfordobserver.co.uk/news/rss/"),
    dict(nome="Soap Central", editoria=SERIE, tipo="indice",
         url="https://www.soapcentral.com/shows/harry-potter"),

    # ---- jogos ----
    dict(nome="GamingBible", editoria=JOGOS, tipo="indice",
         url="https://www.gamingbible.com/news/tv-and-film/harry-potter"),
    dict(nome="GamesRadar", editoria=JOGOS, tipo="feed",
         url="https://www.gamesradar.com/feeds/tag/harry-potter/"),
    dict(nome="r/HarryPotterGame", editoria=JOGOS, tipo="feed",
         url="https://www.reddit.com/r/HarryPotterGame/new/.rss"),

    # ---- parques, loja e palco ----
    dict(nome="Blooloop", editoria=PARQUES, tipo="feed",
         url="https://blooloop.com/feed/"),
    dict(nome="Attractions Magazine", editoria=PARQUES, tipo="feed",
         url="https://attractionsmagazine.com/feed/"),
    dict(nome="WhatsOnStage", editoria=PALCO, tipo="feed",
         url="https://www.whatsonstage.com/feed/"),
    dict(nome="Playbill", editoria=PALCO, tipo="feed",
         url="https://playbill.com/rss/news"),
    dict(nome="The Potter Collector", editoria=ESTUDO, tipo="youtube",
         handle="@thepottercollector", canal="UCvoVMyyL84ywUykEMn862Gg"),
    dict(nome="Harry Potter Exhibition", editoria=PARQUES, tipo="indice",
         url="https://www.harrypotterexhibition.com/press"),
]

# fontes que nunca sustentam uma materia sozinhas
FONTE_FRACA = {
    "mugglenet.com",        # virou veiculo promocional depois de 2025
    "insidethemagic.net",
    "thetab.com",
    "reddit.com",
    "x.com",
    "twitter.com",
}

def por_editoria():
    d = {}
    for b in BANCADAS:
        d.setdefault(b["editoria"], []).append(b)
    return d
