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
import com.openclaw.android.nativeentry.ui.shell.AnalysisReportScreen
import com.openclaw.android.nativeentry.ui.shell.AnalysisResultScreen
import com.openclaw.android.nativeentry.ui.shell.HistoryScreen
import com.openclaw.android.nativeentry.ui.shell.ProductLearningScreen
import com.openclaw.android.nativeentry.ui.shell.ProductProfileScreen
import com.openclaw.android.nativeentry.ui.shell.V1ShellPlaceholderState

@Composable
fun OpenClawNavHost(
    navController: NavHostController,
    placeholderState: V1ShellPlaceholderState,
    gatewaySnapshot: GatewayCheckSnapshot,
    launchSnapshot: OpenClawLaunchSnapshot,
    chatEntryState: OpenClawChatEntryState,
    onRefreshGatewayStatus: () -> Unit,
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
                placeholderState = placeholderState,
                onStartAnalysisClick = { navController.navigate(OpenClawDestination.ProductLearning.route) },
                onContinueFlowClick = { navController.navigate(OpenClawDestination.ProductProfile.route) },
                onViewHistoryClick = { navController.navigateToTopLevel(OpenClawDestination.History) },
                onViewLatestAnalysisClick = { navController.navigate(OpenClawDestination.AnalysisResult.route) },
                onViewLatestReportClick = { navController.navigate(OpenClawDestination.AnalysisReport.route) },
                onViewOpsClick = { navController.navigateToTopLevel(OpenClawDestination.Ops) },
            )
        }
        composable(OpenClawDestination.History.route) {
            HistoryScreen(
                placeholderState = placeholderState,
                onOpenProductProfileClick = { navController.navigate(OpenClawDestination.ProductProfile.route) },
                onOpenAnalysisResultClick = { navController.navigate(OpenClawDestination.AnalysisResult.route) },
                onOpenAnalysisReportClick = { navController.navigate(OpenClawDestination.AnalysisReport.route) },
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
                placeholderState = placeholderState,
                onContinueClick = { navController.navigate(OpenClawDestination.ProductProfile.route) },
                onOpenOpsClick = { navController.navigateToTopLevel(OpenClawDestination.Ops) },
            )
        }
        composable(OpenClawDestination.ProductProfile.route) {
            ProductProfileScreen(
                placeholderState = placeholderState,
                onContinueClick = { navController.navigate(OpenClawDestination.AnalysisResult.route) },
            )
        }
        composable(OpenClawDestination.AnalysisResult.route) {
            AnalysisResultScreen(
                placeholderState = placeholderState,
                onContinueClick = { navController.navigate(OpenClawDestination.AnalysisReport.route) },
            )
        }
        composable(OpenClawDestination.AnalysisReport.route) {
            AnalysisReportScreen(
                placeholderState = placeholderState,
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
