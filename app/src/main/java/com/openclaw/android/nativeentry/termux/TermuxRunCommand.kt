package com.openclaw.android.nativeentry.termux

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build

private const val TermuxPackageName = "com.termux"
private const val TermuxRunCommandService = "com.termux.app.RunCommandService"
private const val TermuxRunCommandAction = "com.termux.RUN_COMMAND"
private const val ExtraCommandPath = "com.termux.RUN_COMMAND_PATH"
private const val ExtraCommandArguments = "com.termux.RUN_COMMAND_ARGUMENTS"
private const val ExtraCommandWorkdir = "com.termux.RUN_COMMAND_WORKDIR"
private const val ExtraCommandBackground = "com.termux.RUN_COMMAND_BACKGROUND"

private const val TermuxBashPath = "/data/data/com.termux/files/usr/bin/bash"
private const val TermuxHomePath = "/data/data/com.termux/files/home"
private const val BootOpenClawPath = "/data/data/com.termux/files/home/bin/boot-openclaw"

data class TermuxCommandDispatchResult(
    val success: Boolean,
    val message: String,
)

fun dispatchBootOpenClaw(context: Context): TermuxCommandDispatchResult {
    if (!isTermuxInstalled(context)) {
        return TermuxCommandDispatchResult(
            success = false,
            message = "未检测到 Termux，请先安装并确认包名为 com.termux。",
        )
    }

    val intent = Intent(TermuxRunCommandAction).apply {
        component = ComponentName(TermuxPackageName, TermuxRunCommandService)
        putExtra(ExtraCommandPath, TermuxBashPath)
        putExtra(ExtraCommandArguments, arrayOf("-lc", BootOpenClawPath))
        putExtra(ExtraCommandWorkdir, TermuxHomePath)
        putExtra(ExtraCommandBackground, true)
    }

    return try {
        val componentName = context.startService(intent)
        if (componentName != null) {
            TermuxCommandDispatchResult(
                success = true,
                message = "已向 Termux 发起 boot-openclaw 启动请求。",
            )
        } else {
            TermuxCommandDispatchResult(
                success = false,
                message = "Termux 未接受启动请求，请检查 RUN_COMMAND 权限与 Termux 设置。",
            )
        }
    } catch (error: SecurityException) {
        TermuxCommandDispatchResult(
            success = false,
            message = "缺少 Termux RUN_COMMAND 权限，请在系统设置中授予运行命令权限。",
        )
    } catch (error: Exception) {
        TermuxCommandDispatchResult(
            success = false,
            message = error.message ?: error.javaClass.simpleName,
        )
    }
}

private fun isTermuxInstalled(context: Context): Boolean =
    try {
        val packageManager = context.packageManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            packageManager.getPackageInfo(
                TermuxPackageName,
                PackageManager.PackageInfoFlags.of(0),
            )
        } else {
            @Suppress("DEPRECATION")
            packageManager.getPackageInfo(TermuxPackageName, 0)
        }
        true
    } catch (_: PackageManager.NameNotFoundException) {
        false
    }
