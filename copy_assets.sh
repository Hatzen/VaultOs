#!/vendor/bin/sh

# Pfade definieren
DEST_DIR="/data/media/0/Android/media/org.kiwix.kiwixmobile"
ZIM_FILE="anonymousplanet.org_en_all_2026-05.zim"

# Warten, bis der interne Speicher (/data) vollständig entschlüsselt und gemountet ist
while [ ! -d "/data/media/0" ]; do
    sleep 2
done

# Prüfen, ob die Datei bereits existiert (verhindert mehrmaliges Kopieren bei jedem Boot)
if [ ! -f "$DEST_DIR/$ZIM_FILE" ]; then
    mkdir -p "$DEST_DIR"
    chmod 0771 "$DEST_DIR"
    
    # Kopieren im Hintergrund-Prozess mit niedriger CPU-Priorität (ionice)
    ionice -c 3 cp "/product/media/kiwix/$ZIM_FILE" "$DEST_DIR/$ZIM_FILE"
    
    # Berechtigungen setzen
    chown -R 1023:1023 "/data/media/0/Android/media/org.kiwix.kiwixmobile" # 1023 = media_rw
    chmod 0664 "$DEST_DIR/$ZIM_FILE"
fi
