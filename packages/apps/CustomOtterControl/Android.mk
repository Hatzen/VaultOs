LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := CustomOtterControl
LOCAL_MODULE_TAGS := optional
# TIPP: Benenne das APK vor dem Build um, damit "debug" nicht im Namen steht
LOCAL_SRC_FILES := app-debug.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)

# 1. Signiert das APK mit dem exakten Zertifikat deines LineageOS-Builds.
# Dadurch erhält die App die Berechtigungsebene "signature".
LOCAL_CERTIFICATE := platform

# 2. Verschiebt die App nach /system/priv-app/ statt /system/app/.
# Zwingend notwendig für "signatureOrSystem" Berechtigungen (wie Factory Reset).
LOCAL_PRIVILEGED_MODULE := true

# 3. Verhindert, dass das System versucht, das APK im Voraus zu optimieren (Dexpreopt),
# was bei Debug-Builds oft zu Kompilierungsfehlern beim OS-Build führt.
LOCAL_DEX_PREOPT := false

# DIESE ZEILE HINZUFÜGEN: Zwingt die App auf die /product Partition; Same partition like privapp-permissions-otter.xml
LOCAL_PRODUCT_MODULE := true

include $(BUILD_PREBUILT)