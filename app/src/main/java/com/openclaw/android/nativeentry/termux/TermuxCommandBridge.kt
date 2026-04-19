package com.openclaw.android.nativeentry.termux

import android.app.PendingIntent
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Deferred

private const val TermuxPackageName = "com.termux"
private const val TermuxRunCommandService = "com.termux.app.RunCommandService"
private const val TermuxRunCommandAction = "com.termux.RUN_COMMAND"
private const val ExtraCommandPath = "com.termux.RUN_COMMAND_PATH"
private const val ExtraCommandArguments = "com.termux.RUN_COMMAND_ARGUMENTS"
private const val ExtraCommandWorkdir = "com.termux.RUN_COMMAND_WORKDIR"
private const val ExtraCommandBackground = "com.termux.RUN_COMMAND_BACKGROUND"
private const val ExtraPendingIntent = "com.termux.RUN_COMMAND_PENDING_INTENT"

private const val TermuxBashPath = "/data/data/com.termux/files/usr/bin/bash"
private const val TermuxHomePath = "/data/data/com.termux/files/home"

const val OpenClawBootLogPath = "/data/data/com.termux/files/home/openclaw-runcommand.log"

private val NextRequestId = AtomicInteger(1)

data class OpenClawTermuxCommandDispatchResult(
    val success: Boolean,
    val message: String,
)

data class OpenClawTermuxCommandLaunch(
    val dispatch: OpenClawTermuxCommandDispatchResult,
    val result: Deferred<OpenClawTermuxCommandResult>?,
)

data class OpenClawTermuxCommandResult(
    val commandKind: String,
    val requestId: Int,
    val exitCode: Int?,
    val stdout: String?,
    val stderr: String?,
    val errorMessage: String?,
)

fun dispatchBootOpenClawWithResult(context: Context): OpenClawTermuxCommandLaunch {
    val command = """
        export HOME=/data/data/com.termux/files/home
        export PATH=${'$'}HOME/bin:/data/data/com.termux/files/usr/bin:${'$'}PATH
        LOG_FILE="$OpenClawBootLogPath"
        START_TIME=${'$'}(date '+%Y-%m-%d %H:%M:%S')
        {
          echo "[${'$'}START_TIME] RUN_COMMAND start"
          echo "HOME=${'$'}HOME"
          echo "PATH=${'$'}PATH"
          echo "COMMAND=boot-openclaw"
          echo "BOOT_PATH=${'$'}(command -v boot-openclaw || echo not_found)"
          boot-openclaw
        } >> "${'$'}LOG_FILE" 2>&1
        EXIT_CODE=${'$'}?
        END_TIME=${'$'}(date '+%Y-%m-%d %H:%M:%S')
        echo "[${'$'}END_TIME] EXIT_CODE=${'$'}EXIT_CODE" >> "${'$'}LOG_FILE"
        exit ${'$'}EXIT_CODE
    """.trimIndent()

    return dispatchCommand(
        context = context,
        commandKind = TermuxCommandKind.BootOpenClaw.value,
        command = command,
    )
}

fun dispatchTmuxSessionCheckWithResult(context: Context): OpenClawTermuxCommandLaunch {
    val command = """
        export HOME=/data/data/com.termux/files/home
        export PATH=${'$'}HOME/bin:/data/data/com.termux/files/usr/bin:${'$'}PATH
        tmux has-session -t openclaw
    """.trimIndent()

    return dispatchCommand(
        context = context,
        commandKind = TermuxCommandKind.TmuxHasSession.value,
        command = command,
    )
}

fun dispatchDashboardUrlWithResult(context: Context): OpenClawTermuxCommandLaunch {
    val command = """
        export HOME=/data/data/com.termux/files/home
        export PATH=${'$'}HOME/bin:/data/data/com.termux/files/usr/bin:${'$'}PATH
        OPENCLAW_ENTRY=/data/data/com.termux/files/usr/lib/node_modules/openclaw/openclaw.mjs
        if [ -f "${'$'}OPENCLAW_ENTRY" ]; then
          node "${'$'}OPENCLAW_ENTRY" dashboard 2>&1
        else
          openclaw dashboard 2>&1
        fi
    """.trimIndent()

    return dispatchCommand(
        context = context,
        commandKind = TermuxCommandKind.DashboardUrl.value,
        command = command,
    )
}

private fun dispatchCommand(
    context: Context,
    commandKind: String,
    command: String,
): OpenClawTermuxCommandLaunch {
    if (!isTermuxInstalled(context)) {
        return OpenClawTermuxCommandLaunch(
            dispatch = OpenClawTermuxCommandDispatchResult(
                success = false,
                message = "未检测到 Termux，请先安装并确认包名为 com.termux。",
            ),
            result = null,
        )
    }

    val requestId = NextRequestId.getAndIncrement()
    val resultDeferred = CompletableDeferred<OpenClawTermuxCommandResult>()
    PendingOpenClawTermuxResults.register(requestId, resultDeferred)

    val callbackIntent = Intent(context, TermuxCommandResultReceiver::class.java).apply {
        putExtra(TermuxResultExtraRequestId, requestId)
        putExtra(TermuxResultExtraCommandKind, commandKind)
    }
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        requestId,
        callbackIntent,
        PendingIntent.FLAG_UPDATE_CURRENT or
            PendingIntent.FLAG_ONE_SHOT or
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                PendingIntent.FLAG_MUTABLE
            } else {
                0
            },
    )

    val intent = Intent(TermuxRunCommandAction).apply {
        component = ComponentName(TermuxPackageName, TermuxRunCommandService)
        putExtra(ExtraCommandPath, TermuxBashPath)
        putExtra(ExtraCommandArguments, arrayOf("-lc", command))
        putExtra(ExtraCommandWorkdir, TermuxHomePath)
        putExtra(ExtraCommandBackground, true)
        putExtra(ExtraPendingIntent, pendingIntent)
    }

    return try {
        val componentName = context.startService(intent)
        if (componentName != null) {
            OpenClawTermuxCommandLaunch(
                dispatch = OpenClawTermuxCommandDispatchResult(
                    success = true,
                    message = when (commandKind) {
                        TermuxCommandKind.BootOpenClaw.value -> "已向 Termux 发起 boot-openclaw 启动请求。"
                        TermuxCommandKind.TmuxHasSession.value -> "已向 Termux 发起 tmux 会话检查。"
                        TermuxCommandKind.DashboardUrl.value -> "已向 Termux 请求 Dashboard 地址。"
                        else -> "已向 Termux 发起命令请求。"
                    },
                ),
                result = resultDeferred,
            )
        } else {
            PendingOpenClawTermuxResults.complete(
                requestId = requestId,
                result = OpenClawTermuxCommandResult(
                    commandKind = commandKind,
                    requestId = requestId,
                    exitCode = null,
                    stdout = null,
                    stderr = null,
                    errorMessage = "Termux 未接受命令请求。",
                ),
            )
            OpenClawTermuxCommandLaunch(
                dispatch = OpenClawTermuxCommandDispatchResult(
                    success = false,
                    message = "Termux 未接受启动请求，请检查 RUN_COMMAND 权限与 Termux 设置。",
                ),
                result = null,
            )
        }
    } catch (error: SecurityException) {
        PendingOpenClawTermuxResults.complete(
            requestId = requestId,
            result = OpenClawTermuxCommandResult(
                commandKind = commandKind,
                requestId = requestId,
                exitCode = null,
                stdout = null,
                stderr = null,
                errorMessage = "缺少 Termux RUN_COMMAND 权限。",
            ),
        )
        OpenClawTermuxCommandLaunch(
            dispatch = OpenClawTermuxCommandDispatchResult(
                success = false,
                message = "缺少 Termux RUN_COMMAND 权限，请在系统设置中授予运行命令权限。",
            ),
            result = null,
        )
    } catch (error: Exception) {
        PendingOpenClawTermuxResults.complete(
            requestId = requestId,
            result = OpenClawTermuxCommandResult(
                commandKind = commandKind,
                requestId = requestId,
                exitCode = null,
                stdout = null,
                stderr = null,
                errorMessage = error.message ?: error.javaClass.simpleName,
            ),
        )
        OpenClawTermuxCommandLaunch(
            dispatch = OpenClawTermuxCommandDispatchResult(
                success = false,
                message = error.message ?: error.javaClass.simpleName,
            ),
            result = null,
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

private enum class TermuxCommandKind(val value: String) {
    BootOpenClaw("boot_openclaw"),
    TmuxHasSession("tmux_has_session"),
    DashboardUrl("dashboard_url"),
}

internal object PendingOpenClawTermuxResults {
    private val pending = ConcurrentHashMap<Int, CompletableDeferred<OpenClawTermuxCommandResult>>()

    fun register(requestId: Int, deferred: CompletableDeferred<OpenClawTermuxCommandResult>) {
        pending[requestId] = deferred
    }

    fun complete(requestId: Int, result: OpenClawTermuxCommandResult) {
        pending.remove(requestId)?.complete(result)
    }
}
