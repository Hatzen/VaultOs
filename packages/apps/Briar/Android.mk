LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := Briar
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := briar.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_OPTIONAL_USES_LIBRARIES := androidx.window.extensions androidx.window.sidecar

# briar wont get flashed maybe because of combined apk
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := true
LOCAL_MULTILIB := 64

include $(BUILD_PREBUILT)