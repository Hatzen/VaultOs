LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

# https://github.com/kiwix/kiwix-android/releases/tag/v3.14.1
# TODO: Add ZIM Files
LOCAL_MODULE := Wiki
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := v3.14.1-universal-standalone.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PLATFORM # TODO dont need highest permission?

include $(BUILD_PREBUILT)
