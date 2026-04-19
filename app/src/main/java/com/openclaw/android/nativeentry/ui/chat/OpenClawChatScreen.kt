package com.openclaw.android.nativeentry.ui.chat

import android.annotation.SuppressLint
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import android.net.Uri
import android.webkit.CookieManager
import android.webkit.ConsoleMessage
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebStorage
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.unit.dp
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import org.json.JSONArray
import org.json.JSONObject

private const val AllowedDashboardHost = "127.0.0.1"
private const val AllowedDashboardPort = 18789
private const val SelfTestBaseUrl = "https://openclaw-self-test/"
private const val MaxConsoleMessages = 4
private const val MaxScriptEntries = 8

private val TimeFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss")
private val TokenRegex = Regex("(#token=)([^&]+)")

private const val SelfTestHtml = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>OpenClaw WebView Self Test</title>
  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background: #f7f6f1;
      color: #1b1b18;
      display: flex;
      min-height: 100vh;
      align-items: center;
      justify-content: center;
    }
    .card {
      padding: 24px;
      border-radius: 16px;
      background: white;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>WebView self-test OK</h1>
    <p>This page is rendered from a local data source.</p>
  </div>
</body>
</html>
"""

enum class OpenClawChatFailureStage {
    GatewayOffline,
    DashboardUrlUnavailable,
}

data class OpenClawChatEntryState(
    val isLoadingDashboardUrl: Boolean = false,
    val dashboardUrl: String? = null,
    val errorMessage: String? = null,
    val failureStage: OpenClawChatFailureStage? = null,
    val chatAttemptId: String? = null,
    val currentDashboardUrlSummary: DashboardUrlSummary? = null,
    val previousDashboardUrlSummary: DashboardUrlSummary? = null,
)

data class DashboardUrlSummary(
    val requestedAt: String,
    val maskedUrl: String,
    val tokenSummary: String,
    val sameAsPrevious: Boolean,
)

private enum class DashboardLoadPhase {
    SelfTest,
    Dashboard,
}

private enum class DashboardViewState {
    SelfTestLoading,
    DashboardLoading,
    DashboardError,
    DashboardCompatibilityIssue,
    DashboardRenderSuspected,
    DashboardVisible,
}

private data class ConsoleLogEntry(
    val message: String,
    val sourceId: String,
    val lineNumber: Int,
    val messageLevel: String,
)

private data class DomScriptEntry(
    val src: String,
    val type: String,
    val noModule: Boolean,
)

private data class DomProbeResult(
    val readyState: String = "unknown",
    val title: String = "",
    val bodyChildren: Int = -1,
    val textLength: Int = -1,
    val background: String = "none",
    val hasModuleScript: Boolean = false,
    val scripts: List<DomScriptEntry> = emptyList(),
)

private data class DashboardDiagnostics(
    val maskedUrl: String,
    val webViewVersion: String = "Unavailable",
    val chatAttemptId: String = "N/A",
    val webViewInstanceId: String = "N/A",
    val currentDashboardUrlSummary: String = "N/A",
    val previousDashboardUrlSummary: String = "N/A",
    val progress: Int = 0,
    val pageTitle: String = "N/A",
    val lastPageStartedAt: String = "N/A",
    val lastPageFinishedAt: String = "N/A",
    val lastPageVisibleAt: String = "N/A",
    val lastMainFrameError: String = "N/A",
    val lastHttpError: String = "N/A",
    val consoleMessages: List<ConsoleLogEntry> = emptyList(),
    val renderProcessGone: String = "N/A",
    val selfTestStatus: String = "Not started",
    val domProbeSummary: String = "N/A",
    val scriptSummary: String = "N/A",
    val hasModuleScriptSummary: String = "Unknown",
    val siteDataResetSummary: String = "Not run",
    val siteDataResetStartedAt: String = "N/A",
    val siteDataResetCallbackAt: String = "N/A",
    val cookieClearObservation: String = "N/A",
    val dashboardLoadInvokedAt: String = "N/A",
    val dashboardLoadTargetUrlMasked: String = "N/A",
    val dashboardOnPageStartedUrlMasked: String = "N/A",
    val dashboardOnPageFinishedUrlMasked: String = "N/A",
)

fun isAllowedDashboardUrlStrict(url: String): Boolean {
    val uri = Uri.parse(url)
    return uri.scheme == "http" &&
        uri.host == AllowedDashboardHost &&
        uri.port == AllowedDashboardPort
}

@Composable
fun OpenClawChatScreen(
    chatEntryState: OpenClawChatEntryState,
    onRetryClick: () -> Unit,
    onBackClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    when {
        chatEntryState.isLoadingDashboardUrl -> {
            OpenClawChatMessagePanel(
                title = "正在进入聊天",
                message = "正在获取本机 OpenClaw Dashboard 地址，请稍候。",
                primaryActionLabel = null,
                onPrimaryActionClick = null,
                secondaryActionLabel = "返回首页",
                onSecondaryActionClick = onBackClick,
                modifier = modifier,
                leadingContent = {
                    CircularProgressIndicator()
                },
            )
        }

        !chatEntryState.errorMessage.isNullOrBlank() -> {
            val title = when (chatEntryState.failureStage) {
                OpenClawChatFailureStage.GatewayOffline -> "Gateway 未在线"
                OpenClawChatFailureStage.DashboardUrlUnavailable -> "Dashboard 地址获取失败"
                null -> "聊天入口暂时不可用"
            }
            OpenClawChatMessagePanel(
                title = title,
                message = chatEntryState.errorMessage.orEmpty(),
                primaryActionLabel = "重新尝试",
                onPrimaryActionClick = onRetryClick,
                secondaryActionLabel = "返回首页",
                onSecondaryActionClick = onBackClick,
                modifier = modifier,
            )
        }

        !chatEntryState.dashboardUrl.isNullOrBlank() -> {
            DiagnosticsDashboardWebView(
                dashboardUrl = chatEntryState.dashboardUrl.orEmpty(),
                chatAttemptId = chatEntryState.chatAttemptId,
                currentDashboardUrlSummary = chatEntryState.currentDashboardUrlSummary,
                previousDashboardUrlSummary = chatEntryState.previousDashboardUrlSummary,
                onRetryClick = onRetryClick,
                onBackClick = onBackClick,
                modifier = modifier,
            )
        }

        else -> {
            OpenClawChatMessagePanel(
                title = "聊天入口暂时不可用",
                message = "尚未获取到可用的 Dashboard 地址。",
                primaryActionLabel = "重新尝试",
                onPrimaryActionClick = onRetryClick,
                secondaryActionLabel = "返回首页",
                onSecondaryActionClick = onBackClick,
                modifier = modifier,
            )
        }
    }
}

@Composable
private fun OpenClawChatMessagePanel(
    title: String,
    message: String,
    primaryActionLabel: String?,
    onPrimaryActionClick: (() -> Unit)?,
    secondaryActionLabel: String,
    onSecondaryActionClick: () -> Unit,
    modifier: Modifier = Modifier,
    leadingContent: (@Composable () -> Unit)? = null,
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                leadingContent?.invoke()
                Text(text = title, style = MaterialTheme.typography.titleLarge)
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (primaryActionLabel != null && onPrimaryActionClick != null) {
                    Button(
                        onClick = onPrimaryActionClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = primaryActionLabel)
                    }
                }
                OutlinedButton(
                    onClick = onSecondaryActionClick,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = secondaryActionLabel)
                }
            }
        }
    }
}

@SuppressLint("SetJavaScriptEnabled")
@Composable
private fun DiagnosticsDashboardWebView(
    dashboardUrl: String,
    chatAttemptId: String?,
    currentDashboardUrlSummary: DashboardUrlSummary?,
    previousDashboardUrlSummary: DashboardUrlSummary?,
    onRetryClick: () -> Unit,
    onBackClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    if (!isAllowedDashboardUrlStrict(dashboardUrl)) {
        OpenClawChatMessagePanel(
            title = "聊天入口地址无效",
            message = "当前地址不是允许的本机 OpenClaw Dashboard 地址。",
            primaryActionLabel = "重新尝试",
            onPrimaryActionClick = onRetryClick,
            secondaryActionLabel = "返回首页",
            onSecondaryActionClick = onBackClick,
            modifier = modifier,
        )
        return
    }

    val context = LocalContext.current
    val maskedUrl = remember(dashboardUrl) { maskDashboardUrl(dashboardUrl) }
    val webViewVersion = remember {
        WebView.getCurrentWebViewPackage()?.let { "${it.packageName} ${it.versionName}" } ?: "Unavailable"
    }
    val webView = remember(dashboardUrl) {
        WebView(context).apply {
            setBackgroundColor(Color.WHITE)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.loadsImagesAutomatically = true
            settings.cacheMode = WebSettings.LOAD_DEFAULT
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
        }
    }
    val webViewInstanceId = remember(webView) { createWebViewInstanceId() }
    var loadPhase by remember(dashboardUrl) { mutableStateOf(DashboardLoadPhase.SelfTest) }
    var viewState by remember(dashboardUrl) { mutableStateOf(DashboardViewState.SelfTestLoading) }
    var diagnostics by remember(dashboardUrl) {
        mutableStateOf(
            DashboardDiagnostics(
                maskedUrl = maskedUrl,
                webViewVersion = webViewVersion,
                chatAttemptId = chatAttemptId ?: "N/A",
                webViewInstanceId = webViewInstanceId,
                currentDashboardUrlSummary = currentDashboardUrlSummary.asDebugText(),
                previousDashboardUrlSummary = previousDashboardUrlSummary.asDebugText(),
            ),
        )
    }
    var overlayMessage by remember(dashboardUrl) { mutableStateOf<String?>(null) }

    fun appendConsoleMessage(entry: ConsoleLogEntry) {
        diagnostics = diagnostics.copy(
            consoleMessages = (diagnostics.consoleMessages + entry).takeLast(MaxConsoleMessages),
        )
    }

    fun clearSiteDataAndLoadDashboard(targetView: WebView) {
        val resetStartedAt = formatNow()
        diagnostics = diagnostics.copy(
            siteDataResetSummary = "Running",
            siteDataResetStartedAt = resetStartedAt,
            siteDataResetCallbackAt = "Pending",
            cookieClearObservation = "awaiting-cookie-clear-callback",
        )
        targetView.clearCache(true)
        targetView.clearHistory()
        targetView.clearFormData()
        WebStorage.getInstance().deleteAllData()
        targetView.postDelayed({
            val currentDiagnostics = diagnostics
            if (currentDiagnostics.siteDataResetStartedAt == resetStartedAt &&
                currentDiagnostics.siteDataResetCallbackAt == "Pending"
            ) {
                diagnostics = currentDiagnostics.copy(
                    cookieClearObservation = "cookie-clear-timeout-suspected",
                )
            }
        }, 3_000L)
        val cookieManager = CookieManager.getInstance()
        cookieManager.removeAllCookies {
            cookieManager.flush()
            val callbackAt = formatNow()
            diagnostics = diagnostics.copy(
                siteDataResetSummary = "Completed $callbackAt",
                siteDataResetCallbackAt = callbackAt,
                cookieClearObservation = "callback-received",
                dashboardLoadInvokedAt = callbackAt,
                dashboardLoadTargetUrlMasked = maskDashboardUrl(dashboardUrl),
            )
            targetView.loadUrl(dashboardUrl)
        }
    }

    DisposableEffect(webView, dashboardUrl) {
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                diagnostics = diagnostics.copy(progress = newProgress)
            }

            override fun onReceivedTitle(view: WebView?, title: String?) {
                diagnostics = diagnostics.copy(pageTitle = title?.takeIf { it.isNotBlank() } ?: "暂无")
            }

            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                if (consoleMessage != null) {
                    appendConsoleMessage(
                        ConsoleLogEntry(
                            message = consoleMessage.message(),
                            sourceId = consoleMessage.sourceId().orEmpty(),
                            lineNumber = consoleMessage.lineNumber(),
                            messageLevel = consoleMessage.messageLevel().name,
                        ),
                    )
                }
                return super.onConsoleMessage(consoleMessage)
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?,
            ): Boolean {
                val targetUrl = request?.url?.toString() ?: return true
                return !(targetUrl.startsWith(SelfTestBaseUrl) ||
                    targetUrl == "about:blank" ||
                    isAllowedDashboardUrlStrict(targetUrl))
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                val isDashboardUrl = url != null && isAllowedDashboardUrlStrict(url)
                diagnostics = diagnostics.copy(
                    lastPageStartedAt = formatNow(),
                    dashboardOnPageStartedUrlMasked = if (isDashboardUrl) {
                        maskDashboardUrl(url)
                    } else {
                        diagnostics.dashboardOnPageStartedUrlMasked
                    },
                    maskedUrl = url?.takeIf { it.startsWith(SelfTestBaseUrl) }?.let { "自测页" }
                        ?: url?.let(::maskDashboardUrl)
                        ?: diagnostics.maskedUrl,
                )
                overlayMessage = null
                viewState = if (loadPhase == DashboardLoadPhase.SelfTest) {
                    DashboardViewState.SelfTestLoading
                } else {
                    DashboardViewState.DashboardLoading
                }
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                val finishedAt = formatNow()
                diagnostics = diagnostics.copy(
                    lastPageFinishedAt = finishedAt,
                    dashboardOnPageFinishedUrlMasked = if (
                        loadPhase == DashboardLoadPhase.Dashboard &&
                        url != null &&
                        isAllowedDashboardUrlStrict(url)
                    ) {
                        maskDashboardUrl(url)
                    } else {
                        diagnostics.dashboardOnPageFinishedUrlMasked
                    },
                )
                if (loadPhase == DashboardLoadPhase.SelfTest && url?.startsWith(SelfTestBaseUrl) == true) {
                    diagnostics = diagnostics.copy(selfTestStatus = "通过")
                    loadPhase = DashboardLoadPhase.Dashboard
                    viewState = DashboardViewState.DashboardLoading
                    view?.post { clearSiteDataAndLoadDashboard(view) }
                    return
                }

                if (loadPhase == DashboardLoadPhase.Dashboard && url != null && isAllowedDashboardUrlStrict(url)) {
                    view?.evaluateJavascript(DomProbeScript) { rawValue ->
                        val probeResult = parseDomProbeResult(rawValue)
                        val probeSummary = buildDomProbeSummary(probeResult)
                        diagnostics = diagnostics.copy(
                            domProbeSummary = probeSummary,
                            scriptSummary = buildScriptSummary(probeResult.scripts),
                            hasModuleScriptSummary = if (probeResult.hasModuleScript) "是" else "否",
                        )
                        viewState = when {
                            hasFatalJavaScriptSyntaxError(diagnostics.consoleMessages) &&
                                lacksMeaningfulRender(probeResult) ->
                                DashboardViewState.DashboardCompatibilityIssue

                            looksLikeRenderSuspected(probeResult, diagnostics.pageTitle) ->
                                DashboardViewState.DashboardRenderSuspected

                            else -> DashboardViewState.DashboardVisible
                        }
                    }
                }
            }

            override fun onPageCommitVisible(view: WebView?, url: String?) {
                diagnostics = diagnostics.copy(lastPageVisibleAt = formatNow())
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?,
            ) {
                if (request?.isForMainFrame != false) {
                    val message = error?.description?.toString() ?: "无法加载本机 Dashboard。"
                    diagnostics = diagnostics.copy(lastMainFrameError = message)
                    overlayMessage = message
                    viewState = DashboardViewState.DashboardError
                }
            }

            override fun onReceivedHttpError(
                view: WebView?,
                request: WebResourceRequest?,
                errorResponse: WebResourceResponse?,
            ) {
                if (request?.isForMainFrame != false) {
                    val message = "HTTP ${errorResponse?.statusCode ?: "?"} ${errorResponse?.reasonPhrase.orEmpty()}".trim()
                    diagnostics = diagnostics.copy(lastHttpError = message)
                    overlayMessage = message
                    viewState = DashboardViewState.DashboardError
                }
            }

            override fun onRenderProcessGone(
                view: WebView?,
                detail: RenderProcessGoneDetail?,
            ): Boolean {
                val message = buildString {
                    append("render process gone")
                    if (detail != null) {
                        append(", didCrash=")
                        append(detail.didCrash())
                        append(", priorityAtExit=")
                        append(detail.rendererPriorityAtExit())
                    }
                }
                diagnostics = diagnostics.copy(renderProcessGone = message)
                overlayMessage = message
                viewState = DashboardViewState.DashboardError
                return true
            }
        }

        diagnostics = diagnostics.copy(selfTestStatus = "进行中")
        webView.loadDataWithBaseURL(SelfTestBaseUrl, SelfTestHtml, "text/html", "utf-8", null)

        onDispose {
            webView.stopLoading()
            webView.destroy()
        }
    }

    Column(modifier = modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
        ) {
            AndroidView(
                factory = { webView },
                modifier = Modifier.fillMaxSize(),
            )

            if (viewState == DashboardViewState.SelfTestLoading || viewState == DashboardViewState.DashboardLoading) {
                LinearProgressIndicator(
                    progress = { diagnostics.progress / 100f },
                    modifier = Modifier.fillMaxWidth(),
                )
            }

            when (viewState) {
                DashboardViewState.DashboardError -> {
                    DiagnosticsOverlayCard(
                        title = "WebView 加载失败",
                        message = overlayMessage ?: "页面加载过程中发生错误。",
                        primaryActionLabel = "重新尝试",
                        onPrimaryActionClick = onRetryClick,
                        secondaryActionLabel = "返回首页",
                        onSecondaryActionClick = onBackClick,
                    )
                }

                DashboardViewState.DashboardCompatibilityIssue -> {
                    DiagnosticsOverlayCard(
                        title = "本机聊天页加载失败",
                        message = "主文档已加载，但设备 WebView / HarmonyOS 与 OpenClaw Dashboard 前端 bundle 可能存在兼容性问题。",
                        primaryActionLabel = "复制调试信息",
                        onPrimaryActionClick = {
                            copyDiagnosticsToClipboard(context, diagnostics, viewState)
                        },
                        secondaryActionLabel = "返回首页",
                        onSecondaryActionClick = onBackClick,
                    )
                }

                DashboardViewState.DashboardRenderSuspected -> {
                    DiagnosticsOverlayCard(
                        title = "页面已加载，但前端疑似未渲染",
                        message = "自测页已通过，Dashboard 主页面已完成加载，但当前设备上的前端内容仍可能没有正常绘制。",
                        primaryActionLabel = "重新尝试",
                        onPrimaryActionClick = onRetryClick,
                        secondaryActionLabel = "返回首页",
                        onSecondaryActionClick = onBackClick,
                    )
                }

                else -> Unit
            }
        }

        DiagnosticsPanel(
            diagnostics = diagnostics,
            viewState = viewState,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun DiagnosticsOverlayCard(
    title: String,
    message: String,
    primaryActionLabel: String,
    onPrimaryActionClick: () -> Unit,
    secondaryActionLabel: String,
    onSecondaryActionClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        contentAlignment = Alignment.Center,
    ) {
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(text = title, style = MaterialTheme.typography.titleMedium)
                Text(text = message, style = MaterialTheme.typography.bodyMedium)
                Button(
                    onClick = onPrimaryActionClick,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = primaryActionLabel)
                }
                OutlinedButton(
                    onClick = onSecondaryActionClick,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = secondaryActionLabel)
                }
            }
        }
    }
}

@Composable
private fun DiagnosticsPanel(
    diagnostics: DashboardDiagnostics,
    viewState: DashboardViewState,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    Card(
        modifier = modifier
            .padding(16.dp)
            .heightIn(max = 260.dp),
    ) {
        Column(
            modifier = Modifier
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(text = "聊天页调试信息", style = MaterialTheme.typography.titleMedium)
            Text(text = "当前状态：${viewState.label()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "WebView 版本：${diagnostics.webViewVersion}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Dashboard 地址：${diagnostics.maskedUrl}", style = MaterialTheme.typography.bodySmall)
            Text(text = "本次 URL 摘要：${diagnostics.currentDashboardUrlSummary}", style = MaterialTheme.typography.bodySmall)
            Text(text = "上次 URL 摘要：${diagnostics.previousDashboardUrlSummary}", style = MaterialTheme.typography.bodySmall)
            Text(text = "页面进度：${diagnostics.progress}%", style = MaterialTheme.typography.bodySmall)
            Text(text = "页面标题：${diagnostics.pageTitle}", style = MaterialTheme.typography.bodySmall)
            Text(text = "自测页结果：${diagnostics.selfTestStatus}", style = MaterialTheme.typography.bodySmall)
            Text(text = "站点状态清理：${diagnostics.siteDataResetSummary}", style = MaterialTheme.typography.bodySmall)
            Text(text = "最近 onPageStarted：${diagnostics.lastPageStartedAt}", style = MaterialTheme.typography.bodySmall)
            Text(text = "最近 onPageFinished：${diagnostics.lastPageFinishedAt}", style = MaterialTheme.typography.bodySmall)
            Text(text = "最近可视提交：${diagnostics.lastPageVisibleAt}", style = MaterialTheme.typography.bodySmall)
            Text(text = "最近资源错误：${diagnostics.lastMainFrameError}", style = MaterialTheme.typography.bodySmall)
            Text(text = "最近 HTTP 错误：${diagnostics.lastHttpError}", style = MaterialTheme.typography.bodySmall)
            Text(text = "最近 render process：${diagnostics.renderProcessGone}", style = MaterialTheme.typography.bodySmall)
            Text(text = "DOM 探针：${diagnostics.domProbeSummary}", style = MaterialTheme.typography.bodySmall)
            Text(text = "是否存在 module 脚本：${diagnostics.hasModuleScriptSummary}", style = MaterialTheme.typography.bodySmall)
            Text(text = "脚本摘要：${diagnostics.scriptSummary}", style = MaterialTheme.typography.bodySmall)
            Text(
                text = "最近 console：${diagnostics.consoleMessages.asDebugText()}",
                style = MaterialTheme.typography.bodySmall,
            )
            Text(text = "Attempt ID：${diagnostics.chatAttemptId}", style = MaterialTheme.typography.bodySmall)
            Text(text = "WebView Instance ID：${diagnostics.webViewInstanceId}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Site data reset started：${diagnostics.siteDataResetStartedAt}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Site data reset callback：${diagnostics.siteDataResetCallbackAt}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Cookie clear observation：${diagnostics.cookieClearObservation}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Dashboard load invoked：${diagnostics.dashboardLoadInvokedAt}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Dashboard load target：${diagnostics.dashboardLoadTargetUrlMasked}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Dashboard onPageStarted URL：${diagnostics.dashboardOnPageStartedUrlMasked}", style = MaterialTheme.typography.bodySmall)
            Text(text = "Dashboard onPageFinished URL：${diagnostics.dashboardOnPageFinishedUrlMasked}", style = MaterialTheme.typography.bodySmall)
            OutlinedButton(
                onClick = { copyDiagnosticsToClipboard(context, diagnostics, viewState) },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "复制调试信息")
            }
        }
    }
}

private fun DashboardViewState.label(): String = when (this) {
    DashboardViewState.SelfTestLoading -> "WebView 自测中"
    DashboardViewState.DashboardLoading -> "Dashboard 加载中"
    DashboardViewState.DashboardError -> "WebView 资源或网络错误"
    DashboardViewState.DashboardCompatibilityIssue -> "设备兼容性失败"
    DashboardViewState.DashboardRenderSuspected -> "加载完成但前端疑似未渲染"
    DashboardViewState.DashboardVisible -> "页面已显示"
}

private fun formatNow(): String =
    TimeFormatter.format(Instant.ofEpochMilli(System.currentTimeMillis()).atZone(ZoneId.systemDefault()))

private fun maskDashboardUrl(url: String): String =
    TokenRegex.replace(url) { match ->
        val token = match.groupValues[2]
        val maskedToken = if (token.length <= 8) {
            "***"
        } else {
            "${token.take(4)}***${token.takeLast(4)}"
        }
        "${match.groupValues[1]}$maskedToken"
    }

private fun DashboardUrlSummary?.asDebugText(): String =
    this?.let {
        "requestedAt=${it.requestedAt}, token=${it.tokenSummary}, sameAsPrevious=${it.sameAsPrevious}, url=${it.maskedUrl}"
    } ?: "暂无"

private fun normalizeJavascriptResult(rawValue: String?): String {
    if (rawValue.isNullOrBlank()) return "暂无"
    return rawValue
        .removePrefix("\"")
        .removeSuffix("\"")
        .replace("\\\"", "\"")
        .replace("\\n", " ")
        .replace("\\u003C", "<")
        .replace("\\u003E", ">")
}

private fun parseDomProbeResult(rawValue: String?): DomProbeResult {
    val normalized = normalizeJavascriptResult(rawValue)
    if (normalized == "暂无") return DomProbeResult()

    return try {
        val json = JSONObject(normalized)
        DomProbeResult(
            readyState = json.optString("readyState", "unknown"),
            title = json.optString("title", ""),
            bodyChildren = json.optInt("bodyChildren", -1),
            textLength = json.optInt("textLength", -1),
            background = json.optString("background", "none"),
            hasModuleScript = json.optBoolean("hasModuleScript", false),
            scripts = json.optJSONArray("scripts").toDomScriptEntries(),
        )
    } catch (_: Exception) {
        DomProbeResult()
    }
}

private fun JSONArray?.toDomScriptEntries(): List<DomScriptEntry> {
    if (this == null) return emptyList()
    return buildList {
        for (index in 0 until length()) {
            val item = optJSONObject(index) ?: continue
            add(
                DomScriptEntry(
                    src = item.optString("src", ""),
                    type = item.optString("type", ""),
                    noModule = item.optBoolean("noModule", false),
                ),
            )
        }
    }
}

private fun buildDomProbeSummary(result: DomProbeResult): String =
    """{"readyState":"${result.readyState}","title":"${result.title}","bodyChildren":${result.bodyChildren},"textLength":${result.textLength},"background":"${result.background}"}"""

private fun buildScriptSummary(scripts: List<DomScriptEntry>): String {
    if (scripts.isEmpty()) return "暂无"
    return scripts.joinToString(" | ") { script ->
        "src=${script.src.ifBlank { "[inline]" }}, type=${script.type.ifBlank { "[classic]" }}, noModule=${script.noModule}"
    }
}

private fun List<ConsoleLogEntry>.asDebugText(): String =
    ifEmpty { listOf(ConsoleLogEntry("暂无", "", 0, "INFO")) }
        .joinToString(" | ") { entry ->
            "${entry.messageLevel}: ${entry.message} (source=${entry.sourceId.ifBlank { "[inline]" }}, line=${entry.lineNumber})"
        }

private fun hasFatalJavaScriptSyntaxError(consoleMessages: List<ConsoleLogEntry>): Boolean =
    consoleMessages.any { message ->
        "uncaught syntaxerror" in message.message.lowercase() ||
            "unexpected token" in message.message.lowercase()
    }

private fun lacksMeaningfulRender(domProbeResult: DomProbeResult): Boolean {
    val hasNoBodyChildren = domProbeResult.bodyChildren == 0
    val hasNoText = domProbeResult.textLength == 0
    return hasNoBodyChildren || hasNoText
}

private fun looksLikeRenderSuspected(domProbeResult: DomProbeResult, pageTitle: String): Boolean {
    val hasNoBodyChildren = domProbeResult.bodyChildren == 0
    val hasNoText = domProbeResult.textLength == 0
    val titleBlank = pageTitle == "暂无"
    return hasNoBodyChildren || (hasNoText && titleBlank)
}

private fun buildDiagnosticsText(
    diagnostics: DashboardDiagnostics,
    viewState: DashboardViewState,
): String =
    buildString {
        appendLine("Attempt ID：${diagnostics.chatAttemptId}")
        appendLine("WebView Instance ID：${diagnostics.webViewInstanceId}")
        appendLine("当前状态：${viewState.label()}")
        appendLine("WebView 版本：${diagnostics.webViewVersion}")
        appendLine("Dashboard 地址：${diagnostics.maskedUrl}")
        appendLine("本次 URL 摘要：${diagnostics.currentDashboardUrlSummary}")
        appendLine("上次 URL 摘要：${diagnostics.previousDashboardUrlSummary}")
        appendLine("页面进度：${diagnostics.progress}%")
        appendLine("页面标题：${diagnostics.pageTitle}")
        appendLine("自测页结果：${diagnostics.selfTestStatus}")
        appendLine("站点状态清理：${diagnostics.siteDataResetSummary}")
        appendLine("最近 onPageStarted：${diagnostics.lastPageStartedAt}")
        appendLine("最近 onPageFinished：${diagnostics.lastPageFinishedAt}")
        appendLine("最近可视提交：${diagnostics.lastPageVisibleAt}")
        appendLine("最近资源错误：${diagnostics.lastMainFrameError}")
        appendLine("最近 HTTP 错误：${diagnostics.lastHttpError}")
        appendLine("最近 render process：${diagnostics.renderProcessGone}")
        appendLine("DOM 探针：${diagnostics.domProbeSummary}")
        appendLine("是否存在 module 脚本：${diagnostics.hasModuleScriptSummary}")
        appendLine("脚本摘要：${diagnostics.scriptSummary}")
        appendLine("最近 console：${diagnostics.consoleMessages.asDebugText()}")
        appendLine("Site data reset started：${diagnostics.siteDataResetStartedAt}")
        appendLine("Site data reset callback：${diagnostics.siteDataResetCallbackAt}")
        appendLine("Cookie clear observation：${diagnostics.cookieClearObservation}")
        appendLine("Dashboard load invoked：${diagnostics.dashboardLoadInvokedAt}")
        appendLine("Dashboard load target：${diagnostics.dashboardLoadTargetUrlMasked}")
        appendLine("Dashboard onPageStarted URL：${diagnostics.dashboardOnPageStartedUrlMasked}")
        appendLine("Dashboard onPageFinished URL：${diagnostics.dashboardOnPageFinishedUrlMasked}")
    }.trim()

private fun copyDiagnosticsToClipboard(
    context: Context,
    diagnostics: DashboardDiagnostics,
    viewState: DashboardViewState,
) {
    val clipboardManager = context.getSystemService(Context.CLIPBOARD_SERVICE) as? ClipboardManager ?: return
    val text = buildDiagnosticsText(diagnostics, viewState)
    clipboardManager.setPrimaryClip(ClipData.newPlainText("openclaw-chat-diagnostics", text))
}

private fun createWebViewInstanceId(): String =
    "wv-${System.currentTimeMillis().toString(16)}"

private const val DomProbeScript =
    """
    (() => {
      const body = document.body;
      const text = body && body.innerText ? body.innerText.trim() : "";
      const scripts = Array.from(document.scripts || []).slice(0, $MaxScriptEntries).map((script) => ({
        src: script.src || "",
        type: script.type || "",
        noModule: !!script.noModule
      }));
      return JSON.stringify({
        readyState: document.readyState,
        title: document.title || "",
        bodyChildren: body ? body.childElementCount : -1,
        textLength: text.length,
        background: body ? window.getComputedStyle(body).backgroundColor : "none",
        hasModuleScript: scripts.some((script) => script.type === "module"),
        scripts
      });
    })();
    """
