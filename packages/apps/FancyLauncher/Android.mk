LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := FancyLauncher
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := fr.neamar.kiss_224.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
# WICHTIG: Erhält die Originalsignatur, damit die App als normaler 
# Launcher erkannt wird und im Play Store aktualisierbar bleibt.
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_PRIVILEGED_MODULE := true
LOCAL_PRODUCT_MODULE := true

include $(BUILD_PREBUILT)