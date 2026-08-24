LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := KernelSU
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := KernelSU_Next_v3.3.0_33214-release.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := platform
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/$(LOCAL_SRC_FILES)



# Erzwingt das Extrahieren der libkernelsu.so aus der APK in das System-Image
# LOCAL_EXTRACT_APK_EDGES := true
#LOCAL_PRODUCT_MODULE := true
# try fix dlopen failed: library "libkernelsu.so" not found
LOCAL_SYSTEM_MODULE := true

LOCAL_MULTILIB := 64

LOCAL_UNCOMPRESS_DEX := true
LOCAL_DEX_PREOPT := true
LOCAL_ENFORCE_USES_LIBRARIES := false

include $(BUILD_PREBUILT)