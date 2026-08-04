LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := FancyLauncher
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := fr.neamar.kiss_224.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PLATFORM # Gibt der App höchste Systemrechte

include $(BUILD_PREBUILT)
