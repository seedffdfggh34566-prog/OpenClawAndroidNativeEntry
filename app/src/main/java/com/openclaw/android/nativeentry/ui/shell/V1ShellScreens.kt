package com.openclaw.android.nativeentry.ui.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
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

@Composable
fun ProductLearningScreen(
    placeholderState: V1ShellPlaceholderState,
    onContinueClick: () -> Unit,
    onOpenOpsClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    ScreenFrame(modifier = modifier) {
        Text(
            text = "产品学习",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "这是 V1 的产品学习占位页，用于承接后续正式对话和信息收集流程。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        ScreenSection(title = "当前收集进度") {
            Text(text = "当前阶段：${placeholderState.runStatus.stageTitle}", style = MaterialTheme.typography.bodyLarge)
            Text(text = "状态：${placeholderState.runStatus.statusLabel}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "最近更新时间：${placeholderState.runStatus.updatedAt}", style = MaterialTheme.typography.bodyMedium)
            Text(text = placeholderState.runStatus.summary, style = MaterialTheme.typography.bodyMedium)
        }

        ScreenSection(title = "已提炼的关键信息") {
            Text(text = "产品：${placeholderState.productProfile.name}", style = MaterialTheme.typography.bodyLarge)
            Text(text = "一句话描述：${placeholderState.productProfile.oneLineDescription}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "目标客户：${placeholderState.productProfile.targetCustomers}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "典型场景：${placeholderState.productProfile.typicalUseCases}", style = MaterialTheme.typography.bodyMedium)
        }

        ScreenSection(title = "待补充信息") {
            placeholderState.productProfile.missingInfo.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        Button(
            onClick = onContinueClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "进入产品画像确认")
        }

        OutlinedButton(
            onClick = onOpenOpsClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "查看运维入口")
        }
    }
}

@Composable
fun ProductProfileScreen(
    placeholderState: V1ShellPlaceholderState,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val profile = placeholderState.productProfile
    ScreenFrame(modifier = modifier) {
        Text(
            text = "产品画像",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "该页面承接 ProductProfile 的 draft / confirmed 形态展示。当前为占位壳层，不做真实编辑与提交。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        ScreenSection(title = "概要") {
            Text(text = "名称：${profile.name}", style = MaterialTheme.typography.bodyLarge)
            Text(text = "状态：${profile.statusLabel}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "一句话描述：${profile.oneLineDescription}", style = MaterialTheme.typography.bodyMedium)
        }

        ScreenSection(title = "客户与场景") {
            Text(text = "目标客户：${profile.targetCustomers}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "典型场景：${profile.typicalUseCases}", style = MaterialTheme.typography.bodyMedium)
        }

        ScreenSection(title = "当前已知优势") {
            profile.coreAdvantages.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        ScreenSection(title = "仍需补充") {
            profile.missingInfo.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        Button(
            onClick = onContinueClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "查看分析结果占位页")
        }
    }
}

@Composable
fun AnalysisResultScreen(
    placeholderState: V1ShellPlaceholderState,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val result = placeholderState.analysisResult
    ScreenFrame(modifier = modifier) {
        Text(
            text = "分析结果",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "该页面用于承接 LeadAnalysisResult 的正式展示骨架，当前内容为占位数据。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        ScreenSection(title = "结果摘要") {
            Text(text = "状态：${result.statusLabel}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "更新时间：${result.updatedAt}", style = MaterialTheme.typography.bodyMedium)
        }

        ScreenSection(title = "优先行业") {
            result.priorityIndustries.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        ScreenSection(title = "优先客户类型") {
            result.priorityCustomerTypes.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        ScreenSection(title = "推荐理由") {
            result.recommendationReasons.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        ScreenSection(title = "风险与限制") {
            result.risks.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }

        Button(
            onClick = onContinueClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "查看分析报告占位页")
        }
    }
}

@Composable
fun AnalysisReportScreen(
    placeholderState: V1ShellPlaceholderState,
    modifier: Modifier = Modifier,
) {
    val report = placeholderState.report
    ScreenFrame(modifier = modifier) {
        Text(
            text = "分析报告",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "该页面承接 AnalysisReport 的正式输出骨架，当前用于演示结构化内容如何在 Android 控制入口中复看。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        ScreenSection(title = "报告摘要") {
            Text(text = report.title, style = MaterialTheme.typography.titleMedium)
            Text(text = "版本：${report.versionLabel}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "更新时间：${report.updatedAt}", style = MaterialTheme.typography.bodyMedium)
            Text(text = report.summary, style = MaterialTheme.typography.bodyMedium)
        }

        report.sections.forEach { section ->
            ScreenSection(title = section.title) {
                Text(text = section.body, style = MaterialTheme.typography.bodyMedium)
            }
        }

        ScreenSection(title = "下一步建议") {
            report.nextSteps.forEach { item ->
                Text(text = "• $item", style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}

@Composable
fun HistoryScreen(
    placeholderState: V1ShellPlaceholderState,
    onOpenProductProfileClick: () -> Unit,
    onOpenAnalysisResultClick: () -> Unit,
    onOpenAnalysisReportClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    ScreenFrame(modifier = modifier) {
        Text(
            text = "历史与状态",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "这里用于承接轻量历史记录和当前 AgentRun 状态，不做完整工作台。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        ScreenSection(title = "当前运行摘要") {
            Text(text = "阶段：${placeholderState.runStatus.stageTitle}", style = MaterialTheme.typography.bodyLarge)
            Text(text = "状态：${placeholderState.runStatus.statusLabel}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "最近更新时间：${placeholderState.runStatus.updatedAt}", style = MaterialTheme.typography.bodyMedium)
            Text(text = placeholderState.runStatus.summary, style = MaterialTheme.typography.bodyMedium)
        }

        ScreenSection(title = "最近对象入口") {
            placeholderState.historyEntries.forEach { entry ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(text = entry.title, style = MaterialTheme.typography.titleMedium)
                        Text(text = entry.subtitle, style = MaterialTheme.typography.bodyMedium)
                        Text(
                            text = "状态：${entry.statusLabel}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        OutlinedButton(
                            onClick = when (entry.type) {
                                PlaceholderHistoryEntryType.ProductProfile -> onOpenProductProfileClick
                                PlaceholderHistoryEntryType.AnalysisResult -> onOpenAnalysisResultClick
                                PlaceholderHistoryEntryType.AnalysisReport -> onOpenAnalysisReportClick
                            },
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text(text = "打开")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ScreenFrame(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
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
            content = content,
        )
    }
}

@Composable
private fun ScreenSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            content = {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                content()
            },
        )
    }
}
