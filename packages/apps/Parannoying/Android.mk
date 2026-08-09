LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := Parannoying
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := app-prod-release.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED

# briar wont get flashed maybe because of combined apk
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := true
LOCAL_MULTILIB := 64

include $(BUILD_PREBUILT)