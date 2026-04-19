package com.openclaw.android.nativeentry.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.ListAlt
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector

sealed class OpenClawDestination(
    val route: String,
    val title: String,
    val label: String,
    private val iconVector: ImageVector,
) {
    @Composable
    fun icon() {
        Icon(
            imageVector = iconVector,
            contentDescription = label,
        )
    }

    data object Home : OpenClawDestination(
        route = "home",
        title = "OpenClaw",
        label = "Home",
        iconVector = Icons.Outlined.Home,
    )

    data object Logs : OpenClawDestination(
        route = "logs",
        title = "Logs",
        label = "Logs",
        iconVector = Icons.Outlined.ListAlt,
    )

    data object Settings : OpenClawDestination(
        route = "settings",
        title = "Settings",
        label = "Settings",
        iconVector = Icons.Outlined.Settings,
    )

    data object Chat : OpenClawDestination(
        route = "chat",
        title = "聊天",
        label = "聊天",
        iconVector = Icons.Outlined.Home,
    )

    companion object {
        val topLevelDestinations = listOf(Home, Logs, Settings)
        private val allDestinations = topLevelDestinations + Chat

        fun fromRoute(route: String?): OpenClawDestination? =
            allDestinations.firstOrNull { it.route == route }
    }
}
