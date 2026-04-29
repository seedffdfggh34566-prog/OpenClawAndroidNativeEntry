package com.openclaw.android.nativeentry.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ListAlt
import androidx.compose.material.icons.outlined.Build
import androidx.compose.material.icons.outlined.History
import androidx.compose.material.icons.outlined.Home
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
        title = "AI 销售助手",
        label = "Home",
        iconVector = Icons.Outlined.Home,
    )

    data object History : OpenClawDestination(
        route = "history",
        title = "历史与状态",
        label = "History",
        iconVector = Icons.Outlined.History,
    )

    data object Workspace : OpenClawDestination(
        route = "workspace",
        title = "销售工作区",
        label = "销售工作区",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    data object Ops : OpenClawDestination(
        route = "ops",
        title = "运维与诊断",
        label = "Ops",
        iconVector = Icons.Outlined.Build,
    )

    data object Settings : OpenClawDestination(
        route = "settings",
        title = "设置",
        label = "Settings",
        iconVector = Icons.Outlined.Settings,
    )

    data object ProductLearning : OpenClawDestination(
        route = "product_learning",
        title = "产品学习",
        label = "产品学习",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    data object ProductProfile : OpenClawDestination(
        route = "product_profile",
        title = "产品画像",
        label = "产品画像",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    data object AnalysisResult : OpenClawDestination(
        route = "analysis_result",
        title = "分析结果",
        label = "分析结果",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    data object AnalysisReport : OpenClawDestination(
        route = "analysis_report",
        title = "分析报告",
        label = "分析报告",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    data object OpsDiagnostics : OpenClawDestination(
        route = "ops_diagnostics",
        title = "详细诊断",
        label = "详细诊断",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    data object Chat : OpenClawDestination(
        route = "chat",
        title = "Dashboard",
        label = "Dashboard",
        iconVector = Icons.AutoMirrored.Outlined.ListAlt,
    )

    companion object {
        val topLevelDestinations = listOf(Home, Workspace, History, Ops, Settings)
        private val allDestinations = topLevelDestinations + listOf(
            ProductLearning,
            ProductProfile,
            AnalysisResult,
            AnalysisReport,
            OpsDiagnostics,
            Chat,
        )

        fun fromRoute(route: String?): OpenClawDestination? =
            allDestinations.firstOrNull { it.route == route }
    }
}
