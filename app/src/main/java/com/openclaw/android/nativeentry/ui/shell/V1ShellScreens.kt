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
    supplementalNotes: String,
    onProductNameChange: (String) -> Unit,
    onProductDescriptionChange: (String) -> Unit,
    onSourceNotesChange: (String) -> Unit,
    onSupplementalNotesChange: (String) -> Unit,
    onSubmitProductProfileClick: () -> Unit,
    onSubmitProductProfileEnrichClick: () -> Unit,
    onContinueClick: () -> Unit,
    onOpenOpsClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val currentProfile = (backendState.productProfile as? V1SectionState.Loaded)?.value
    val canSubmitEnrich = currentProfile?.status == "draft" &&
        supplementalNotes.isNotBlank() &&
        backendState.productProfileEnrich !is V1SectionState.Loading &&
        backendState.productLearningRun !is V1SectionState.Loading
    val isReadyForConfirmation = currentProfile
        ?.let { it.status == "draft" && it.learningStage == "ready_for_confirmation" } == true
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
            text = "创建产品画像后，可继续补充一轮信息，让后端重新富化并收敛到确认状态。",
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
                        text = "提交后会生成第一版产品画像，并自动提炼客户、场景和优势。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在提交到真实后端。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "尚未创建产品画像。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = createState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = createState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val profile = createState.value.productProfile
                    Text(text = "已创建：${profile.name}", style = MaterialTheme.typography.bodyLarge)
                    Text(
                        text = "状态：${profile.status} · ${profile.learningStage} · v${profile.version}",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }

            when (val runState = backendState.productLearningRun) {
                V1SectionState.Idle -> Unit
                V1SectionState.Loading -> {
                    Text(
                        text = "正在富化产品画像，请稍候。",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

                V1SectionState.Empty -> {
                    Text(text = "当前没有 product_learning 运行。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = runState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = runState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val run = runState.value.agentRun
                    Text(text = "运行：${run.runType}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${run.status}", style = MaterialTheme.typography.bodyMedium)
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
                        "创建并学习产品"
                    },
                )
            }
        }

        ScreenSection(title = "当前理解") {
            when (val profileState = backendState.productProfile) {
                V1SectionState.Idle,
                V1SectionState.Loading -> StateNotice("正在读取最新 ProductProfile。")

                V1SectionState.Empty -> StateNotice("当前还没有可继续学习的 ProductProfile。")

                is V1SectionState.Failed -> FailureNotice(
                    title = profileState.error.title,
                    detail = profileState.error.detail,
                )

                is V1SectionState.Loaded -> {
                    val profile = profileState.value
                    Text(text = profile.name, style = MaterialTheme.typography.titleMedium)
                    Text(
                        text = "状态：${profile.status} · ${profile.learningStage} · v${profile.version}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(text = "目标客户：${profile.targetCustomers.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "目标行业：${profile.targetIndustries.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "典型场景：${profile.typicalUseCases.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "解决痛点：${profile.painPointsSolved.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "核心优势：${profile.coreAdvantages.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "限制条件：${profile.constraints.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                }
            }
        }

        ScreenSection(title = "仍需补充") {
            val missingFields = currentProfile?.missingFields.orEmpty()
            missingFields.ifEmpty { listOf("暂无") }.forEach { BulletText(text = it) }
            if (isReadyForConfirmation) {
                Text(
                    text = "当前画像已达到 ready_for_confirmation，可进入确认。",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }

        ScreenSection(title = "继续补充信息") {
            OutlinedTextField(
                value = supplementalNotes,
                onValueChange = onSupplementalNotesChange,
                label = { Text(text = "补充材料") },
                minLines = 3,
                modifier = Modifier.fillMaxWidth(),
            )

            when (val enrichState = backendState.productProfileEnrich) {
                V1SectionState.Idle -> {
                    Text(
                        text = "提交后会基于补充材料重新学习，并刷新当前产品画像。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在提交补充信息。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "当前没有可补充的 ProductProfile。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> FailureNotice(
                    title = enrichState.error.title,
                    detail = enrichState.error.detail,
                )

                is V1SectionState.Loaded -> {
                    val run = enrichState.value.agentRun
                    Text(text = "已创建补充运行：${run.id}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${run.status}", style = MaterialTheme.typography.bodyMedium)
                }
            }

            Button(
                onClick = onSubmitProductProfileEnrichClick,
                enabled = canSubmitEnrich,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = if (backendState.productProfileEnrich is V1SectionState.Loading) {
                        "补充中"
                    } else {
                        "提交补充并重新学习"
                    },
                )
            }
        }

        if (backendState.isDebugFallbackEnabled) {
            ScreenSection(title = "占位调试参考") {
                DebugFallbackBanner()
                Text(text = "产品：${placeholderState.productProfile.name}", style = MaterialTheme.typography.bodyLarge)
                Text(text = "一句话描述：${placeholderState.productProfile.oneLineDescription}", style = MaterialTheme.typography.bodyMedium)
            }
        }

        Button(
            onClick = onContinueClick,
            enabled = currentProfile != null,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isReadyForConfirmation) "查看并确认产品画像" else "查看最新产品画像")
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
    onConfirmProductProfileClick: () -> Unit,
    onTriggerLeadAnalysisClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val profileIsConfirmed = (backendState.productProfile as? V1SectionState.Loaded)
        ?.value
        ?.status == "confirmed"

    val canTriggerLeadAnalysis = profileIsConfirmed &&
        backendState.analysisRun !is V1SectionState.Loading

    val canConfirm = (backendState.productProfile as? V1SectionState.Loaded)
        ?.value
        ?.let { profile ->
            profile.status == "draft" &&
                profile.learningStage == "ready_for_confirmation" &&
                backendState.productProfileConfirm !is V1SectionState.Loading
        } == true

    ScreenFrame(modifier = modifier) {
        Text(
            text = "产品画像",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "先确认系统对产品、客户和切入场景的理解，再进入获客分析。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val profileState = backendState.productProfile) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取最新产品画像。")

            V1SectionState.Empty -> StateNotice("当前还没有可确认的产品画像。")

            is V1SectionState.Failed -> FailureNotice(
                title = profileState.error.title,
                detail = profileState.error.detail,
            )

            is V1SectionState.Loaded -> {
                val profile = profileState.value
                ScreenSection(title = "我们理解你的产品") {
                    Text(text = profile.name, style = MaterialTheme.typography.titleMedium)
                    Text(text = profile.oneLineDescription, style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "当前进度：${profile.status.toUserStatusLabel()} · ${profile.learningStage.toLearningStageLabel()} · v${profile.version}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(text = "更新时间：${profile.updatedAt}", style = MaterialTheme.typography.bodySmall)
                }

                ScreenSection(title = "适合卖给谁") {
                    Text(text = "客户类型：${profile.targetCustomers.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "目标行业：${profile.targetIndustries.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "主要痛点：${profile.painPointsSolved.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "优先场景") {
                    Text(text = "典型场景：${profile.typicalUseCases.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "交付模式：${profile.deliveryModel}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "核心优势与限制") {
                    profile.coreAdvantages.ifEmpty { listOf("暂无") }.forEach { BulletText(text = it) }
                    Text(text = "限制条件：${profile.constraints.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
                }

                ScreenSection(title = "仍需补充") {
                    profile.missingFields.ifEmpty { listOf("暂无") }.forEach { BulletText(text = it) }
                }
            }
        }

        if (backendState.isDebugFallbackEnabled) {
            PlaceholderProductProfileSection(placeholderState)
        }

        ScreenSection(title = "产品画像确认") {
            when (val confirmState = backendState.productProfileConfirm) {
                V1SectionState.Idle -> {
                    val profile = (backendState.productProfile as? V1SectionState.Loaded)?.value
                    Text(
                        text = if (profileIsConfirmed) {
                            "当前产品画像已确认，可以进入获客分析。"
                        } else if (profile?.learningStage == "ready_for_confirmation") {
                            "当前画像已达到可确认状态。确认后即可生成获客分析。"
                        } else {
                            "当前仍需补齐关键信息，先回到产品学习页继续补充。"
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在提交确认请求。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "没有可确认的产品画像。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = confirmState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = confirmState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val profile = confirmState.value.productProfile
                    Text(text = "确认成功：${profile.name}", style = MaterialTheme.typography.bodyLarge)
                    Text(
                        text = "新状态：${profile.status} · ${profile.learningStage} · v${profile.version}",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }

            Button(
                onClick = onConfirmProductProfileClick,
                enabled = canConfirm,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = when {
                        backendState.productProfileConfirm is V1SectionState.Loading -> "确认中"
                        profileIsConfirmed -> "已确认"
                        else -> "确认产品画像"
                    },
                )
            }
        }

        ScreenSection(title = "获客分析运行") {
            when (val runState = backendState.analysisRun) {
                V1SectionState.Idle -> {
                    Text(
                        text = if (profileIsConfirmed) {
                            "点击后会基于已确认的产品画像生成获客分析。"
                        } else {
                            "请先确认产品画像，再触发获客分析。"
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在生成获客分析。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "没有可用于分析的已确认产品画像。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = runState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = runState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val run = runState.value.agentRun
                    Text(text = "获客分析已提交。", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${run.status.toUserStatusLabel()}", style = MaterialTheme.typography.bodyMedium)
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
            text = "这里汇总优先行业、客户类型、切入场景和下一步销售动作。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val resultState = backendState.analysisResult) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取最新获客分析结果。")

            V1SectionState.Empty -> StateNotice("当前还没有获客分析结果。")

            is V1SectionState.Failed -> FailureNotice(
                title = resultState.error.title,
                detail = resultState.error.detail,
            )

            is V1SectionState.Loaded -> {
                val result = resultState.value
                ScreenSection(title = "优先尝试方向") {
                    Text(text = result.title, style = MaterialTheme.typography.titleMedium)
                    Text(text = result.summary, style = MaterialTheme.typography.bodyMedium)
                    result.priorityIndustries.firstOrNull()?.let {
                        Text(text = "优先行业：$it", style = MaterialTheme.typography.bodyMedium)
                    }
                    result.priorityCustomerTypes.firstOrNull()?.let {
                        Text(text = "优先客户：$it", style = MaterialTheme.typography.bodyMedium)
                    }
                    result.scenarioOpportunities.firstOrNull()?.let {
                        Text(text = "优先场景：$it", style = MaterialTheme.typography.bodyMedium)
                    }
                    Text(
                        text = "状态：${result.status.toUserStatusLabel()} · v${result.version} · ${result.updatedAt}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                ScreenSection(title = "分析范围") {
                    Text(text = result.analysisScope, style = MaterialTheme.typography.bodyMedium)
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
                    ScreenSection(title = "判断依据") {
                        result.rankingExplanations.forEach { BulletText(text = it) }
                    }
                }

                if (result.recommendations.isNotEmpty()) {
                    ScreenSection(title = "下一步建议") {
                        result.recommendations.forEach { BulletText(text = it) }
                    }
                }

                if (result.risks.isNotEmpty() || result.limitations.isNotEmpty()) {
                    ScreenSection(title = "风险和限制") {
                        result.risks.forEach { BulletText(text = it) }
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
                        text = "生成报告后，可以把当前分析作为一份稳定材料复看。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                V1SectionState.Loading -> {
                    Text(text = "正在生成分析报告。", style = MaterialTheme.typography.bodyMedium)
                }

                V1SectionState.Empty -> {
                    Text(text = "没有可用于生成报告的获客分析结果。", style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Failed -> {
                    Text(text = runState.error.title, style = MaterialTheme.typography.bodyLarge)
                    Text(text = runState.error.detail, style = MaterialTheme.typography.bodyMedium)
                }

                is V1SectionState.Loaded -> {
                    val run = runState.value.agentRun
                    Text(text = "报告生成已提交。", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${run.status.toUserStatusLabel()}", style = MaterialTheme.typography.bodyMedium)
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
                        "生成可复看的分析报告"
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
            text = "这是一份可复看的销售分析交付物，用于对齐目标客户、切入场景和下一步行动。",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (val reportState = backendState.report) {
            V1SectionState.Idle,
            V1SectionState.Loading -> StateNotice("正在读取最新分析报告。")

            V1SectionState.Empty -> StateNotice("当前还没有可复看的分析报告。")

            is V1SectionState.Failed -> FailureNotice(
                title = reportState.error.title,
                detail = reportState.error.detail,
            )

            is V1SectionState.Loaded -> {
                val report = reportState.value
                ScreenSection(title = "执行摘要") {
                    Text(text = report.title, style = MaterialTheme.typography.titleMedium)
                    Text(text = report.summary, style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "状态：${report.status.toUserStatusLabel()} · v${report.version} · ${report.updatedAt}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                val recommendationSections = report.sections.filter { section ->
                    section.title.contains("建议") || section.title.contains("行动")
                }
                if (recommendationSections.isNotEmpty()) {
                    ScreenSection(title = "重点建议") {
                        recommendationSections.forEach { section ->
                            Text(text = section.body, style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }

                report.sections.filterNot { section -> section in recommendationSections }.forEach { section ->
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
