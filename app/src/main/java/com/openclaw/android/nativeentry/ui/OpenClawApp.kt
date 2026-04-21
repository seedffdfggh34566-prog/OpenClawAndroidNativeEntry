package com.openclaw.android.nativeentry.ui

import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.Modifier
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.openclaw.android.nativeentry.navigation.OpenClawDestination
import com.openclaw.android.nativeentry.navigation.OpenClawNavHost
import com.openclaw.android.nativeentry.navigation.navigateToTopLevel
import com.openclaw.android.nativeentry.termux.OpenClawBootLogPath
import com.openclaw.android.nativeentry.termux.OpenClawTermuxCommandResult
import com.openclaw.android.nativeentry.termux.dispatchBootOpenClawWithResult
import com.openclaw.android.nativeentry.termux.dispatchDashboardUrlWithResult
import com.openclaw.android.nativeentry.termux.dispatchTmuxSessionCheckWithResult
import com.openclaw.android.nativeentry.ui.chat.OpenClawChatEntryState
import com.openclaw.android.nativeentry.ui.chat.OpenClawChatFailureStage
import com.openclaw.android.nativeentry.ui.chat.DashboardUrlSummary
import com.openclaw.android.nativeentry.ui.chat.isAllowedDashboardUrlStrict
import com.openclaw.android.nativeentry.ui.home.GatewayCheckSnapshot
import com.openclaw.android.nativeentry.ui.home.GatewayStatus
import com.openclaw.android.nativeentry.ui.home.OpenClawLaunchSnapshot
import com.openclaw.android.nativeentry.ui.home.detectGatewayStatus
import com.openclaw.android.nativeentry.ui.shell.sampleV1ShellPlaceholderState
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private const val GatewayLaunchTimeoutMillis = 75_000L
private const val GatewayLaunchPollIntervalMillis = 1_500L
private val DashboardUrlPattern = Regex("""http://127\.0\.0\.1:18789[^\s]*#token=[^\s]+""")

@Composable
fun OpenClawApp() {
    val context = LocalContext.current
    val navController = rememberNavController()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val lifecycleOwner = LocalLifecycleOwner.current
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val currentScreen = OpenClawDestination.fromRoute(currentDestination?.route) ?: OpenClawDestination.Home
    val isTopLevelScreen = OpenClawDestination.topLevelDestinations.any { it.route == currentScreen.route }
    val placeholderState = remember { sampleV1ShellPlaceholderState() }
    var gatewaySnapshot by remember { mutableStateOf(GatewayCheckSnapshot()) }
    var launchSnapshot by remember { mutableStateOf(OpenClawLaunchSnapshot()) }
    var chatEntryState by remember { mutableStateOf(OpenClawChatEntryState()) }
    var lastDashboardUrlSummary by remember { mutableStateOf<DashboardUrlSummary?>(null) }
    var latestRefreshToken by remember { mutableIntStateOf(0) }
    var refreshJob by remember { mutableStateOf<Job?>(null) }
    var launchPollingJob by remember { mutableStateOf<Job?>(null) }

    fun updateGatewaySnapshot(status: GatewayStatus) {
        gatewaySnapshot = gatewaySnapshot.copy(
            status = status,
            checkedAtMillis = System.currentTimeMillis(),
        )
    }

    fun refreshGatewayStatus() {
        if (launchPollingJob?.isActive == true) return
        refreshJob?.cancel()
        val requestToken = latestRefreshToken + 1
        latestRefreshToken = requestToken
        gatewaySnapshot = gatewaySnapshot.copy(
            status = GatewayStatus.Checking,
            checkedAtMillis = System.currentTimeMillis(),
        )
        refreshJob = scope.launch {
            val detectedStatus = detectGatewayStatus()
            if (requestToken == latestRefreshToken && launchPollingJob?.isActive != true) {
                updateGatewaySnapshot(detectedStatus)
            }
        }
    }

    fun startOpenClaw() {
        if (launchSnapshot.isLaunching) return

        refreshJob?.cancel()
        launchPollingJob?.cancel()

        val attemptedAtMillis = System.currentTimeMillis()
        val bootLaunch = dispatchBootOpenClawWithResult(context)
        val dispatchResult = bootLaunch.dispatch

        launchSnapshot = OpenClawLaunchSnapshot(
            attemptedAtMillis = attemptedAtMillis,
            dispatchSucceeded = dispatchResult.success,
            dispatchMessage = dispatchResult.message,
            logFilePath = OpenClawBootLogPath,
            pollingStarted = dispatchResult.success,
            connectionSucceeded = if (dispatchResult.success) null else false,
            finalMessage = if (dispatchResult.success) {
                "启动命令已发出，正在检查 tmux 会话并轮询 Gateway 状态。"
            } else {
                dispatchResult.message
            },
            isLaunching = dispatchResult.success,
        )

        scope.launch {
            snackbarHostState.showSnackbar(dispatchResult.message)
        }

        if (!dispatchResult.success) return

        scope.launch {
            val bootResult = bootLaunch.result?.await() ?: return@launch
            val exitCode = bootResult.exitCode
            val resultMessage = when {
                exitCode == null && !bootResult.errorMessage.isNullOrBlank() -> bootResult.errorMessage
                exitCode != null -> "boot-openclaw 已退出，exit code=$exitCode"
                else -> "boot-openclaw 已执行完成。"
            } ?: "boot-openclaw 已执行完成。"

            launchSnapshot = launchSnapshot.copy(
                bootExitCode = exitCode,
                finalMessage = if (launchSnapshot.connectionSucceeded == true) {
                    launchSnapshot.finalMessage
                } else {
                    resultMessage
                },
            )
        }

        gatewaySnapshot = gatewaySnapshot.copy(
            status = GatewayStatus.Checking,
            checkedAtMillis = attemptedAtMillis,
        )

        launchPollingJob = scope.launch {
            val deadline = System.currentTimeMillis() + GatewayLaunchTimeoutMillis
            var lastObservedStatus: GatewayStatus = GatewayStatus.Unreachable
            var tmuxSessionExists = false

            while (System.currentTimeMillis() < deadline) {
                if (!tmuxSessionExists) {
                    val tmuxLaunch = dispatchTmuxSessionCheckWithResult(context)
                    if (!tmuxLaunch.dispatch.success) {
                        launchSnapshot = launchSnapshot.copy(
                            tmuxSessionExists = false,
                            tmuxSessionMessage = tmuxLaunch.dispatch.message,
                            connectionSucceeded = false,
                            finalMessage = tmuxLaunch.dispatch.message,
                            isLaunching = false,
                        )
                        return@launch
                    }

                    val tmuxResult = tmuxLaunch.result?.await()
                    tmuxSessionExists = tmuxResult?.exitCode == 0
                    launchSnapshot = launchSnapshot.copy(
                        tmuxSessionExists = tmuxSessionExists,
                        tmuxSessionMessage = if (tmuxSessionExists) {
                            "已检测到 openclaw tmux 会话。"
                        } else {
                            "启动脚本未成功建立 openclaw tmux 会话。"
                        },
                    )

                    if (!tmuxSessionExists) {
                        gatewaySnapshot = gatewaySnapshot.copy(
                            status = GatewayStatus.Checking,
                            checkedAtMillis = System.currentTimeMillis(),
                        )
                        delay(GatewayLaunchPollIntervalMillis)
                        continue
                    }
                }

                val observedStatus = detectGatewayStatus()
                lastObservedStatus = observedStatus

                gatewaySnapshot = gatewaySnapshot.copy(
                    status = if (observedStatus is GatewayStatus.Running) observedStatus else GatewayStatus.Checking,
                    checkedAtMillis = System.currentTimeMillis(),
                )

                if (observedStatus is GatewayStatus.Running) {
                    launchSnapshot = launchSnapshot.copy(
                        pollingStarted = true,
                        tmuxSessionExists = true,
                        tmuxSessionMessage = "已检测到 openclaw tmux 会话。",
                        connectionSucceeded = true,
                        finalMessage = "Gateway 已连接成功。",
                        isLaunching = false,
                    )
                    return@launch
                }

                delay(GatewayLaunchPollIntervalMillis)
            }

            updateGatewaySnapshot(lastObservedStatus)
            launchSnapshot = launchSnapshot.copy(
                pollingStarted = true,
                tmuxSessionExists = tmuxSessionExists,
                tmuxSessionMessage = if (tmuxSessionExists) {
                    "已检测到 openclaw tmux 会话。"
                } else {
                    "启动脚本未成功建立 openclaw tmux 会话。"
                },
                connectionSucceeded = false,
                finalMessage = when {
                    !tmuxSessionExists -> "启动脚本未成功建立 openclaw tmux 会话。"
                    launchSnapshot.bootExitCode != null && launchSnapshot.bootExitCode != 0 ->
                        "boot-openclaw 已退出，exit code=${launchSnapshot.bootExitCode}"
                    lastObservedStatus is GatewayStatus.Failed ->
                        "启动后仍未连接：${lastObservedStatus.message}"
                    lastObservedStatus is GatewayStatus.Unreachable ->
                        "启动后仍未连接，已超过 75 秒。"
                    lastObservedStatus is GatewayStatus.Checking ->
                        "启动后仍未连接，轮询结束时仍在检测中。"
                    else -> "Gateway 已连接成功。"
                },
                isLaunching = false,
            )
        }
    }

    fun loadChatEntry() {
        if (chatEntryState.isLoadingDashboardUrl) return

        refreshJob?.cancel()
        val chatAttemptId = generateChatAttemptId()
        chatEntryState = OpenClawChatEntryState(
            isLoadingDashboardUrl = true,
            chatAttemptId = chatAttemptId,
        )

        scope.launch {
            gatewaySnapshot = gatewaySnapshot.copy(
                status = GatewayStatus.Checking,
                checkedAtMillis = System.currentTimeMillis(),
            )

            val detectedStatus = detectGatewayStatus()
            updateGatewaySnapshot(detectedStatus)

            if (detectedStatus !is GatewayStatus.Running) {
                chatEntryState = OpenClawChatEntryState(
                    errorMessage = "Gateway 当前未在线，请先启动 OpenClaw。",
                    failureStage = OpenClawChatFailureStage.GatewayOffline,
                    chatAttemptId = chatAttemptId,
                )
                snackbarHostState.showSnackbar("Gateway 当前未在线，请先启动 OpenClaw。")
                return@launch
            }

            navController.navigate(OpenClawDestination.Chat.route) {
                launchSingleTop = true
            }

            val dashboardLaunch = dispatchDashboardUrlWithResult(context)
            if (!dashboardLaunch.dispatch.success) {
                chatEntryState = OpenClawChatEntryState(
                    errorMessage = dashboardLaunch.dispatch.message,
                    failureStage = OpenClawChatFailureStage.DashboardUrlUnavailable,
                    chatAttemptId = chatAttemptId,
                )
                snackbarHostState.showSnackbar(dashboardLaunch.dispatch.message)
                return@launch
            }

            val dashboardResult = dashboardLaunch.result?.await()
            val dashboardUrl = extractDashboardUrl(dashboardResult)
            val failureMessage = buildDashboardFailureMessage(dashboardResult, dashboardUrl)
            val previousDashboardUrlSummary = lastDashboardUrlSummary
            val dashboardUrlSummary = dashboardUrl?.let {
                buildDashboardUrlSummary(
                    dashboardUrl = it,
                    previousSummary = previousDashboardUrlSummary,
                )
            }

            if (dashboardUrl != null && isAllowedDashboardUrlStrict(dashboardUrl)) {
                lastDashboardUrlSummary = dashboardUrlSummary
                chatEntryState = OpenClawChatEntryState(
                    dashboardUrl = dashboardUrl,
                    chatAttemptId = chatAttemptId,
                    currentDashboardUrlSummary = dashboardUrlSummary,
                    previousDashboardUrlSummary = previousDashboardUrlSummary,
                )
            } else {
                chatEntryState = OpenClawChatEntryState(
                    errorMessage = failureMessage,
                    failureStage = OpenClawChatFailureStage.DashboardUrlUnavailable,
                    chatAttemptId = chatAttemptId,
                    currentDashboardUrlSummary = dashboardUrlSummary,
                    previousDashboardUrlSummary = previousDashboardUrlSummary,
                )
                snackbarHostState.showSnackbar(failureMessage)
            }
        }
    }

    fun navigateBack() {
        if (currentScreen == OpenClawDestination.Chat) {
            chatEntryState = chatEntryState.copy(isLoadingDashboardUrl = false)
        }
        if (!navController.popBackStack()) {
            navController.navigateToTopLevel(OpenClawDestination.Home)
        }
    }

    LaunchedEffect(Unit) {
        refreshGatewayStatus()
    }

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                refreshGatewayStatus()
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(text = currentScreen.title) },
                navigationIcon = {
                    if (!isTopLevelScreen) {
                        IconButton(onClick = ::navigateBack) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "返回",
                            )
                        }
                    }
                },
            )
        },
        bottomBar = {
            if (isTopLevelScreen) {
                NavigationBar {
                    OpenClawDestination.topLevelDestinations.forEach { destination ->
                        val selected = currentDestination?.hierarchy?.any { it.route == destination.route } == true
                        NavigationBarItem(
                            selected = selected,
                            onClick = { navController.navigateToTopLevel(destination) },
                            icon = { destination.icon() },
                            label = { Text(text = destination.label) },
                        )
                    }
                }
            }
        },
        snackbarHost = {
            SnackbarHost(hostState = snackbarHostState)
        },
        contentWindowInsets = WindowInsets(0, 0, 0, 0),
    ) { innerPadding ->
        OpenClawNavHost(
            navController = navController,
            placeholderState = placeholderState,
            gatewaySnapshot = gatewaySnapshot,
            launchSnapshot = launchSnapshot,
            chatEntryState = chatEntryState,
            onRefreshGatewayStatus = ::refreshGatewayStatus,
            modifier = Modifier.padding(innerPadding),
            onStartOpenClawClick = ::startOpenClaw,
            onOpenDashboardClick = ::loadChatEntry,
            onRetryChatClick = ::loadChatEntry,
            onBackFromChatClick = ::navigateBack,
        )
    }
}

private fun extractDashboardUrl(result: OpenClawTermuxCommandResult?): String? {
    if (result == null) return null
    val candidates = listOfNotNull(result.stdout, result.stderr, result.errorMessage)
    return candidates.firstNotNullOfOrNull { text ->
        DashboardUrlPattern.find(text)?.value
    }
}

private fun buildDashboardFailureMessage(
    result: OpenClawTermuxCommandResult?,
    dashboardUrl: String?,
): String {
    if (!dashboardUrl.isNullOrBlank() && !isAllowedDashboardUrlStrict(dashboardUrl)) {
        return "Dashboard 地址不是允许的本机地址。"
    }

    val rawMessage = listOfNotNull(
        result?.errorMessage,
        result?.stderr?.takeIf { it.isNotBlank() },
        result?.stdout?.takeIf { it.isNotBlank() },
    ).firstOrNull()?.lineSequence()?.firstOrNull()?.trim()

    if (!rawMessage.isNullOrBlank()) {
        return "未能获取可用的 Dashboard 地址：$rawMessage"
    }

    return "未能从 openclaw dashboard 获取带 token 的本机聊天地址。"
}

private fun buildDashboardUrlSummary(
    dashboardUrl: String,
    previousSummary: DashboardUrlSummary?,
): DashboardUrlSummary {
    val maskedUrl = maskDashboardUrlForSummary(dashboardUrl)
    val token = DashboardUrlPattern.find(dashboardUrl)?.value
        ?.substringAfter("#token=")
        ?.substringBefore('&')
        .orEmpty()
    val tokenSummary = if (token.length <= 8) "***" else "${token.take(4)}***${token.takeLast(4)}"
    return DashboardUrlSummary(
        requestedAt = java.time.LocalTime.now().format(java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss")),
        maskedUrl = maskedUrl,
        tokenSummary = tokenSummary,
        sameAsPrevious = previousSummary?.tokenSummary == tokenSummary && previousSummary.maskedUrl == maskedUrl,
    )
}

private fun maskDashboardUrlForSummary(url: String): String =
    Regex("(#token=)([^&]+)").replace(url) { match ->
        val token = match.groupValues[2]
        val maskedToken = if (token.length <= 8) "***" else "${token.take(4)}***${token.takeLast(4)}"
        "${match.groupValues[1]}$maskedToken"
    }

private fun generateChatAttemptId(): String =
    "chat-${System.currentTimeMillis().toString(16)}"
