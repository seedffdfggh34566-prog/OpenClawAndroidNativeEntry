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
    val canOpenProductProfile = (backendState.history as? V1SectionState.Loaded)
        ?.value
        ?.latestProductProfile != null

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
                    Text(text = "正在同步当前销售分析进度。", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = backendState.backendBaseUrl,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Empty -> {
                    Text(text = "还没有销售分析记录。", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "从产品学习开始，先让系统理解你要卖的产品。",
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
                    val profile = history.value.latestProductProfile
                    val analysis = history.value.latestAnalysisResult
                    val report = history.value.latestReport

                    Text(
                        text = when {
                            currentRun != null -> "正在处理：${currentRun.runType.toFlowName()}"
                            report != null -> "销售分析报告已生成。"
                            analysis != null -> "获客分析结果已生成。"
                            profile?.status == "confirmed" -> "产品画像已确认。"
                            profile?.learningStage == "ready_for_confirmation" -> "产品画像已可确认。"
                            profile != null -> "产品画像还在补充中。"
                            else -> "还没有开始产品学习。"
                        },
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(
                        text = when {
                            currentRun != null -> "当前状态：${currentRun.status.toUserStatusLabel()}。完成后回到这里查看下一步。"
                            report != null -> "下一步：复看报告，或回到结果页继续对齐销售动作。"
                            analysis != null -> "下一步：查看分析结果，必要时生成可复看的报告。"
                            profile?.status == "confirmed" -> "下一步：生成获客分析，找出优先切入的客户方向。"
                            profile?.learningStage == "ready_for_confirmation" -> "下一步：确认产品画像，然后生成获客分析。"
                            profile != null -> "下一步：继续补充产品信息，让画像达到可确认状态。"
                            else -> "下一步：点击“开始分析”，创建第一版产品画像。"
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    if (profile != null) {
                        Text(text = "当前产品：${profile.name}", style = MaterialTheme.typography.bodyMedium)
                        Text(
                            text = "进度：${profile.status.toUserStatusLabel()} · ${profile.learningStage.toLearningStageLabel()} · v${profile.version}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
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
                enabled = canOpenProductProfile,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = if (canOpenProductProfile) "查看或确认产品画像" else "先开始产品学习")
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
                        text = "产品理解：${profile?.name ?: "暂无"}（${profile?.status?.toUserStatusLabel() ?: "未开始"}）",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        text = "获客分析：${analysis?.title ?: "暂无"}（${analysis?.status?.toUserStatusLabel() ?: "未生成"}）",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        text = "分析报告：${report?.title ?: "暂无"}（${report?.status?.toUserStatusLabel() ?: "未生成"}）",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

                V1SectionState.Empty -> {
                    Text(text = "暂无可复看的销售分析结果。", style = MaterialTheme.typography.bodyMedium)
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
                enabled = (backendState.history as? V1SectionState.Loaded)?.value?.latestAnalysisResult != null,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "查看获客分析结果")
            }
            OutlinedButton(
                onClick = onViewLatestReportClick,
                enabled = (backendState.history as? V1SectionState.Loaded)?.value?.latestReport != null,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "查看分析报告")
            }
        }
    }
}

private fun String.toFlowName(): String =
    when (this) {
        "product_learning" -> "产品学习"
        "lead_analysis" -> "获客分析"
        "report_generation" -> "分析报告生成"
        else -> this
    }

private fun String.toUserStatusLabel(): String =
    when (this) {
        "draft" -> "待确认"
        "confirmed" -> "已确认"
        "succeeded" -> "已完成"
        "failed" -> "失败"
        "running" -> "处理中"
        "pending" -> "等待中"
        "cancelled" -> "已取消"
        "published" -> "可复看"
        else -> this
    }

private fun String.toLearningStageLabel(): String =
    when (this) {
        "collecting" -> "继续补充"
        "ready_for_confirmation" -> "可确认"
        "confirmed" -> "已确认"
        else -> this
    }
