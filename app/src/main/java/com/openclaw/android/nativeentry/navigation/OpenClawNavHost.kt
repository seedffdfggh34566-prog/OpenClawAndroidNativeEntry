package com.openclaw.android.nativeentry.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.openclaw.android.nativeentry.ui.chat.OpenClawChatEntryState
import com.openclaw.android.nativeentry.ui.chat.OpenClawChatScreen
import com.openclaw.android.nativeentry.ui.home.GatewayCheckSnapshot
import com.openclaw.android.nativeentry.ui.home.HomeScreen
import com.openclaw.android.nativeentry.ui.home.OpenClawLaunchSnapshot
import com.openclaw.android.nativeentry.ui.logs.LogsScreen
import com.openclaw.android.nativeentry.ui.ops.OpsScreen
import com.openclaw.android.nativeentry.ui.settings.SettingsScreen
import com.openclaw.android.nativeentry.ui.workspace.SalesWorkspaceScreen
import com.openclaw.android.nativeentry.ui.shell.AnalysisReportScreen
import com.openclaw.android.nativeentry.ui.shell.AnalysisResultScreen
import com.openclaw.android.nativeentry.ui.shell.HistoryScreen
import com.openclaw.android.nativeentry.ui.shell.ProductLearningScreen
import com.openclaw.android.nativeentry.ui.shell.ProductProfileScreen
import com.openclaw.android.nativeentry.ui.shell.V1BackendUiState
import com.openclaw.android.nativeentry.data.backend.SalesWorkspacePatchDraftApplyResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspacePatchDraftPreviewDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceReadOnlySnapshot
import com.openclaw.android.nativeentry.ui.shell.V1ShellPlaceholderState
import com.openclaw.android.nativeentry.ui.shell.V1SectionState

@Composable
fun OpenClawNavHost(
    navController: NavHostController,
    backendState: V1BackendUiState,
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    patchDraftPreviewState: V1SectionState<SalesWorkspacePatchDraftPreviewDto>,
    patchDraftApplyState: V1SectionState<SalesWorkspacePatchDraftApplyResponseDto>,
    placeholderState: V1ShellPlaceholderState,
    gatewaySnapshot: GatewayCheckSnapshot,
    launchSnapshot: OpenClawLaunchSnapshot,
    chatEntryState: OpenClawChatEntryState,
    onRefreshGatewayStatus: () -> Unit,
    onRefreshBackend: () -> Unit,
    onRefreshWorkspace: () -> Unit,
    onPreviewRuntimePatchDraft: () -> Unit,
    onApplyReviewedRuntimePatchDraft: () -> Unit,
    onUseDebugFallback: () -> Unit,
    onLoadLatestProductProfile: () -> Unit,
    onLoadLatestReport: () -> Unit,
    onLoadLatestAnalysisResult: () -> Unit,
    onConfirmProductProfile: () -> Unit,
    productName: String,
    productDescription: String,
    sourceNotes: String,
    supplementalNotes: String,
    onProductNameChange: (String) -> Unit,
    onProductDescriptionChange: (String) -> Unit,
    onSourceNotesChange: (String) -> Unit,
    onSupplementalNotesChange: (String) -> Unit,
    onSubmitProductProfile: () -> Unit,
    onSubmitProductProfileEnrich: () -> Unit,
    onTriggerLeadAnalysis: () -> Unit,
    onTriggerReportGeneration: () -> Unit,
    modifier: Modifier = Modifier,
    onStartOpenClawClick: () -> Unit,
    onOpenDashboardClick: () -> Unit,
    onRetryChatClick: () -> Unit,
    onBackFromChatClick: () -> Unit,
) {
    NavHost(
        navController = navController,
        startDestination = OpenClawDestination.Home.route,
        modifier = modifier,
    ) {
        composable(OpenClawDestination.Home.route) {
            HomeScreen(
                backendState = backendState,
                placeholderState = placeholderState,
                onStartAnalysisClick = { navController.navigate(OpenClawDestination.ProductLearning.route) },
                onContinueFlowClick = { navController.navigate(OpenClawDestination.ProductProfile.route) },
                onViewHistoryClick = { navController.navigateToTopLevel(OpenClawDestination.History) },
                onViewLatestAnalysisClick = { navController.navigate(OpenClawDestination.AnalysisResult.route) },
                onViewLatestReportClick = { navController.navigate(OpenClawDestination.AnalysisReport.route) },
                onViewOpsClick = { navController.navigateToTopLevel(OpenClawDestination.Ops) },
                onRefreshBackendClick = onRefreshBackend,
                onUseDebugFallbackClick = onUseDebugFallback,
            )
        }
        composable(OpenClawDestination.History.route) {
            HistoryScreen(
                backendState = backendState,
                placeholderState = placeholderState,
                onOpenProductProfileClick = { navController.navigate(OpenClawDestination.ProductProfile.route) },
                onOpenAnalysisResultClick = { navController.navigate(OpenClawDestination.AnalysisResult.route) },
                onOpenAnalysisReportClick = { navController.navigate(OpenClawDestination.AnalysisReport.route) },
                onRefreshBackendClick = onRefreshBackend,
                onUseDebugFallbackClick = onUseDebugFallback,
            )
        }
        composable(OpenClawDestination.Workspace.route) {
            SalesWorkspaceScreen(
                workspaceState = workspaceState,
                patchDraftPreviewState = patchDraftPreviewState,
                patchDraftApplyState = patchDraftApplyState,
                onRefreshClick = onRefreshWorkspace,
                onPreviewClick = onPreviewRuntimePatchDraft,
                onApplyClick = onApplyReviewedRuntimePatchDraft,
            )
        }
        composable(OpenClawDestination.Ops.route) {
            OpsScreen(
                gatewaySnapshot = gatewaySnapshot,
                launchSnapshot = launchSnapshot,
                onRefreshGatewayStatus = onRefreshGatewayStatus,
                onStartOpenClawClick = onStartOpenClawClick,
                onOpenDashboardClick = onOpenDashboardClick,
                onViewDiagnosticsClick = { navController.navigate(OpenClawDestination.OpsDiagnostics.route) },
            )
        }
        composable(OpenClawDestination.Settings.route) {
            SettingsScreen()
        }
        composable(OpenClawDestination.ProductLearning.route) {
            ProductLearningScreen(
                backendState = backendState,
                placeholderState = placeholderState,
                productName = productName,
                productDescription = productDescription,
                sourceNotes = sourceNotes,
                supplementalNotes = supplementalNotes,
                onProductNameChange = onProductNameChange,
                onProductDescriptionChange = onProductDescriptionChange,
                onSourceNotesChange = onSourceNotesChange,
                onSupplementalNotesChange = onSupplementalNotesChange,
                onSubmitProductProfileClick = onSubmitProductProfile,
                onSubmitProductProfileEnrichClick = onSubmitProductProfileEnrich,
                onContinueClick = { navController.navigate(OpenClawDestination.ProductProfile.route) },
                onOpenOpsClick = { navController.navigateToTopLevel(OpenClawDestination.Ops) },
            )
        }
        composable(OpenClawDestination.ProductProfile.route) {
            ProductProfileScreen(
                backendState = backendState,
                placeholderState = placeholderState,
                onContinueClick = { navController.navigate(OpenClawDestination.AnalysisResult.route) },
                onRefreshClick = onLoadLatestProductProfile,
                onConfirmProductProfileClick = onConfirmProductProfile,
                onTriggerLeadAnalysisClick = onTriggerLeadAnalysis,
            )
        }
        composable(OpenClawDestination.AnalysisResult.route) {
            AnalysisResultScreen(
                backendState = backendState,
                placeholderState = placeholderState,
                onTriggerReportGenerationClick = onTriggerReportGeneration,
                onContinueClick = { navController.navigate(OpenClawDestination.AnalysisReport.route) },
                onRefreshClick = onLoadLatestAnalysisResult,
            )
        }
        composable(OpenClawDestination.AnalysisReport.route) {
            AnalysisReportScreen(
                backendState = backendState,
                placeholderState = placeholderState,
                onRefreshClick = onLoadLatestReport,
            )
        }
        composable(OpenClawDestination.OpsDiagnostics.route) {
            LogsScreen(
                gatewaySnapshot = gatewaySnapshot,
                launchSnapshot = launchSnapshot,
            )
        }
        composable(OpenClawDestination.Chat.route) {
            OpenClawChatScreen(
                chatEntryState = chatEntryState,
                onRetryClick = onRetryChatClick,
                onBackClick = onBackFromChatClick,
            )
        }
    }
}

fun NavHostController.navigateToTopLevel(destination: OpenClawDestination) {
    navigate(destination.route) {
        popUpTo(graph.findStartDestination().id) {
            saveState = true
        }
        launchSingleTop = true
        restoreState = true
    }
}
