package com.openclaw.android.nativeentry.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.openclaw.android.nativeentry.ui.shell.V1BackendUiState
import com.openclaw.android.nativeentry.ui.shell.V1SectionState
import com.openclaw.android.nativeentry.ui.shell.V1ShellPlaceholderState

@Composable
fun HomeScreen(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onStartAnalysisClick: () -> Unit,
    onContinueFlowClick: () -> Unit,
    onViewHistoryClick: () -> Unit,
    onViewLatestAnalysisClick: () -> Unit,
    onViewLatestReportClick: () -> Unit,
    onViewOpsClick: () -> Unit,
    onRefreshBackendClick: () -> Unit,
    onUseDebugFallbackClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.TopCenter,
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 760.dp)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(PaddingValues(horizontal = 24.dp, vertical = 28.dp)),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "AI 销售助手 V1",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "通过产品学习、获客分析和结构化报告，帮助你用更短时间明确下一步销售方向。",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            Button(
                onClick = onStartAnalysisClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "开始分析")
            }

            CurrentWorkCard(
                backendState = backendState,
                placeholderState = placeholderState,
                onContinueFlowClick = onContinueFlowClick,
                onRefreshBackendClick = onRefreshBackendClick,
                onUseDebugFallbackClick = onUseDebugFallbackClick,
            )

            RecentResultsCard(
                backendState = backendState,
                placeholderState = placeholderState,
                onViewLatestAnalysisClick = onViewLatestAnalysisClick,
                onViewLatestReportClick = onViewLatestReportClick,
            )

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "辅助入口",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    OutlinedButton(
                        onClick = onViewHistoryClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "查看历史与状态")
                    }
                    OutlinedButton(
                        onClick = onViewOpsClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "进入运维与诊断")
                    }
                }
            }
        }
    }
}

@Composable
private fun CurrentWorkCard(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onContinueFlowClick: () -> Unit,
    onRefreshBackendClick: () -> Unit,
    onUseDebugFallbackClick: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "当前工作摘要",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )

            when (val history = backendState.history) {
                V1SectionState.Idle,
                V1SectionState.Loading -> {
                    Text(text = "正在读取真实后端 /history。", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = backendState.backendBaseUrl,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Empty -> {
                    Text(text = "后端已连接，但当前没有 ProductProfile、AnalysisResult 或 Report。", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "这是空库状态，不再展示样例数据冒充真实结果。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                is V1SectionState.Failed -> {
                    Text(text = history.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = history.error.detail, style = MaterialTheme.typography.bodyMedium)
                    OutlinedButton(
                        onClick = onUseDebugFallbackClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "查看占位调试数据")
                    }
                }

                is V1SectionState.Loaded -> {
                    val currentRun = history.value.currentRun
                    if (currentRun != null) {
                        Text(text = "当前运行：${currentRun.runType}", style = MaterialTheme.typography.bodyLarge)
                        Text(text = "状态：${currentRun.status}", style = MaterialTheme.typography.bodyMedium)
                        Text(text = "来源：${currentRun.triggerSource}", style = MaterialTheme.typography.bodyMedium)
                    } else {
                        Text(text = "当前没有运行中的 AgentRun。", style = MaterialTheme.typography.bodyMedium)
                    }

                    val profile = history.value.latestProductProfile
                    if (profile != null) {
                        Text(text = "最新产品画像：${profile.name}", style = MaterialTheme.typography.bodyMedium)
                        Text(text = "状态：${profile.status} · v${profile.version}", style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }

            if (backendState.isDebugFallbackEnabled) {
                Text(
                    text = "当前显示占位/调试数据，不是后端真实结果。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
                Text(text = "阶段：${placeholderState.runStatus.stageTitle}", style = MaterialTheme.typography.bodyMedium)
                Text(text = placeholderState.runStatus.summary, style = MaterialTheme.typography.bodyMedium)
            }

            OutlinedButton(
                onClick = onRefreshBackendClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "刷新真实后端")
            }
            OutlinedButton(
                onClick = onContinueFlowClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "继续当前流程")
            }
        }
    }
}

@Composable
private fun RecentResultsCard(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onViewLatestAnalysisClick: () -> Unit,
    onViewLatestReportClick: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "最近结果入口",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )

            when (val history = backendState.history) {
                is V1SectionState.Loaded -> {
                    val profile = history.value.latestProductProfile
                    val analysis = history.value.latestAnalysisResult
                    val report = history.value.latestReport
                    Text(
                        text = "ProductProfile：${profile?.name ?: "暂无"} (${profile?.status ?: "none"})",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        text = "LeadAnalysisResult：${analysis?.title ?: "暂无"} (${analysis?.status ?: "none"})",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        text = "AnalysisReport：${report?.title ?: "暂无"} (${report?.status ?: "none"})",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

                V1SectionState.Empty -> {
                    Text(text = "真实后端当前没有最近对象。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = "真实后端读取失败，未展示样例结果。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Idle,
                V1SectionState.Loading -> {
                    Text(text = "正在读取最近对象。", style = MaterialTheme.typography.bodyMedium)
                }
            }

            if (backendState.isDebugFallbackEnabled) {
                Text(
                    text = "占位/调试 ProductProfile：${placeholderState.productProfile.name}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }

            OutlinedButton(
                onClick = onViewLatestAnalysisClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "查看最新分析结果")
            }
            OutlinedButton(
                onClick = onViewLatestReportClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "查看最新分析报告")
            }
        }
    }
}
