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
import com.openclaw.android.nativeentry.ui.settings.SettingsScreen

@Composable
fun OpenClawNavHost(
    navController: NavHostController,
    gatewaySnapshot: GatewayCheckSnapshot,
    launchSnapshot: OpenClawLaunchSnapshot,
    chatEntryState: OpenClawChatEntryState,
    onRefreshGatewayStatus: () -> Unit,
    modifier: Modifier = Modifier,
    onStartOpenClawClick: () -> Unit,
    onEnterChatClick: () -> Unit,
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
                gatewaySnapshot = gatewaySnapshot,
                launchSnapshot = launchSnapshot,
                onRefreshGatewayStatus = onRefreshGatewayStatus,
                onStartOpenClawClick = onStartOpenClawClick,
                onEnterChatClick = onEnterChatClick,
            )
        }
        composable(OpenClawDestination.Logs.route) {
            LogsScreen(
                gatewaySnapshot = gatewaySnapshot,
                launchSnapshot = launchSnapshot,
            )
        }
        composable(OpenClawDestination.Settings.route) {
            SettingsScreen()
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
