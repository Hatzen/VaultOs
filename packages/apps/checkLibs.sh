#!/bin/bash

# Pfad zu aapt aus den Android Host-Tools ermitteln
AAPT_TOOL="../../../../../out/host/linux-x86/bin/aapt"

# Falls das Tool nicht gebaut ist, das globale System-aapt als Fallback nutzen
if [ ! -f "$AAPT_TOOL" ]; then
    AAPT_TOOL="aapt"
fi

echo "========================================= "
echo " Scanne APKs für <uses-library> Einträge  "
echo "========================================= "

# Rekursiv nach allen APKs im aktuellen Verzeichnis suchen
find . -type f -name "*.apk" | while read -r apk; do
    echo ""
    echo "Prüfe APK: $apk"
    
    # Extrahiere benötigte (required) Bibliotheken
    req_libs=$($AAPT_TOOL dump badging "$apk" 2>/dev/null | grep "uses-library:" | sed "s/uses-library:'//;s/'//")
    # Extrahiere optionale (optional) Bibliotheken
    opt_libs=$($AAPT_TOOL dump badging "$apk" 2>/dev/null | grep "uses-library-not-required:" | sed "s/uses-library-not-required:'//;s/'//")
    
    # Ausgabe für Android.bp formatieren
    echo "--> Für Android.bp eintragen:"
    if [ -n "$req_libs" ]; then
        # Formatieren als kommagetrennte Liste in Anführungszeichen
        bp_req=$(echo "$req_libs" | tr '\n' ' ' | sed "s/ /\", \"/g;s/\", \"$/\"/;s/^/\"/")
        echo "    uses_libs: [$bp_req],"
    else
        echo "    uses_libs: [],"
    fi
    
    if [ -n "$opt_libs" ]; then
        bp_opt=$(echo "$opt_libs" | tr '\n' ' ' | sed "s/ /\", \"/g;s/\", \"$/\"/;s/^/\"/")
        echo "    optional_uses_libs: [$bp_opt],"
    else
        echo "    optional_uses_libs: [],"
    fi
    echo "-----------------------------------------"
done
