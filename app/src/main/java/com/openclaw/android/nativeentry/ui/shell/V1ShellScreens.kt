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
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun ProductLearningScreen(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    productName: String,
    productDescription: String,
    sourceNotes: String,
    onProductNameChange: (String) -> Unit,
    onProductDescriptionChange: (String) -> Unit,
    onSourceNotesChange: (String) -> Unit,
    onSubmitProductProfileClick: () -> Unit,
    onContinueClick: () -> Unit,
    onOpenOpsClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val canSubmit = productName.isNotBlank() &&
        productDescription.isNotBlank() &&
        backendState.productProfileCreate !is V1SectionState.Loading

    ScreenFrame(modifier = modifier) {
        Text(
            text = "产品学习",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "填写最小产品信息后创建 ProductProfile 草稿。当前只创建画像，不触发分析。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        ScreenSection(title = "创建产品画像草稿") {
            OutlinedTextField(
                value = productName,
                onValueChange = onProductNameChange,
                label = { Text(text = "产品名称") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = productDescription,
                onValueChange = onProductDescriptionChange,
                label = { Text(text = "一句话描述") },
                minLines = 2,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = sourceNotes,
                onValueChange = onSourceNotesChange,
                label = { Text(text = "补充材料（可选）") },
                minLines = 3,
                modifier = Modifier.fillMaxWidth(),
            )

            when (val createState = backendState.productProfileCreate) {
                V1SectionState.Idle -> {
                    Text(
                        text = "提交后会调用真实 POST /product-profiles，创建 draft 状态 ProductProfile。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在提交到真实后端。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "尚未创建 ProductProfile。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = createState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = createState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val profile = createState.value.productProfile
                    Text(text = "已创建：${profile.name}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${profile.status} · v${profile.version}", style = MaterialTheme.typography.bodyMedium)
                }
            }

            Button(
                onClick = onSubmitProductProfileClick,
                enabled = canSubmit,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = if (backendState.productProfileCreate is V1SectionState.Loading) {
                        "提交中"
                    } else {
                        "创建 ProductProfile 草稿"
                    },
                )
            }
        }

        ScreenSection(title = "占位调试参考") {
            DebugFallbackBanner()
            Text(text = "产品：${placeholderState.productProfile.name}", style = MaterialTheme.typography.bodyLarge)
            Text(text = "一句话描述：${placeholderState.productProfile.oneLineDescription}", style = MaterialTheme.typography.bodyMedium)
        }

        OutlinedButton(
            onClick = onContinueClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "查看最新产品画像")
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
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onContinueClick: () -> Unit,
    onRefreshClick: () -> Unit,
    onTriggerLeadAnalysisClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val canTriggerLeadAnalysis = backendState.productProfile is V1SectionState.Loaded &&
        backendState.analysisRun !is V1SectionState.Loading

    ScreenFrame(modifier = modifier) {
        Text(
            text = "产品画像",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "该页面读取真实 GET /product-profiles/{id}。当前仍不做编辑与提交。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val profileState = backendState.productProfile) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取最新 ProductProfile 详情。")

            V1SectionState.Empty -> StateNotice("真实后端当前没有可打开的 ProductProfile。")

            is V1SectionState.Failed -> FailureNotice(
                title = profileState.error.title,
                detail = profileState.error.detail,
            )

            is V1SectionState.Loaded -> {
                val profile = profileState.value
                ScreenSection(title = "概要") {
                    Text(text = "名称：${profile.name}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${profile.status} · v${profile.version}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "一句话描述：${profile.oneLineDescription}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "更新时间：${profile.updatedAt}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "客户与场景") {
                    Text(text = "目标客户：${profile.targetCustomers.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "目标行业：${profile.targetIndustries.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "典型场景：${profile.typicalUseCases.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "优势与限制") {
                    profile.coreAdvantages.ifEmpty { listOf("暂无") }.forEach { BulletText(text = it) }
                    Text(text = "交付模式：${profile.deliveryModel}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "仍需补充") {
                    profile.missingFields.ifEmpty { listOf("暂无") }.forEach { BulletText(text = it) }
                }
            }
        }

        if (backendState.isDebugFallbackEnabled) {
            PlaceholderProductProfileSection(placeholderState)
        }

        ScreenSection(title = "获客分析运行") {
            when (val runState = backendState.analysisRun) {
                V1SectionState.Idle -> {
                    Text(
                        text = "点击后会创建 lead_analysis AgentRun，并轮询运行状态。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在创建并轮询 lead_analysis。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "没有可用于分析的 ProductProfile。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = runState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = runState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val run = runState.value.agentRun
                    Text(text = "运行：${run.runType}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${run.status}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "Run ID：${run.id}", style = MaterialTheme.typography.bodyMedium)
                    run.errorMessage?.let {
                        Text(text = "错误：$it", style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }

            Button(
                onClick = onTriggerLeadAnalysisClick,
                enabled = canTriggerLeadAnalysis,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = if (backendState.analysisRun is V1SectionState.Loading) {
                        "运行中"
                    } else {
                        "生成获客分析"
                    },
                )
            }
        }

        OutlinedButton(
            onClick = onRefreshClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "刷新真实详情")
        }
        Button(
            onClick = onContinueClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "查看分析结果摘要")
        }
    }
}

@Composable
fun AnalysisResultScreen(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onTriggerReportGenerationClick: () -> Unit,
    onContinueClick: () -> Unit,
    onRefreshClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val canTriggerReportGeneration = (backendState.history as? V1SectionState.Loaded)
        ?.value
        ?.latestAnalysisResult != null &&
        backendState.reportRun !is V1SectionState.Loading

    ScreenFrame(modifier = modifier) {
        Text(
            text = "分析结果",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "该页面读取真实 GET /lead-analysis-results/{id}，展示完整获客分析详情。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val resultState = backendState.analysisResult) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取最新 LeadAnalysisResult 详情。")

            V1SectionState.Empty -> StateNotice("真实后端当前没有 LeadAnalysisResult。")

            is V1SectionState.Failed -> FailureNotice(
                title = resultState.error.title,
                detail = resultState.error.detail,
            )

            is V1SectionState.Loaded -> {
                val result = resultState.value
                ScreenSection(title = "结果概要") {
                    Text(text = result.title, style = MaterialTheme.typography.titleMedium)
                    Text(text = "状态：${result.status} · v${result.version}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "分析范围：${result.analysisScope}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "更新时间：${result.updatedAt}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "分析摘要") {
                    Text(text = result.summary, style = MaterialTheme.typography.bodyMedium)
                }

                if (result.priorityIndustries.isNotEmpty()) {
                    ScreenSection(title = "优先行业") {
                        result.priorityIndustries.forEach { BulletText(text = it) }
                    }
                }

                if (result.priorityCustomerTypes.isNotEmpty()) {
                    ScreenSection(title = "优先客户类型") {
                        result.priorityCustomerTypes.forEach { BulletText(text = it) }
                    }
                }

                if (result.scenarioOpportunities.isNotEmpty()) {
                    ScreenSection(title = "场景机会") {
                        result.scenarioOpportunities.forEach { BulletText(text = it) }
                    }
                }

                if (result.rankingExplanations.isNotEmpty()) {
                    ScreenSection(title = "排序说明") {
                        result.rankingExplanations.forEach { BulletText(text = it) }
                    }
                }

                if (result.recommendations.isNotEmpty()) {
                    ScreenSection(title = "建议") {
                        result.recommendations.forEach { BulletText(text = it) }
                    }
                }

                if (result.risks.isNotEmpty()) {
                    ScreenSection(title = "风险") {
                        result.risks.forEach { BulletText(text = it) }
                    }
                }

                if (result.limitations.isNotEmpty()) {
                    ScreenSection(title = "限制") {
                        result.limitations.forEach { BulletText(text = it) }
                    }
                }
            }
        }

        if (backendState.isDebugFallbackEnabled) {
            PlaceholderAnalysisResultSection(placeholderState)
        }

        OutlinedButton(
            onClick = onRefreshClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "刷新真实详情")
        }

        ScreenSection(title = "报告生成运行") {
            when (val runState = backendState.reportRun) {
                V1SectionState.Idle -> {
                    Text(
                        text = "点击后会创建 report_generation AgentRun，并轮询运行状态。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在创建并轮询 report_generation。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "没有可用于生成报告的 LeadAnalysisResult。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = runState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = runState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val run = runState.value.agentRun
                    Text(text = "运行：${run.runType}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${run.status}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "Run ID：${run.id}", style = MaterialTheme.typography.bodyMedium)
                    run.errorMessage?.let {
                        Text(text = "错误：$it", style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }

            Button(
                onClick = onTriggerReportGenerationClick,
                enabled = canTriggerReportGeneration,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = if (backendState.reportRun is V1SectionState.Loading) {
                        "运行中"
                    } else {
                        "生成分析报告"
                    },
                )
            }
        }

        Button(
            onClick = onContinueClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "查看分析报告")
        }
    }
}

@Composable
fun AnalysisReportScreen(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onRefreshClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    ScreenFrame(modifier = modifier) {
        Text(
            text = "分析报告",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "该页面读取真实 GET /reports/{id}，用于复看后端沉淀的 AnalysisReport。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val reportState = backendState.report) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取最新 AnalysisReport 详情。")

            V1SectionState.Empty -> StateNotice("真实后端当前没有可打开的 AnalysisReport。")

            is V1SectionState.Failed -> FailureNotice(
                title = reportState.error.title,
                detail = reportState.error.detail,
            )

            is V1SectionState.Loaded -> {
                val report = reportState.value
                ScreenSection(title = "报告摘要") {
                    Text(text = report.title, style = MaterialTheme.typography.titleMedium)
                    Text(text = "状态：${report.status} · v${report.version}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "更新时间：${report.updatedAt}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = report.summary, style = MaterialTheme.typography.bodyMedium)
                }

                report.sections.forEach { section ->
                    ScreenSection(title = section.title) {
                        Text(text = section.body, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }

        if (backendState.isDebugFallbackEnabled) {
            PlaceholderReportSection(placeholderState)
        }

        OutlinedButton(
            onClick = onRefreshClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "刷新真实报告")
        }
    }
}

@Composable
fun HistoryScreen(
    backendState: V1BackendUiState,
    placeholderState: V1ShellPlaceholderState,
    onOpenProductProfileClick: () -> Unit,
    onOpenAnalysisResultClick: () -> Unit,
    onOpenAnalysisReportClick: () -> Unit,
    onRefreshBackendClick: () -> Unit,
    onUseDebugFallbackClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    ScreenFrame(modifier = modifier) {
        Text(
            text = "历史与状态",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "这里读取真实 /history，承接轻量历史记录和当前 AgentRun 状态。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val historyState = backendState.history) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取真实后端 /history。")

            V1SectionState.Empty -> StateNotice("后端已连接，但当前历史为空。")

            is V1SectionState.Failed -> {
                FailureNotice(
                    title = historyState.error.title,
                    detail = historyState.error.detail,
                )
                OutlinedButton(
                    onClick = onUseDebugFallbackClick,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = "查看占位调试数据")
                }
            }

            is V1SectionState.Loaded -> {
                val history = historyState.value
                ScreenSection(title = "当前运行摘要") {
                    val run = history.currentRun
                    if (run == null) {
                        Text(text = "当前没有运行中的 AgentRun。", style = MaterialTheme.typography.bodyMedium)
                    } else {
                        Text(text = "运行：${run.runType}", style = MaterialTheme.typography.bodyLarge)
                        Text(text = "状态：${run.status}", style = MaterialTheme.typography.bodyMedium)
                        Text(text = "来源：${run.triggerSource}", style = MaterialTheme.typography.bodyMedium)
                        Text(text = "开始：${run.startedAt ?: "暂无"}", style = MaterialTheme.typography.bodyMedium)
                    }
                }

                ScreenSection(title = "最近对象入口") {
                    if (history.recentItems.isEmpty()) {
                        Text(text = "当前没有最近对象。", style = MaterialTheme.typography.bodyMedium)
                    }
                    history.recentItems.forEach { entry ->
                        HistoryEntryCard(
                            title = entry.title,
                            subtitle = "${entry.objectType} · ${entry.updatedAt}",
                            status = entry.status,
                            onOpenClick = when (entry.objectType) {
                                "product_profile" -> onOpenProductProfileClick
                                "lead_analysis_result" -> onOpenAnalysisResultClick
                                "analysis_report" -> onOpenAnalysisReportClick
                                else -> onRefreshBackendClick
                            },
                        )
                    }
                }
            }
        }

        if (backendState.isDebugFallbackEnabled) {
            PlaceholderHistorySection(
                placeholderState = placeholderState,
                onOpenProductProfileClick = onOpenProductProfileClick,
                onOpenAnalysisResultClick = onOpenAnalysisResultClick,
                onOpenAnalysisReportClick = onOpenAnalysisReportClick,
            )
        }

        OutlinedButton(
            onClick = onRefreshBackendClick,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "刷新真实后端")
        }
    }
}

@Composable
private fun PlaceholderProductProfileSection(placeholderState: V1ShellPlaceholderState) {
    val profile = placeholderState.productProfile
    ScreenSection(title = "占位/调试产品画像") {
        DebugFallbackBanner()
        Text(text = "名称：${profile.name}", style = MaterialTheme.typography.bodyLarge)
        Text(text = "状态：${profile.statusLabel}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "一句话描述：${profile.oneLineDescription}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "目标客户：${profile.targetCustomers}", style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun PlaceholderAnalysisResultSection(placeholderState: V1ShellPlaceholderState) {
    val result = placeholderState.analysisResult
    ScreenSection(title = "占位/调试分析结果") {
        DebugFallbackBanner()
        Text(text = "状态：${result.statusLabel}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "更新时间：${result.updatedAt}", style = MaterialTheme.typography.bodyMedium)
        result.priorityIndustries.forEach { BulletText(text = it) }
    }
}

@Composable
private fun PlaceholderReportSection(placeholderState: V1ShellPlaceholderState) {
    val report = placeholderState.report
    ScreenSection(title = "占位/调试分析报告") {
        DebugFallbackBanner()
        Text(text = report.title, style = MaterialTheme.typography.titleMedium)
        Text(text = "版本：${report.versionLabel}", style = MaterialTheme.typography.bodyMedium)
        Text(text = report.summary, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun PlaceholderHistorySection(
    placeholderState: V1ShellPlaceholderState,
    onOpenProductProfileClick: () -> Unit,
    onOpenAnalysisResultClick: () -> Unit,
    onOpenAnalysisReportClick: () -> Unit,
) {
    ScreenSection(title = "占位/调试最近对象") {
        DebugFallbackBanner()
        placeholderState.historyEntries.forEach { entry ->
            HistoryEntryCard(
                title = entry.title,
                subtitle = entry.subtitle,
                status = entry.statusLabel,
                onOpenClick = when (entry.type) {
                    PlaceholderHistoryEntryType.ProductProfile -> onOpenProductProfileClick
                    PlaceholderHistoryEntryType.AnalysisResult -> onOpenAnalysisResultClick
                    PlaceholderHistoryEntryType.AnalysisReport -> onOpenAnalysisReportClick
                },
            )
        }
    }
}

@Composable
private fun HistoryEntryCard(
    title: String,
    subtitle: String,
    status: String,
    onOpenClick: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(text = title, style = MaterialTheme.typography.titleMedium)
            Text(text = subtitle, style = MaterialTheme.typography.bodyMedium)
            Text(
                text = "状态：$status",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            OutlinedButton(
                onClick = onOpenClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "打开")
            }
        }
    }
}

@Composable
private fun StateNotice(message: String) {
    ScreenSection(title = "状态") {
        Text(text = message, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun FailureNotice(title: String, detail: String) {
    ScreenSection(title = "读取失败") {
        Text(text = title, style = MaterialTheme.typography.bodyLarge)
        Text(text = detail, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun DebugFallbackBanner() {
    Text(
        text = "当前内容为占位/调试数据，不是后端真实结果。",
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.error,
    )
}

@Composable
private fun BulletText(text: String) {
    Text(text = "• $text", style = MaterialTheme.typography.bodyMedium)
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

private fun List<String>.joinToDisplayText(): String =
    if (isEmpty()) "暂无" else joinToString("、")
