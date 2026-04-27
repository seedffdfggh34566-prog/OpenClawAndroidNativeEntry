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
import com.openclaw.android.nativeentry.data.backend.AnalysisRunCreateRequestDto
import com.openclaw.android.nativeentry.data.backend.BackendReadError
import com.openclaw.android.nativeentry.data.backend.BackendReadResult
import com.openclaw.android.nativeentry.data.backend.HistoryResponseDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileCreateRequestDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileEnrichRequestDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileEnrichResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceBackendClient
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceChatTurnResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDemoWorkspaceId
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewApplyResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceReadOnlySnapshot
import com.openclaw.android.nativeentry.data.backend.V1BackendClient
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
import com.openclaw.android.nativeentry.ui.shell.V1BackendUiState
import com.openclaw.android.nativeentry.ui.shell.V1SectionState
import com.openclaw.android.nativeentry.ui.shell.sampleV1ShellPlaceholderState
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private const val GatewayLaunchTimeoutMillis = 75_000L
private const val GatewayLaunchPollIntervalMillis = 1_500L
private const val AnalysisRunPollAttempts = 30
private const val AnalysisRunPollIntervalMillis = 1_000L
private val DashboardUrlPattern = Regex("""http://127\.0\.0\.1:18789[^\s]*#token=[^\s]+""")

@Composable
fun OpenClawApp() {
    val context = LocalContext.current
    val navController = rememberNavController()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val lifecycleOwner = LocalLifecycleOwner.current
    val backendClient = remember { V1BackendClient() }
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val currentScreen = OpenClawDestination.fromRoute(currentDestination?.route) ?: OpenClawDestination.Home
    val isTopLevelScreen = OpenClawDestination.topLevelDestinations.any { it.route == currentScreen.route }
    val placeholderState = remember { sampleV1ShellPlaceholderState() }
    val workspaceClient = remember { SalesWorkspaceBackendClient() }
    var backendState by remember { mutableStateOf(V1BackendUiState()) }
    var workspaceState by remember {
        mutableStateOf<V1SectionState<SalesWorkspaceReadOnlySnapshot>>(V1SectionState.Idle)
    }
    var draftReviewState by remember {
        mutableStateOf<V1SectionState<SalesWorkspaceDraftReviewDto>>(V1SectionState.Idle)
    }
    var patchDraftApplyState by remember {
        mutableStateOf<V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>>(V1SectionState.Idle)
    }
    var chatFirstTurnState by remember {
        mutableStateOf<V1SectionState<SalesWorkspaceChatTurnResponseDto>>(V1SectionState.Idle)
    }
    var workspaceChatInput by remember { mutableStateOf("") }
    var workspaceChatMessageType by remember { mutableStateOf("product_profile_update") }
    var productName by remember { mutableStateOf("") }
    var productDescription by remember { mutableStateOf("") }
    var sourceNotes by remember { mutableStateOf("") }
    var supplementalNotes by remember { mutableStateOf("") }
    var gatewaySnapshot by remember { mutableStateOf(GatewayCheckSnapshot()) }
    var launchSnapshot by remember { mutableStateOf(OpenClawLaunchSnapshot()) }
    var chatEntryState by remember { mutableStateOf(OpenClawChatEntryState()) }
    var lastDashboardUrlSummary by remember { mutableStateOf<DashboardUrlSummary?>(null) }
    var latestRefreshToken by remember { mutableIntStateOf(0) }
    var refreshJob by remember { mutableStateOf<Job?>(null) }
    var backendRefreshJob by remember { mutableStateOf<Job?>(null) }
    var workspaceLoadJob by remember { mutableStateOf<Job?>(null) }
    var draftReviewJob by remember { mutableStateOf<Job?>(null) }
    var patchDraftApplyJob by remember { mutableStateOf<Job?>(null) }
    var chatFirstTurnJob by remember { mutableStateOf<Job?>(null) }
    var productProfileLoadJob by remember { mutableStateOf<Job?>(null) }
    var productProfileCreateJob by remember { mutableStateOf<Job?>(null) }
    var productProfileEnrichJob by remember { mutableStateOf<Job?>(null) }
    var analysisRunJob by remember { mutableStateOf<Job?>(null) }
    var reportRunJob by remember { mutableStateOf<Job?>(null) }
    var reportLoadJob by remember { mutableStateOf<Job?>(null) }
    var analysisResultLoadJob by remember { mutableStateOf<Job?>(null) }
    var launchPollingJob by remember { mutableStateOf<Job?>(null) }
    val loadedHistory = backendState.loadedHistory()
    val latestProductProfileId = loadedHistory?.latestProductProfile?.id
    val latestReportId = loadedHistory?.latestReport?.id
    val latestAnalysisResultId = loadedHistory?.latestAnalysisResult?.id

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

    fun useDebugFallback() {
        backendState = backendState.copy(isDebugFallbackEnabled = true)
    }

    fun refreshV1History() {
        backendRefreshJob?.cancel()
        backendState = backendState.copy(
            history = V1SectionState.Loading,
            productProfile = V1SectionState.Idle,
            productProfileConfirm = V1SectionState.Idle,
            productProfileEnrich = V1SectionState.Idle,
            productLearningRun = V1SectionState.Idle,
            report = V1SectionState.Idle,
            isDebugFallbackEnabled = false,
        )
        backendRefreshJob = scope.launch {
            when (val result = backendClient.getHistory()) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(history = V1SectionState.Failed(result.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        history = if (result.value.isEmpty) {
                            V1SectionState.Empty
                        } else {
                            V1SectionState.Loaded(result.value)
                        },
                    )
                }
            }
        }
    }

    fun refreshSalesWorkspace() {
        workspaceLoadJob?.cancel()
        workspaceState = V1SectionState.Loading
        workspaceLoadJob = scope.launch {
            workspaceState = when (val result = workspaceClient.getReadOnlySnapshot(SalesWorkspaceDemoWorkspaceId)) {
                is BackendReadResult.Failure -> V1SectionState.Failed(result.error)
                is BackendReadResult.Success -> V1SectionState.Loaded(result.value)
            }
        }
    }

    fun createDraftReviewFromRuntimePreview() {
        val loadedWorkspace = (workspaceState as? V1SectionState.Loaded<SalesWorkspaceReadOnlySnapshot>)
            ?.value
            ?.workspace
        if (loadedWorkspace == null) {
            draftReviewState = V1SectionState.Failed(
                BackendReadError(
                    title = "无法生成 Draft Review",
                    detail = "请先刷新并加载 Sales Workspace。",
                ),
            )
            return
        }

        draftReviewJob?.cancel()
        patchDraftApplyState = V1SectionState.Idle
        draftReviewState = V1SectionState.Loading
        draftReviewJob = scope.launch {
            draftReviewState = when (
                val result = workspaceClient.createDraftReviewFromRuntimePreview(
                    workspaceId = loadedWorkspace.id,
                    baseWorkspaceVersion = loadedWorkspace.workspaceVersion,
                )
            ) {
                is BackendReadResult.Failure -> V1SectionState.Failed(result.error)
                is BackendReadResult.Success -> V1SectionState.Loaded(result.value)
            }
        }
    }

    fun submitChatFirstWorkspaceTurn() {
        val loadedWorkspace = (workspaceState as? V1SectionState.Loaded<SalesWorkspaceReadOnlySnapshot>)
            ?.value
            ?.workspace
        if (loadedWorkspace == null) {
            chatFirstTurnState = V1SectionState.Failed(
                BackendReadError(
                    title = "无法提交 chat-first 输入",
                    detail = "请先刷新并加载 Sales Workspace。",
                ),
            )
            return
        }
        val content = workspaceChatInput.trim()
        if (content.isBlank()) {
            chatFirstTurnState = V1SectionState.Failed(
                BackendReadError(
                    title = "无法提交 chat-first 输入",
                    detail = "请输入产品信息或获客方向。",
                ),
            )
            return
        }

        chatFirstTurnJob?.cancel()
        patchDraftApplyState = V1SectionState.Idle
        draftReviewState = V1SectionState.Idle
        chatFirstTurnState = V1SectionState.Loading
        chatFirstTurnJob = scope.launch {
            when (
                val result = workspaceClient.runChatFirstSalesAgentTurn(
                    workspaceId = loadedWorkspace.id,
                    baseWorkspaceVersion = loadedWorkspace.workspaceVersion,
                    messageType = workspaceChatMessageType,
                    content = content,
                )
            ) {
                is BackendReadResult.Failure -> chatFirstTurnState = V1SectionState.Failed(result.error)
                is BackendReadResult.Success -> {
                    chatFirstTurnState = V1SectionState.Loaded(result.value)
                    draftReviewState = result.value.draftReview?.let { V1SectionState.Loaded(it) } ?: V1SectionState.Empty
                    workspaceChatInput = ""
                }
            }
        }
    }

    fun acceptDraftReview() {
        val draftReview = (draftReviewState as? V1SectionState.Loaded<SalesWorkspaceDraftReviewDto>)
            ?.value
        if (draftReview == null) {
            draftReviewState = V1SectionState.Failed(
                BackendReadError(
                    title = "无法审阅 Draft Review",
                    detail = "请先生成 Draft Review。",
                ),
            )
            return
        }

        draftReviewJob?.cancel()
        patchDraftApplyState = V1SectionState.Idle
        draftReviewState = V1SectionState.Loading
        draftReviewJob = scope.launch {
            draftReviewState = when (
                val result = workspaceClient.reviewDraftReview(
                    workspaceId = draftReview.workspaceId,
                    draftReviewId = draftReview.id,
                    decision = "accept",
                )
            ) {
                is BackendReadResult.Failure -> V1SectionState.Failed(result.error)
                is BackendReadResult.Success -> V1SectionState.Loaded(result.value)
            }
        }
    }

    fun rejectDraftReview() {
        val draftReview = (draftReviewState as? V1SectionState.Loaded<SalesWorkspaceDraftReviewDto>)
            ?.value
        if (draftReview == null) {
            draftReviewState = V1SectionState.Failed(
                BackendReadError(
                    title = "无法拒绝 Draft Review",
                    detail = "请先生成 Draft Review。",
                ),
            )
            return
        }

        draftReviewJob?.cancel()
        patchDraftApplyState = V1SectionState.Idle
        draftReviewState = V1SectionState.Loading
        draftReviewJob = scope.launch {
            draftReviewState = when (
                val result = workspaceClient.rejectDraftReview(
                    workspaceId = draftReview.workspaceId,
                    draftReviewId = draftReview.id,
                )
            ) {
                is BackendReadResult.Failure -> V1SectionState.Failed(result.error)
                is BackendReadResult.Success -> V1SectionState.Loaded(result.value)
            }
        }
    }

    fun applyReviewedDraftReview() {
        val draftReview = (draftReviewState as? V1SectionState.Loaded<SalesWorkspaceDraftReviewDto>)
            ?.value
        if (draftReview == null) {
            patchDraftApplyState = V1SectionState.Failed(
                BackendReadError(
                    title = "无法应用 Draft Review",
                    detail = "请先生成并接受 Draft Review。",
                ),
            )
            return
        }

        patchDraftApplyJob?.cancel()
        patchDraftApplyState = V1SectionState.Loading
        patchDraftApplyJob = scope.launch {
            when (
                val result = workspaceClient.applyDraftReview(
                    workspaceId = draftReview.workspaceId,
                    draftReviewId = draftReview.id,
                )
            ) {
                is BackendReadResult.Failure -> {
                    patchDraftApplyState = V1SectionState.Failed(result.error)
                }

                is BackendReadResult.Success -> {
                    patchDraftApplyState = V1SectionState.Loaded(result.value)
                    draftReviewState = V1SectionState.Idle
                    workspaceState = V1SectionState.Loading
                    workspaceState = when (
                        val snapshot = workspaceClient.getReadOnlySnapshot(result.value.workspace.id)
                    ) {
                        is BackendReadResult.Failure -> V1SectionState.Failed(snapshot.error)
                        is BackendReadResult.Success -> V1SectionState.Loaded(snapshot.value)
                    }
                }
            }
        }
    }

    fun loadLatestProductProfile() {
        val profileId = backendState.loadedHistory()?.latestProductProfile?.id
        if (profileId.isNullOrBlank()) {
            backendState = backendState.copy(productProfile = V1SectionState.Empty)
            return
        }

        productProfileLoadJob?.cancel()
        backendState = backendState.copy(productProfile = V1SectionState.Loading)
        productProfileLoadJob = scope.launch {
            when (val result = backendClient.getProductProfile(profileId)) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(productProfile = V1SectionState.Failed(result.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(productProfile = V1SectionState.Loaded(result.value))
                }
            }
        }
    }

    fun loadLatestReport() {
        val reportId = backendState.loadedHistory()?.latestReport?.id
        if (reportId.isNullOrBlank()) {
            backendState = backendState.copy(report = V1SectionState.Empty)
            return
        }

        reportLoadJob?.cancel()
        backendState = backendState.copy(report = V1SectionState.Loading)
        reportLoadJob = scope.launch {
            when (val result = backendClient.getReport(reportId)) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(report = V1SectionState.Failed(result.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(report = V1SectionState.Loaded(result.value))
                }
            }
        }
    }

    fun loadLatestAnalysisResult() {
        val analysisResultId = backendState.loadedHistory()?.latestAnalysisResult?.id
        if (analysisResultId.isNullOrBlank()) {
            backendState = backendState.copy(analysisResult = V1SectionState.Empty)
            return
        }

        analysisResultLoadJob?.cancel()
        backendState = backendState.copy(analysisResult = V1SectionState.Loading)
        analysisResultLoadJob = scope.launch {
            when (val result = backendClient.getLeadAnalysisResult(analysisResultId)) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(analysisResult = V1SectionState.Failed(result.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(analysisResult = V1SectionState.Loaded(result.value))
                }
            }
        }
    }

    fun submitProductProfile() {
        val trimmedName = productName.trim()
        val trimmedDescription = productDescription.trim()
        val trimmedSourceNotes = sourceNotes.trim()

        if (trimmedName.isBlank() || trimmedDescription.isBlank()) {
            return
        }

        productProfileCreateJob?.cancel()
        backendState = backendState.copy(
            productProfileCreate = V1SectionState.Loading,
            productLearningRun = V1SectionState.Idle,
        )
        productProfileCreateJob = scope.launch {
            val createResult = backendClient.createProductProfile(
                ProductProfileCreateRequestDto(
                    name = trimmedName,
                    oneLineDescription = trimmedDescription,
                    sourceNotes = trimmedSourceNotes.ifBlank { null },
                ),
            )

            when (createResult) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(
                        productProfileCreate = V1SectionState.Failed(createResult.error),
                    )
                }

                is BackendReadResult.Success -> {
                    val createPayload = createResult.value
                    val createdProfile = createPayload.productProfile
                    backendState = backendState.copy(
                        productProfileCreate = V1SectionState.Loaded(createPayload),
                        productProfile = V1SectionState.Loading,
                        productProfileConfirm = V1SectionState.Idle,
                        productLearningRun = if (createPayload.currentRun != null) {
                            V1SectionState.Loading
                        } else {
                            V1SectionState.Idle
                        },
                    )

                    val currentRun = createPayload.currentRun
                    if (currentRun != null) {
                        var finalSucceeded = false
                        var attempt = 0
                        while (attempt < AnalysisRunPollAttempts && !finalSucceeded) {
                            when (val detailResult = backendClient.getAnalysisRun(currentRun.id)) {
                                is BackendReadResult.Failure -> {
                                    backendState = backendState.copy(
                                        productLearningRun = V1SectionState.Failed(detailResult.error),
                                    )
                                    return@launch
                                }

                                is BackendReadResult.Success -> {
                                    backendState = backendState.copy(
                                        productLearningRun = V1SectionState.Loaded(detailResult.value),
                                    )
                                    val run = detailResult.value.agentRun
                                    if (run.status == "succeeded") {
                                        finalSucceeded = true
                                    } else if (run.status == "failed" || run.status == "cancelled") {
                                        backendState = backendState.copy(
                                            productLearningRun = V1SectionState.Failed(
                                                BackendReadError(
                                                    title = "产品学习运行未成功",
                                                    detail = run.errorMessage
                                                        ?: "product_learning 已进入 ${run.status} 状态。",
                                                ),
                                            ),
                                        )
                                        return@launch
                                    }
                                }
                            }

                            attempt += 1
                            if (attempt < AnalysisRunPollAttempts && !finalSucceeded) {
                                delay(AnalysisRunPollIntervalMillis)
                            }
                        }

                        if (!finalSucceeded) {
                            backendState = backendState.copy(
                                productLearningRun = V1SectionState.Failed(
                                    BackendReadError(
                                        title = "产品学习运行未在轮询窗口内完成",
                                        detail = "请稍后重新进入产品画像页查看最新状态。",
                                    ),
                                ),
                            )
                            return@launch
                        }
                    }

                    when (val profileResult = backendClient.getProductProfile(createdProfile.id)) {
                        is BackendReadResult.Failure -> {
                            backendState = backendState.copy(
                                productProfile = V1SectionState.Failed(profileResult.error),
                            )
                            return@launch
                        }

                        is BackendReadResult.Success -> {
                            backendState = backendState.copy(
                                productProfile = V1SectionState.Loaded(profileResult.value),
                            )
                        }
                    }

                    when (val historyResult = backendClient.getHistory()) {
                        is BackendReadResult.Failure -> {
                            backendState = backendState.copy(
                                history = V1SectionState.Failed(historyResult.error),
                            )
                        }

                        is BackendReadResult.Success -> {
                            backendState = backendState.copy(
                                history = if (historyResult.value.isEmpty) {
                                    V1SectionState.Empty
                                } else {
                                    V1SectionState.Loaded(historyResult.value)
                                },
                                isDebugFallbackEnabled = false,
                            )
                        }
                    }
                }
            }
        }
    }

    fun submitProductProfileEnrich() {
        val profileId = when (val profileState = backendState.productProfile) {
            is V1SectionState.Loaded -> profileState.value.id
            else -> backendState.loadedHistory()?.latestProductProfile?.id
        }
        val trimmedNotes = supplementalNotes.trim()

        if (profileId.isNullOrBlank()) {
            backendState = backendState.copy(productProfileEnrich = V1SectionState.Empty)
            return
        }

        if (trimmedNotes.isBlank()) {
            return
        }

        productProfileEnrichJob?.cancel()
        backendState = backendState.copy(
            productProfileEnrich = V1SectionState.Loading,
            productLearningRun = V1SectionState.Idle,
            productProfileConfirm = V1SectionState.Idle,
        )
        productProfileEnrichJob = scope.launch {
            val enrichResult = backendClient.enrichProductProfile(
                id = profileId,
                payload = ProductProfileEnrichRequestDto(
                    supplementalNotes = trimmedNotes,
                    triggerSource = "android_product_learning_iteration",
                ),
            )

            val runId = when (enrichResult) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(
                        productProfileEnrich = V1SectionState.Failed(enrichResult.error),
                    )
                    return@launch
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        productProfileEnrich = V1SectionState.Loaded(enrichResult.value),
                        productLearningRun = V1SectionState.Loading,
                    )
                    enrichResult.value.agentRun.id
                }
            }

            var finalSucceeded = false
            var attempt = 0
            while (attempt < AnalysisRunPollAttempts && !finalSucceeded) {
                when (val detailResult = backendClient.getAnalysisRun(runId)) {
                    is BackendReadResult.Failure -> {
                        backendState = backendState.copy(
                            productLearningRun = V1SectionState.Failed(detailResult.error),
                        )
                        return@launch
                    }

                    is BackendReadResult.Success -> {
                        backendState = backendState.copy(
                            productProfileEnrich = V1SectionState.Loaded(
                                ProductProfileEnrichResponseDto(detailResult.value.agentRun),
                            ),
                            productLearningRun = V1SectionState.Loaded(detailResult.value),
                        )
                        val run = detailResult.value.agentRun
                        if (run.status == "succeeded") {
                            finalSucceeded = true
                        } else if (run.status == "failed" || run.status == "cancelled") {
                            backendState = backendState.copy(
                                productLearningRun = V1SectionState.Failed(
                                    BackendReadError(
                                        title = "产品学习补充未成功",
                                        detail = run.errorMessage
                                            ?: "product_learning 已进入 ${run.status} 状态。",
                                    ),
                                ),
                            )
                            return@launch
                        }
                    }
                }

                attempt += 1
                if (attempt < AnalysisRunPollAttempts && !finalSucceeded) {
                    delay(AnalysisRunPollIntervalMillis)
                }
            }

            if (!finalSucceeded) {
                backendState = backendState.copy(
                    productLearningRun = V1SectionState.Failed(
                        BackendReadError(
                            title = "产品学习补充未在轮询窗口内完成",
                            detail = "请稍后刷新产品学习页或产品画像页查看最新状态。",
                        ),
                    ),
                )
                return@launch
            }

            backendState = backendState.copy(productProfile = V1SectionState.Loading)
            when (val profileResult = backendClient.getProductProfile(profileId)) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(
                        productProfile = V1SectionState.Failed(profileResult.error),
                    )
                    return@launch
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        productProfile = V1SectionState.Loaded(profileResult.value),
                    )
                    supplementalNotes = ""
                }
            }

            when (val historyResult = backendClient.getHistory()) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(history = V1SectionState.Failed(historyResult.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        history = if (historyResult.value.isEmpty) {
                            V1SectionState.Empty
                        } else {
                            V1SectionState.Loaded(historyResult.value)
                        },
                        isDebugFallbackEnabled = false,
                    )
                }
            }
        }
    }

    fun confirmProductProfile() {
        val profileId = when (val profileState = backendState.productProfile) {
            is V1SectionState.Loaded -> profileState.value.id
            else -> backendState.loadedHistory()?.latestProductProfile?.id
        }

        if (profileId.isNullOrBlank()) {
            backendState = backendState.copy(productProfileConfirm = V1SectionState.Empty)
            return
        }

        backendState = backendState.copy(productProfileConfirm = V1SectionState.Loading)
        scope.launch {
            when (val result = backendClient.confirmProductProfile(profileId)) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(productProfileConfirm = V1SectionState.Failed(result.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        productProfileConfirm = V1SectionState.Loaded(result.value),
                        productProfile = V1SectionState.Loading,
                    )
                    when (val profileResult = backendClient.getProductProfile(profileId)) {
                        is BackendReadResult.Failure -> {
                            backendState = backendState.copy(
                                productProfile = V1SectionState.Failed(profileResult.error),
                            )
                        }

                        is BackendReadResult.Success -> {
                            backendState = backendState.copy(
                                productProfile = V1SectionState.Loaded(profileResult.value),
                            )
                        }
                    }

                    when (val historyResult = backendClient.getHistory()) {
                        is BackendReadResult.Failure -> {
                            backendState = backendState.copy(
                                history = V1SectionState.Failed(historyResult.error),
                            )
                        }

                        is BackendReadResult.Success -> {
                            backendState = backendState.copy(
                                history = if (historyResult.value.isEmpty) {
                                    V1SectionState.Empty
                                } else {
                                    V1SectionState.Loaded(historyResult.value)
                                },
                                isDebugFallbackEnabled = false,
                            )
                        }
                    }
                }
            }
        }
    }

    fun triggerLeadAnalysis() {
        val profileId = when (val profileState = backendState.productProfile) {
            is V1SectionState.Loaded -> profileState.value.id
            else -> backendState.loadedHistory()?.latestProductProfile?.id
        }

        if (profileId.isNullOrBlank()) {
            backendState = backendState.copy(analysisRun = V1SectionState.Empty)
            return
        }

        analysisRunJob?.cancel()
        backendState = backendState.copy(analysisRun = V1SectionState.Loading)
        analysisRunJob = scope.launch {
            val createResult = backendClient.createAnalysisRun(
                AnalysisRunCreateRequestDto(
                    runType = "lead_analysis",
                    productProfileId = profileId,
                    leadAnalysisResultId = null,
                    triggerSource = "android_product_profile",
                ),
            )

            val runId = when (createResult) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(
                        analysisRun = V1SectionState.Failed(createResult.error),
                    )
                    return@launch
                }

                is BackendReadResult.Success -> {
                    createResult.value.agentRun.id
                }
            }

            var finalSucceeded = false
            var attempt = 0
            while (attempt < AnalysisRunPollAttempts && !finalSucceeded) {
                val detailResult = backendClient.getAnalysisRun(runId)
                when (detailResult) {
                    is BackendReadResult.Failure -> {
                        backendState = backendState.copy(
                            analysisRun = V1SectionState.Failed(detailResult.error),
                        )
                        return@launch
                    }

                    is BackendReadResult.Success -> {
                        backendState = backendState.copy(
                            analysisRun = V1SectionState.Loaded(detailResult.value),
                        )

                        val run = detailResult.value.agentRun
                        if (run.status == "succeeded") {
                            finalSucceeded = true
                        } else if (run.status == "failed" || run.status == "cancelled") {
                            return@launch
                        }
                    }
                }

                attempt += 1
                if (attempt < AnalysisRunPollAttempts && !finalSucceeded) {
                    delay(AnalysisRunPollIntervalMillis)
                }
            }

            if (!finalSucceeded) {
                return@launch
            }

            when (val historyResult = backendClient.getHistory()) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(history = V1SectionState.Failed(historyResult.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        history = if (historyResult.value.isEmpty) {
                            V1SectionState.Empty
                        } else {
                            V1SectionState.Loaded(historyResult.value)
                        },
                        isDebugFallbackEnabled = false,
                    )
                }
            }

            navController.navigate(OpenClawDestination.AnalysisResult.route) {
                launchSingleTop = true
            }
        }
    }

    fun triggerReportGeneration() {
        val history = backendState.loadedHistory()
        val profileId = history?.latestProductProfile?.id
        val analysisResultId = history?.latestAnalysisResult?.id

        if (profileId.isNullOrBlank() || analysisResultId.isNullOrBlank()) {
            backendState = backendState.copy(reportRun = V1SectionState.Empty)
            return
        }

        reportRunJob?.cancel()
        backendState = backendState.copy(reportRun = V1SectionState.Loading)
        reportRunJob = scope.launch {
            val createResult = backendClient.createAnalysisRun(
                AnalysisRunCreateRequestDto(
                    runType = "report_generation",
                    productProfileId = profileId,
                    leadAnalysisResultId = analysisResultId,
                    triggerSource = "android_analysis_result",
                ),
            )

            val runId = when (createResult) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(reportRun = V1SectionState.Failed(createResult.error))
                    return@launch
                }

                is BackendReadResult.Success -> createResult.value.agentRun.id
            }

            var finalReportId: String? = null
            var attempt = 0
            while (attempt < AnalysisRunPollAttempts && finalReportId == null) {
                val detailResult = backendClient.getAnalysisRun(runId)
                when (detailResult) {
                    is BackendReadResult.Failure -> {
                        backendState = backendState.copy(reportRun = V1SectionState.Failed(detailResult.error))
                        return@launch
                    }

                    is BackendReadResult.Success -> {
                        backendState = backendState.copy(reportRun = V1SectionState.Loaded(detailResult.value))

                        val run = detailResult.value.agentRun
                        if (run.status == "succeeded") {
                            finalReportId = detailResult.value.resultSummary["report_id"]
                        } else if (run.status == "failed" || run.status == "cancelled") {
                            backendState = backendState.copy(
                                reportRun = V1SectionState.Failed(
                                    BackendReadError(
                                        title = "报告生成未成功",
                                        detail = run.errorMessage ?: "report_generation 已进入 ${run.status} 状态。",
                                    ),
                                ),
                            )
                            return@launch
                        }
                    }
                }

                attempt += 1
                if (attempt < AnalysisRunPollAttempts && finalReportId == null) {
                    delay(AnalysisRunPollIntervalMillis)
                }
            }

            val reportId = finalReportId
            if (reportId.isNullOrBlank()) {
                backendState = backendState.copy(
                    reportRun = V1SectionState.Failed(
                        BackendReadError(
                            title = "报告生成未返回报告 ID",
                            detail = "report_generation 未在轮询窗口内返回 result_summary.report_id。",
                        ),
                    ),
                )
                return@launch
            }

            backendState = backendState.copy(report = V1SectionState.Loading)
            when (val reportResult = backendClient.getReport(reportId)) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(report = V1SectionState.Failed(reportResult.error))
                    return@launch
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(report = V1SectionState.Loaded(reportResult.value))
                }
            }

            when (val historyResult = backendClient.getHistory()) {
                is BackendReadResult.Failure -> {
                    backendState = backendState.copy(history = V1SectionState.Failed(historyResult.error))
                }

                is BackendReadResult.Success -> {
                    backendState = backendState.copy(
                        history = if (historyResult.value.isEmpty) {
                            V1SectionState.Empty
                        } else {
                            V1SectionState.Loaded(historyResult.value)
                        },
                        isDebugFallbackEnabled = false,
                    )
                }
            }

            navController.navigate(OpenClawDestination.AnalysisReport.route) {
                launchSingleTop = true
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
        refreshV1History()
    }

    LaunchedEffect(currentScreen, latestProductProfileId) {
        if (
            currentScreen == OpenClawDestination.ProductProfile ||
            currentScreen == OpenClawDestination.ProductLearning
        ) {
            loadLatestProductProfile()
        }
    }

    LaunchedEffect(currentScreen, latestReportId) {
        if (currentScreen == OpenClawDestination.AnalysisReport) {
            loadLatestReport()
        }
    }

    LaunchedEffect(currentScreen, latestAnalysisResultId) {
        if (currentScreen == OpenClawDestination.AnalysisResult) {
            loadLatestAnalysisResult()
        }
    }

    LaunchedEffect(currentScreen) {
        if (currentScreen == OpenClawDestination.Workspace && workspaceState !is V1SectionState.Loading) {
            refreshSalesWorkspace()
        }
    }

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                refreshGatewayStatus()
                refreshV1History()
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
            backendState = backendState,
            workspaceState = workspaceState,
            draftReviewState = draftReviewState,
            patchDraftApplyState = patchDraftApplyState,
            chatFirstTurnState = chatFirstTurnState,
            placeholderState = placeholderState,
            gatewaySnapshot = gatewaySnapshot,
            launchSnapshot = launchSnapshot,
            chatEntryState = chatEntryState,
            onRefreshGatewayStatus = ::refreshGatewayStatus,
            onRefreshBackend = ::refreshV1History,
            onRefreshWorkspace = ::refreshSalesWorkspace,
            onCreateDraftReview = ::createDraftReviewFromRuntimePreview,
            workspaceChatInput = workspaceChatInput,
            workspaceChatMessageType = workspaceChatMessageType,
            onWorkspaceChatInputChange = { workspaceChatInput = it },
            onWorkspaceChatMessageTypeChange = { workspaceChatMessageType = it },
            onSubmitWorkspaceChatTurn = ::submitChatFirstWorkspaceTurn,
            onAcceptDraftReview = ::acceptDraftReview,
            onRejectDraftReview = ::rejectDraftReview,
            onApplyDraftReview = ::applyReviewedDraftReview,
            onUseDebugFallback = ::useDebugFallback,
            onLoadLatestProductProfile = ::loadLatestProductProfile,
            onLoadLatestReport = ::loadLatestReport,
            onLoadLatestAnalysisResult = ::loadLatestAnalysisResult,
            onConfirmProductProfile = ::confirmProductProfile,
            productName = productName,
            productDescription = productDescription,
            sourceNotes = sourceNotes,
            supplementalNotes = supplementalNotes,
            onProductNameChange = { productName = it },
            onProductDescriptionChange = { productDescription = it },
            onSourceNotesChange = { sourceNotes = it },
            onSupplementalNotesChange = { supplementalNotes = it },
            onSubmitProductProfile = ::submitProductProfile,
            onSubmitProductProfileEnrich = ::submitProductProfileEnrich,
            onTriggerLeadAnalysis = ::triggerLeadAnalysis,
            onTriggerReportGeneration = ::triggerReportGeneration,
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

private fun V1BackendUiState.loadedHistory(): HistoryResponseDto? =
    (history as? V1SectionState.Loaded)?.value
