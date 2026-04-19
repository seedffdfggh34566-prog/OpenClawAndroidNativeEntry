package com.openclaw.android.nativeentry.ui.chat

import android.annotation.SuppressLint
import android.net.Uri
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
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

private const val AllowedDashboardHost = "127.0.0.1"
private const val AllowedDashboardPort = 18789

data class ChatEntryState(
    val isLoadingDashboardUrl: Boolean = false,
    val dashboardUrl: String? = null,
    val errorMessage: String? = null,
)

fun isAllowedDashboardUrl(url: String): Boolean {
    val uri = Uri.parse(url)
    return uri.scheme == "http" &&
        uri.host == AllowedDashboardHost &&
        uri.port == AllowedDashboardPort
}

@Composable
fun ChatScreen(
    chatEntryState: ChatEntryState,
    onRetryClick: () -> Unit,
    onBackClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    when {
        chatEntryState.isLoadingDashboardUrl -> {
            ChatMessagePanel(
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
            ChatMessagePanel(
                title = "聊天入口暂时不可用",
                message = chatEntryState.errorMessage.orEmpty(),
                primaryActionLabel = "重新尝试",
                onPrimaryActionClick = onRetryClick,
                secondaryActionLabel = "返回首页",
                onSecondaryActionClick = onBackClick,
                modifier = modifier,
            )
        }

        !chatEntryState.dashboardUrl.isNullOrBlank() -> {
            DashboardWebView(
                dashboardUrl = chatEntryState.dashboardUrl.orEmpty(),
                onRetryClick = onRetryClick,
                onBackClick = onBackClick,
                modifier = modifier,
            )
        }

        else -> {
            ChatMessagePanel(
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
private fun ChatMessagePanel(
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
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleLarge,
                )
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
private fun DashboardWebView(
    dashboardUrl: String,
    onRetryClick: () -> Unit,
    onBackClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    if (!isAllowedDashboardUrl(dashboardUrl)) {
        ChatMessagePanel(
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
    val webView = remember {
        WebView(context).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.loadsImagesAutomatically = true
            settings.cacheMode = WebSettings.LOAD_DEFAULT
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.setSupportMultipleWindows(false)
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
        }
    }
    var isPageLoading by remember(dashboardUrl) { mutableStateOf(true) }
    var pageErrorMessage by remember(dashboardUrl) { mutableStateOf<String?>(null) }

    DisposableEffect(webView) {
        onDispose {
            webView.destroy()
        }
    }

    if (pageErrorMessage != null) {
        ChatMessagePanel(
            title = "聊天页加载失败",
            message = pageErrorMessage ?: "页面未能成功加载。",
            primaryActionLabel = "重新尝试",
            onPrimaryActionClick = onRetryClick,
            secondaryActionLabel = "返回首页",
            onSecondaryActionClick = onBackClick,
            modifier = modifier,
        )
        return
    }

    Box(modifier = modifier.fillMaxSize()) {
        AndroidView(
            factory = {
                webView.apply {
                    webViewClient = object : WebViewClient() {
                        override fun shouldOverrideUrlLoading(
                            view: WebView?,
                            request: WebResourceRequest?,
                        ): Boolean {
                            val targetUrl = request?.url?.toString() ?: return true
                            return !isAllowedDashboardUrl(targetUrl)
                        }

                        override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                            isPageLoading = true
                            pageErrorMessage = null
                        }

                        override fun onPageFinished(view: WebView?, url: String?) {
                            isPageLoading = false
                        }

                        override fun onReceivedError(
                            view: WebView?,
                            request: WebResourceRequest?,
                            error: WebResourceError?,
                        ) {
                            if (request?.isForMainFrame != false) {
                                isPageLoading = false
                                pageErrorMessage = error?.description?.toString() ?: "无法加载本机 Dashboard。"
                            }
                        }
                    }
                    loadUrl(dashboardUrl)
                }
            },
            update = { view ->
                if (view.url != dashboardUrl) {
                    pageErrorMessage = null
                    isPageLoading = true
                    view.stopLoading()
                    view.loadUrl(dashboardUrl)
                }
            },
            modifier = Modifier.fillMaxSize(),
        )

        if (isPageLoading) {
            LinearProgressIndicator(
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}
