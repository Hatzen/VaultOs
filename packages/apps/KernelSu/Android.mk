LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := KernelSU
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := KernelSU_Legacy_v1.1.1_12857-release.apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := platform

# Erzwingt das Extrahieren der libkernelsu.so aus der APK in das System-Image
LOCAL_EXTRACT_APK_EDGES := true
#LOCAL_PRODUCT_MODULE := true
# try fix dlopen failed: library "libkernelsu.so" not found
LOCAL_SYSTEM_MODULE := true
LOCAL_PRIVILEGED_MODULE := true

LOCAL_ENFORCE_USES_LIBRARIES := false

include $(BUILD_PREBUILT)