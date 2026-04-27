package com.openclaw.android.nativeentry.ui.workspace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
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
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceChatTurnResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewApplyResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceReadOnlySnapshot
import com.openclaw.android.nativeentry.ui.shell.V1SectionState

@Composable
fun SalesWorkspaceScreen(
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    draftReviewState: V1SectionState<SalesWorkspaceDraftReviewDto>,
    patchDraftApplyState: V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>,
    chatFirstTurnState: V1SectionState<SalesWorkspaceChatTurnResponseDto>,
    chatInput: String,
    chatMessageType: String,
    onRefreshClick: () -> Unit,
    onCreateDraftReviewClick: () -> Unit,
    onChatInputChange: (String) -> Unit,
    onChatMessageTypeChange: (String) -> Unit,
    onSubmitChatTurnClick: () -> Unit,
    onAcceptDraftReviewClick: () -> Unit,
    onRejectDraftReviewClick: () -> Unit,
    onApplyDraftReviewClick: () -> Unit,
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
                    ChatFirstWorkspaceTurn(
                        workspaceVersion = workspaceState.value.workspace.workspaceVersion,
                        chatInput = chatInput,
                        chatMessageType = chatMessageType,
                        chatFirstTurnState = chatFirstTurnState,
                        onChatInputChange = onChatInputChange,
                        onChatMessageTypeChange = onChatMessageTypeChange,
                        onSubmitChatTurnClick = onSubmitChatTurnClick,
                    )
                    PatchDraftReviewGate(
                        workspaceVersion = workspaceState.value.workspace.workspaceVersion,
                        draftReviewState = draftReviewState,
                        applyState = patchDraftApplyState,
                        onCreateDraftReviewClick = onCreateDraftReviewClick,
                        onAcceptDraftReviewClick = onAcceptDraftReviewClick,
                        onRejectDraftReviewClick = onRejectDraftReviewClick,
                        onApplyDraftReviewClick = onApplyDraftReviewClick,
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
private fun ChatFirstWorkspaceTurn(
    workspaceVersion: Int,
    chatInput: String,
    chatMessageType: String,
    chatFirstTurnState: V1SectionState<SalesWorkspaceChatTurnResponseDto>,
    onChatInputChange: (String) -> Unit,
    onChatMessageTypeChange: (String) -> Unit,
    onSubmitChatTurnClick: () -> Unit,
) {
    val isLoading = chatFirstTurnState is V1SectionState.Loading
    WorkspaceCard(title = "Chat-first Workspace Turn") {
        Text(
            text = "输入产品理解或获客方向；Android 只提交文本，backend Runtime 生成 Draft Review。",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(text = "当前 workspace version：$workspaceVersion", style = MaterialTheme.typography.bodyMedium)

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            ChatMessageTypeButton(
                label = "产品理解",
                selected = chatMessageType == "product_profile_update",
                onClick = { onChatMessageTypeChange("product_profile_update") },
                modifier = Modifier.weight(1f),
            )
            ChatMessageTypeButton(
                label = "获客方向",
                selected = chatMessageType == "lead_direction_update",
                onClick = { onChatMessageTypeChange("lead_direction_update") },
                modifier = Modifier.weight(1f),
            )
            ChatMessageTypeButton(
                label = "混合",
                selected = chatMessageType == "mixed_product_and_direction_update",
                onClick = { onChatMessageTypeChange("mixed_product_and_direction_update") },
                modifier = Modifier.weight(1f),
            )
        }

        OutlinedTextField(
            value = chatInput,
            onValueChange = onChatInputChange,
            modifier = Modifier.fillMaxWidth(),
            minLines = 3,
            label = { Text(text = "对 Sales Agent 说") },
            placeholder = { Text(text = "例如：我们做 FactoryOps AI，先找华东 100 到 500 人制造企业。") },
        )

        Button(
            onClick = onSubmitChatTurnClick,
            enabled = !isLoading && chatInput.isNotBlank(),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isLoading) "正在生成 Draft Review" else "提交 chat-first turn")
        }

        when (chatFirstTurnState) {
            V1SectionState.Idle -> Text(text = "尚未提交 chat-first 输入。", style = MaterialTheme.typography.bodyMedium)
            V1SectionState.Loading -> Text(text = "backend 正在创建 ConversationMessage / AgentRun / ContextPack。")
            V1SectionState.Empty -> Text(text = "本轮没有生成 Draft Review。", style = MaterialTheme.typography.bodyMedium)
            is V1SectionState.Failed -> {
                Text(text = chatFirstTurnState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = chatFirstTurnState.error.detail, style = MaterialTheme.typography.bodyMedium)
            }
            is V1SectionState.Loaded -> ChatFirstTurnDetails(chatFirstTurnState.value)
        }
    }
}

@Composable
private fun ChatMessageTypeButton(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    if (selected) {
        Button(onClick = onClick, modifier = modifier) {
            Text(text = label)
        }
    } else {
        OutlinedButton(onClick = onClick, modifier = modifier) {
            Text(text = label)
        }
    }
}

@Composable
private fun ChatFirstTurnDetails(response: SalesWorkspaceChatTurnResponseDto) {
    Text(text = "Message：${response.conversationMessage.id}", style = MaterialTheme.typography.bodyMedium)
    Text(text = "AgentRun：${response.agentRun.id} · ${response.agentRun.status}", style = MaterialTheme.typography.bodyMedium)
    Text(text = "Assistant：${response.assistantMessage.content}", style = MaterialTheme.typography.bodyMedium)
    response.draftReview?.let { review ->
        Text(
            text = "Draft Review：${review.id} · ${review.status}",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = "Preview version：${review.preview.previewWorkspaceVersion}；operations=${review.draft.operationCount}",
            style = MaterialTheme.typography.bodyMedium,
        )
    } ?: Text(
        text = "本轮没有 patch draft；workspace 未写入。",
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun PatchDraftReviewGate(
    workspaceVersion: Int,
    draftReviewState: V1SectionState<SalesWorkspaceDraftReviewDto>,
    applyState: V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>,
    onCreateDraftReviewClick: () -> Unit,
    onAcceptDraftReviewClick: () -> Unit,
    onRejectDraftReviewClick: () -> Unit,
    onApplyDraftReviewClick: () -> Unit,
) {
    val draftReview = (draftReviewState as? V1SectionState.Loaded<SalesWorkspaceDraftReviewDto>)?.value
    val draftReviewIsCurrent = draftReview?.baseWorkspaceVersion == workspaceVersion
    val isDraftReviewLoading = draftReviewState is V1SectionState.Loading
    val isApplyLoading = applyState is V1SectionState.Loading
    val canReview = draftReview?.status == "previewed" && draftReviewIsCurrent && !isDraftReviewLoading && !isApplyLoading
    val canApply = draftReview?.status == "reviewed" && draftReviewIsCurrent && !isDraftReviewLoading && !isApplyLoading

    WorkspaceCard(title = "PatchDraft Review Gate") {
        Text(
            text = "Android 只负责创建和审阅 Draft Review；正式写入由 Sales Workspace Kernel 校验。",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(text = "当前 workspace version：$workspaceVersion", style = MaterialTheme.typography.bodyMedium)

        Button(
            onClick = onCreateDraftReviewClick,
            enabled = !isDraftReviewLoading && !isApplyLoading,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isDraftReviewLoading) "正在创建 Draft Review" else "生成 Draft Review")
        }

        when (draftReviewState) {
            V1SectionState.Idle -> Text(
                text = "尚未生成 Draft Review。",
                style = MaterialTheme.typography.bodyMedium,
            )

            V1SectionState.Loading -> Text(
                text = "Runtime prototype 正在生成 deterministic draft，并由 backend 创建 Draft Review。",
                style = MaterialTheme.typography.bodyMedium,
            )

            V1SectionState.Empty -> Text(text = "暂无 Draft Review。", style = MaterialTheme.typography.bodyMedium)
            is V1SectionState.Failed -> {
                Text(text = draftReviewState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = draftReviewState.error.detail, style = MaterialTheme.typography.bodyMedium)
                Text(
                    text = "如出现 workspace_version_conflict、draft_review_expired 或 draft_review_state_conflict，请刷新 workspace 后重新生成 Draft Review。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            is V1SectionState.Loaded -> DraftReviewDetails(draftReviewState.value, draftReviewIsCurrent)
        }

        OutlinedButton(
            onClick = onAcceptDraftReviewClick,
            enabled = canReview,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "接受 Draft Review")
        }

        OutlinedButton(
            onClick = onRejectDraftReviewClick,
            enabled = canReview,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "拒绝 Draft Review")
        }

        OutlinedButton(
            onClick = onApplyDraftReviewClick,
            enabled = canApply,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isApplyLoading) "正在按 Review ID 应用" else "按 Review ID 应用")
        }

        if (draftReview != null && !draftReviewIsCurrent) {
            Text(
                text = "Draft Review 基于 version ${draftReview.baseWorkspaceVersion}，当前 workspace 已是 version $workspaceVersion。请刷新后重新生成。",
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
private fun DraftReviewDetails(
    draftReview: SalesWorkspaceDraftReviewDto,
    draftReviewIsCurrent: Boolean,
) {
    val topCandidate = draftReview.preview.previewTopCandidate
    Text(text = "Draft Review：${draftReview.id}", style = MaterialTheme.typography.bodyMedium)
    Text(text = "Status：${draftReview.status}", style = MaterialTheme.typography.bodyMedium)
    Text(text = "Draft：${draftReview.draft.id}", style = MaterialTheme.typography.bodyMedium)
    Text(text = "Materialized Patch：${draftReview.preview.materializedPatch.id}", style = MaterialTheme.typography.bodyMedium)
    Text(
        text = "Preview version：${draftReview.preview.previewWorkspaceVersion}；would_mutate=${draftReview.preview.wouldMutate}",
        style = MaterialTheme.typography.bodyMedium,
    )
    Text(text = "Operations：${draftReview.draft.operationCount}", style = MaterialTheme.typography.bodyMedium)
    draftReview.review?.let { review ->
        Text(
            text = "Review：${review.decision} by ${review.reviewedBy} (${review.client})",
            style = MaterialTheme.typography.bodyMedium,
        )
        if (review.comment.isNotBlank()) {
            Text(text = review.comment, style = MaterialTheme.typography.bodySmall)
        }
    }
    draftReview.applyResult?.let { result ->
        Text(text = "Apply result：${result.status}", style = MaterialTheme.typography.bodyMedium)
        result.materializedPatchId?.let {
            Text(text = "Applied patch：$it", style = MaterialTheme.typography.bodySmall)
        }
        result.workspaceVersion?.let {
            Text(text = "Applied workspace version：$it", style = MaterialTheme.typography.bodySmall)
        }
        result.errorCode?.let {
            Text(text = "Apply error：$it ${result.errorMessage.orEmpty()}", style = MaterialTheme.typography.bodySmall)
        }
    }
    Text(
        text = if (draftReviewIsCurrent) {
            "Draft Review 仍匹配当前 workspace version。"
        } else {
            "Draft Review 已过期，不能应用。"
        },
        style = MaterialTheme.typography.bodySmall,
        color = if (draftReviewIsCurrent) {
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
private fun PatchDraftApplyDetails(response: SalesWorkspaceDraftReviewApplyResponseDto) {
    val topCandidate = response.topCandidate
    Text(
        text = "已通过 ${response.draftReview.id} 应用 ${response.patch.id}，workspace version ${response.workspace.workspaceVersion}。",
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
