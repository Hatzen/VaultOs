LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := Parannoying
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := app-prod-release.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)

# Der Trick: Wir setzen das Zertifikat explizit auf 'PRESIGNED' 
# und verbieten dem Bausystem, die App während des Builds zu manipulieren
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := true

LOCAL_PRODUCT_MODULE := true

# Deaktiviert Dex-Optimierungen und Entpacken, da die App bereits fertig ist
LOCAL_UNCOMPRESS_DEX := false
LOCAL_DEX_PREOPT := false
LOCAL_ENFORCE_USES_LIBRARIES := false

include $(BUILD_PREBUILT)