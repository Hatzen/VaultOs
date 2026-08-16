LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := Kernel
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := app-fdroid-release.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_OPTIONAL_USES_LIBRARIES := androidx.window.extensions androidx.window.sidecar

# trial not flashing it
LOCAL_PRODUCT_MODULE := true
LOCAL_MULTILIB := 64

# Unconfirmed so far
LOCAL_UNCOMPRESS_DEX := false
LOCAL_DEX_PREOPT := false

include $(BUILD_PREBUILT)
