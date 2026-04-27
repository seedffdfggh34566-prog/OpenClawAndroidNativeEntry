package com.openclaw.android.nativeentry.ui.workspace

import androidx.compose.foundation.layout.Arrangement
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
import com.openclaw.android.nativeentry.data.backend.SalesWorkspacePatchDraftApplyResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspacePatchDraftPreviewDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceReadOnlySnapshot
import com.openclaw.android.nativeentry.ui.shell.V1SectionState

@Composable
fun SalesWorkspaceScreen(
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    patchDraftPreviewState: V1SectionState<SalesWorkspacePatchDraftPreviewDto>,
    patchDraftApplyState: V1SectionState<SalesWorkspacePatchDraftApplyResponseDto>,
    onRefreshClick: () -> Unit,
    onPreviewClick: () -> Unit,
    onApplyClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(PaddingValues(horizontal = 20.dp, vertical = 24.dp)),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(
            modifier = Modifier.widthIn(max = 720.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text(
                text = "Sales Workspace",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = "查看当前 workspace，并通过显式审阅 gate 应用 Runtime PatchDraft。",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            when (workspaceState) {
                V1SectionState.Idle -> WorkspaceNotice("尚未读取 workspace。")
                V1SectionState.Loading -> WorkspaceNotice("正在读取 Sales Workspace。")
                V1SectionState.Empty -> WorkspaceNotice("当前没有可展示的 workspace。")
                is V1SectionState.Failed -> WorkspaceCard(title = workspaceState.error.title) {
                    Text(text = workspaceState.error.detail, style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "请确认后端已启动、已运行 seed 脚本，并已执行 adb reverse tcp:8013 tcp:8013。",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                is V1SectionState.Loaded -> {
                    WorkspaceContent(workspaceState.value)
                    PatchDraftReviewGate(
                        workspaceVersion = workspaceState.value.workspace.workspaceVersion,
                        previewState = patchDraftPreviewState,
                        applyState = patchDraftApplyState,
                        onPreviewClick = onPreviewClick,
                        onApplyClick = onApplyClick,
                    )
                }
            }

            Button(
                onClick = onRefreshClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "刷新工作区")
            }
        }
    }
}

@Composable
private fun PatchDraftReviewGate(
    workspaceVersion: Int,
    previewState: V1SectionState<SalesWorkspacePatchDraftPreviewDto>,
    applyState: V1SectionState<SalesWorkspacePatchDraftApplyResponseDto>,
    onPreviewClick: () -> Unit,
    onApplyClick: () -> Unit,
) {
    val preview = (previewState as? V1SectionState.Loaded<SalesWorkspacePatchDraftPreviewDto>)?.value
    val previewIsCurrent = preview?.patchDraft?.baseWorkspaceVersion == workspaceVersion
    val isPreviewLoading = previewState is V1SectionState.Loading
    val isApplyLoading = applyState is V1SectionState.Loading

    WorkspaceCard(title = "PatchDraft Review Gate") {
        Text(
            text = "Android 只负责请求预览和提交已审阅 draft；正式写入由 Sales Workspace Kernel 校验。",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(text = "当前 workspace version：$workspaceVersion", style = MaterialTheme.typography.bodyMedium)

        Button(
            onClick = onPreviewClick,
            enabled = !isPreviewLoading && !isApplyLoading,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isPreviewLoading) "正在生成预览" else "生成 PatchDraft 预览")
        }

        when (previewState) {
            V1SectionState.Idle -> Text(
                text = "尚未生成 PatchDraft 预览。",
                style = MaterialTheme.typography.bodyMedium,
            )

            V1SectionState.Loading -> Text(
                text = "Runtime prototype 正在生成 deterministic draft。",
                style = MaterialTheme.typography.bodyMedium,
            )

            V1SectionState.Empty -> Text(text = "暂无 PatchDraft 预览。", style = MaterialTheme.typography.bodyMedium)
            is V1SectionState.Failed -> {
                Text(text = previewState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = previewState.error.detail, style = MaterialTheme.typography.bodyMedium)
            }

            is V1SectionState.Loaded -> PatchDraftPreviewDetails(previewState.value, previewIsCurrent)
        }

        OutlinedButton(
            onClick = onApplyClick,
            enabled = preview != null && previewIsCurrent && !isPreviewLoading && !isApplyLoading,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isApplyLoading) "正在应用已审阅 Draft" else "应用已审阅 Draft")
        }

        if (preview != null && !previewIsCurrent) {
            Text(
                text = "预览基于 version ${preview.patchDraft.baseWorkspaceVersion}，当前 workspace 已是 version $workspaceVersion。请刷新后重新生成预览。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error,
            )
        }

        when (applyState) {
            V1SectionState.Idle,
            V1SectionState.Empty -> Unit

            V1SectionState.Loading -> Text(
                text = "正在通过 backend review gate 应用 draft。",
                style = MaterialTheme.typography.bodyMedium,
            )

            is V1SectionState.Failed -> {
                Text(text = applyState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = applyState.error.detail, style = MaterialTheme.typography.bodyMedium)
            }

            is V1SectionState.Loaded -> PatchDraftApplyDetails(applyState.value)
        }
    }
}

@Composable
private fun PatchDraftPreviewDetails(
    preview: SalesWorkspacePatchDraftPreviewDto,
    previewIsCurrent: Boolean,
) {
    val topCandidate = preview.previewTopCandidate
    Text(text = "Draft：${preview.patchDraft.id}", style = MaterialTheme.typography.bodyMedium)
    Text(text = "Patch：${preview.patch.id}", style = MaterialTheme.typography.bodyMedium)
    Text(
        text = "Preview version：${preview.previewWorkspaceVersion}；would_mutate=${preview.wouldMutate}",
        style = MaterialTheme.typography.bodyMedium,
    )
    Text(text = "Operations：${preview.patchDraft.operationCount}", style = MaterialTheme.typography.bodyMedium)
    Text(
        text = if (previewIsCurrent) {
            "预览仍匹配当前 workspace version。"
        } else {
            "预览已过期，不能应用。"
        },
        style = MaterialTheme.typography.bodySmall,
        color = if (previewIsCurrent) {
            MaterialTheme.colorScheme.onSurfaceVariant
        } else {
            MaterialTheme.colorScheme.error
        },
    )
    if (topCandidate == null) {
        Text(text = "预览排序暂无 top candidate。", style = MaterialTheme.typography.bodyMedium)
    } else {
        Text(
            text = "预览第一：#${topCandidate.rank} ${topCandidate.candidateName} · ${topCandidate.score}",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
        )
        Text(text = topCandidate.reason, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun PatchDraftApplyDetails(response: SalesWorkspacePatchDraftApplyResponseDto) {
    val topCandidate = response.topCandidate
    Text(
        text = "已应用 ${response.patch.id}，workspace version ${response.workspace.workspaceVersion}。",
        style = MaterialTheme.typography.bodyMedium,
    )
    if (topCandidate != null) {
        Text(
            text = "当前第一：#${topCandidate.rank} ${topCandidate.candidateName} · ${topCandidate.score}",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
private fun WorkspaceContent(snapshot: SalesWorkspaceReadOnlySnapshot) {
    val workspace = snapshot.workspace
    val product = workspace.currentProductProfile
    val direction = workspace.currentLeadDirection

    WorkspaceCard(title = workspace.name) {
        Text(text = "Workspace ID：${workspace.id}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "Version：${workspace.workspaceVersion}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "Goal：${workspace.goal.ifBlank { "-" }}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "Status：${workspace.status}", style = MaterialTheme.typography.bodyMedium)
    }

    WorkspaceCard(title = "当前产品理解") {
        if (product == null) {
            Text(text = "暂无当前产品画像。", style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = product.productName, style = MaterialTheme.typography.titleMedium)
            Text(text = product.oneLiner, style = MaterialTheme.typography.bodyMedium)
            Text(text = "目标客户：${product.targetCustomers.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "痛点：${product.painPoints.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "价值：${product.valueProps.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
        }
    }

    WorkspaceCard(title = "当前获客方向") {
        if (direction == null) {
            Text(text = "暂无当前获客方向。", style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = "行业：${direction.priorityIndustries.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "客户类型：${direction.targetCustomerTypes.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "地区：${direction.regions.joinToDisplayText()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "原因：${direction.changeReason.ifBlank { "-" }}", style = MaterialTheme.typography.bodyMedium)
        }
    }

    WorkspaceCard(title = "候选排序") {
        val rankingBoard = snapshot.rankingBoard ?: workspace.rankingBoard
        val items = rankingBoard?.rankedItems.orEmpty()
        if (items.isEmpty()) {
            Text(text = "当前没有候选排序。", style = MaterialTheme.typography.bodyMedium)
        } else {
            items.take(5).forEach { item ->
                Text(
                    text = "#${item.rank} ${item.candidateName} · ${item.score} · ${item.status}",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(text = item.reason, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }

    WorkspaceCard(title = "Ranking Delta") {
        val deltas = snapshot.rankingBoard?.deltas.orEmpty()
        if (deltas.isEmpty()) {
            Text(text = "暂无 ranking delta。", style = MaterialTheme.typography.bodyMedium)
        } else {
            deltas.take(4).forEach { delta ->
                Text(
                    text = "${delta.candidateId}: ${delta.previousRank ?: "-"} -> ${delta.newRank}, ${delta.previousScore} -> ${delta.newScore}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(text = delta.reason, style = MaterialTheme.typography.bodySmall)
            }
        }
    }

    WorkspaceCard(title = "ContextPack") {
        val contextPack = snapshot.contextPack
        if (contextPack == null) {
            Text(text = "暂无 ContextPack。", style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = contextPack.id, style = MaterialTheme.typography.titleSmall)
            Text(text = "Top candidates:", style = MaterialTheme.typography.bodyMedium)
            contextPack.topCandidates.take(5).forEach { candidate ->
                Text(
                    text = "#${candidate.rank} ${candidate.name} · ${candidate.score}",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Text(
                text = contextPack.kernelBoundary,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }

    WorkspaceCard(title = "Markdown Projection") {
        val files = snapshot.projection?.files.orEmpty().keys.sorted()
        if (files.isEmpty()) {
            Text(text = "暂无 projection 文件。", style = MaterialTheme.typography.bodyMedium)
        } else {
            files.forEach { file ->
                Text(text = file, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}

@Composable
private fun WorkspaceNotice(message: String) {
    WorkspaceCard(title = "状态") {
        Text(text = message, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun WorkspaceCard(
    title: String,
    content: @Composable () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )
            content()
        }
    }
}

private fun List<String>.joinToDisplayText(): String =
    if (isEmpty()) "-" else joinToString("、")
