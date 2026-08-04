# TODOs

Das ist die perfekte Weiterentwicklung für das Konzept! Wenn das Gerät sowieso keinen Internetzugang hat, wird es durch ein integriertes Offline-Ökosystem erst recht zum ultimativen „Digitalen Überlebens-Kit“ (oder wie man es bei SHIFT nennen könnte: ShiftOS-Vault).
Hier sind die besten Open-Source-Anwendungen, die genau für dieses Szenario gebaut wurden und dem System massiven Nutzwert verleihen:
## 1. Das „Wissen der Menschheit“ (Wikipedia & Lexika)

* Kiwix (Offline-Reader): Die absolute Nummer 1 für dieses Projekt. Kiwix erlaubt es, ganze ZIM-Dateien offline zu lesen.
* Der Content: Du kannst die komplette Wikipedia (komprimiert ohne Bilder ca. 12 GB, mit Bildern ca. 100 GB), das Wiktionary, medizinische Enzyklopädien (MDWiki) oder die Wikivoyage-Reiseführer direkt in die Systempartition integrieren.
* GitHub/Source: [Kiwix Android](https://github.com/kiwix/kiwix-android) [1, 2] 

## 2. Navigation & Überleben (Offline-Karten & Tools)

* Organic Maps / OsmAnd: Beide basieren auf OpenStreetMap. Organic Maps ist extrem schnell, schlank und komplett für den reinen Offline-Betrieb optimiert (inklusive Offline-Routenplanung für Fußgänger/Fahrräder). [3, 4, 5, 6, 7] 
* Trail Sense: Das ultimative Prepper-Werkzeug. Es nutzt die internen Sensoren des SHIFTphone 8 (Kompass, Barometer, Gyroskop) und bietet einen Kompass, Wettervorhersage anhand des Luftdrucks, Schrittzähler, Sonnenuhr und ein Alarmsystem für Stürme – komplett offline. [8] 
* GitHub/Source: [Organic Maps](https://github.com/organicmaps/organicmaps) & [Trail Sense](https://github.com/kylecorry31/Trail-Sense)

## 3. Produktivität & Dokumente (Prepper Guides)

* Collabora Office / LibreOffice Viewer: Damit der Nutzer Prepper-Guides (PDFs, Word-Dokumente, Excel-Tabellen für Inventuren) direkt öffnen kann.
* Logseq / Markor: Leistungsstarke, text- und Markdown-basierte Notizen-Apps. Sie speichern Daten in einfachen Textdateien auf dem Gerät, perfekt für Krisen-Tagebücher oder Notfallpläne. [9, 10, 11] 
* GitHub/Source: [Markor](https://github.com/gsantner/markor)

## 4. Werkzeuge & Medien

* Secure Tasks / Simple Tools: Nutze die "Simple Mobile Tools"-Reihe (Rechner, Kalender, Taschenlampe). Sie sind extrem schlank und haben keinerlei Tracker.
* VLC Media Player: Um Offline-Überlebensvideos, Audio-Guides oder Musik abzuspielen. Er bringt alle Codecs direkt mit.
* GitHub/Source: [Simple Tools](https://github.com/SimpleMobileTools) [12] 

## 5. Unterhaltung (Klassische Offline-Spiele)

* Lichess (Offline-Modus): Das gesamte Schachspiel als Open Source. Man kann perfekt gegen eine lokale Engine (Stockfish) spielen.
* Shattered Pixel Dungeon: Ein fantastisches, quelloffenes, rundenbasiertes RPG-Spiel. Es hat einen extrem hohen Wiederspielwert und benötigt null Internet.
* GitHub/Source: [Shattered Pixel Dungeon](https://github.com/00-Evan/shattered-pixel-dungeon) [13] 

------------------------------
## Wie du diese Apps (inklusive Daten) ins Image brennst
Da einige dieser Daten (Karten, Wikipedia-Pakete) sehr groß sind, integrierst du die Apps als System-Apps (wie oben beschrieben), legst aber die dazugehörigen Mediendateien in den Standard-User-Speicher (/sdcard/ bzw. Storage/Emulated/0/), damit die Apps sie beim ersten Booten sofort finden.
Dazu nutzt du im Android-Quellcode den Ordner device/shift/otter/rootdir/etc/ oder das PRODUCT_COPY_FILES-Makro in deiner device.mk:

# Kopiert eine vorab heruntergeladene Wikipedia-ZIM-Datei direkt auf das Telefon
PRODUCT_COPY_FILES += \
    vendor/shift/assets/wikipedia_de_all.zim:data/media/0/Kiwix/wikipedia_de_all.zim \
    vendor/shift/assets/germany_offline_map.mwm:data/media/0/MapsWithMe/germany.mwm

## Der finale "Wow-Effekt" bei der Präsentation
Stell dir vor, du übergibst das SHIFTphone 8 beim Bewerbungsgespräch. Es hat kein WLAN, keine SIM-Karte. Du drückst den Custom-Key, liest einen Text per KI, öffnest parallel die weltweite Offline-Karte und suchst auf einer lokalen Kopie der Wikipedia nach Überlebensstrategien – alles flüssig, autark und unhackbar. Das beweist nicht nur technisches Können, sondern ein tiefes Verständnis für das Produkt und die Zielgruppe von SHIFT.
Soll ich dir zeigen, wie du für diese vorinstallierten Apps die Standard-Pfade und Berechtigungen im Android-Manifest fest verdrahtest, damit der Nutzer nach dem Einschalten sofort loslegen kann?
