LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := Wiki
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := v3.14.1-universal-standalone.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)

# Korrektur: Die heruntergeladene APK ist bereits signiert!
LOCAL_CERTIFICATE := PRESIGNED

LOCAL_OPTIONAL_USES_LIBRARIES := androidx.window.extensions androidx.window.sidecar

include $(BUILD_PREBUILT)