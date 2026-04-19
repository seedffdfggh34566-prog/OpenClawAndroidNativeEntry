package com.openclaw.android.nativeentry.ui.home

import java.net.ConnectException
import java.net.HttpURLConnection
import java.net.NoRouteToHostException
import java.net.SocketTimeoutException
import java.net.URL
import java.net.UnknownHostException
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

const val GatewayEndpoint = "http://127.0.0.1:18789"

private val DisplayTimeFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

sealed interface GatewayStatus {
    data object Checking : GatewayStatus

    data class Running(
        val statusCode: Int,
    ) : GatewayStatus

    data object Unreachable : GatewayStatus

    data class Failed(
        val message: String,
    ) : GatewayStatus
}

data class GatewayCheckSnapshot(
    val status: GatewayStatus = GatewayStatus.Checking,
    val checkedAtMillis: Long? = null,
    val endpoint: String = GatewayEndpoint,
)

data class OpenClawLaunchSnapshot(
    val attemptedAtMillis: Long? = null,
    val dispatchSucceeded: Boolean? = null,
    val dispatchMessage: String = "尚未尝试启动",
    val logFilePath: String = "/data/data/com.termux/files/home/openclaw-runcommand.log",
    val bootExitCode: Int? = null,
    val tmuxSessionExists: Boolean? = null,
    val tmuxSessionMessage: String = "尚未检查 tmux 会话",
    val pollingStarted: Boolean = false,
    val connectionSucceeded: Boolean? = null,
    val finalMessage: String = "尚未尝试启动",
    val isLaunching: Boolean = false,
)

suspend fun detectGatewayStatus(): GatewayStatus = withContext(Dispatchers.IO) {
    try {
        val connection = (URL(GatewayEndpoint).openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 2_000
            readTimeout = 2_000
            instanceFollowRedirects = false
            useCaches = false
            setRequestProperty("Cache-Control", "no-cache")
            setRequestProperty("Pragma", "no-cache")
            setRequestProperty("Connection", "close")
        }

        connection.use {
            GatewayStatus.Running(statusCode = it.responseCode)
        }
    } catch (_: ConnectException) {
        GatewayStatus.Unreachable
    } catch (_: SocketTimeoutException) {
        GatewayStatus.Unreachable
    } catch (_: NoRouteToHostException) {
        GatewayStatus.Unreachable
    } catch (_: UnknownHostException) {
        GatewayStatus.Unreachable
    } catch (error: Exception) {
        GatewayStatus.Failed(message = error.message ?: error.javaClass.simpleName)
    }
}

fun GatewayCheckSnapshot.lastCheckedLabel(): String =
    checkedAtMillis?.let {
        DisplayTimeFormatter.format(
            Instant.ofEpochMilli(it).atZone(ZoneId.systemDefault()),
        )
    } ?: "暂无"

fun GatewayStatus.title(): String = when (this) {
    GatewayStatus.Checking -> "状态：检测中"
    is GatewayStatus.Running -> "状态：已连接 / 运行中"
    GatewayStatus.Unreachable -> "状态：无法连接"
    is GatewayStatus.Failed -> "状态：检测失败"
}

fun GatewayStatus.description(): String = when (this) {
    GatewayStatus.Checking -> "正在检测本机 Gateway，请稍候。"
    is GatewayStatus.Running -> "已收到本机 Gateway 响应（HTTP $statusCode），说明服务正在监听该地址。"
    GatewayStatus.Unreachable -> "当前无法连接到 127.0.0.1:18789，请确认设备上的 Gateway 是否已启动。"
    is GatewayStatus.Failed -> "检测过程中发生异常：$message"
}

fun GatewayStatus.diagnosticStatus(): String = when (this) {
    GatewayStatus.Checking -> "检测中"
    is GatewayStatus.Running -> "成功"
    GatewayStatus.Unreachable -> "失败"
    is GatewayStatus.Failed -> "失败"
}

fun GatewayStatus.diagnosticDetail(): String = when (this) {
    GatewayStatus.Checking -> "正在发起新的检测请求。"
    is GatewayStatus.Running -> "HTTP $statusCode"
    GatewayStatus.Unreachable -> "无法连接到本机地址"
    is GatewayStatus.Failed -> message
}

fun OpenClawLaunchSnapshot.attemptedAtLabel(): String =
    attemptedAtMillis?.let {
        DisplayTimeFormatter.format(
            Instant.ofEpochMilli(it).atZone(ZoneId.systemDefault()),
        )
    } ?: "暂无"

private inline fun <T> HttpURLConnection.use(block: (HttpURLConnection) -> T): T =
    try {
        block(this)
    } finally {
        disconnect()
    }
