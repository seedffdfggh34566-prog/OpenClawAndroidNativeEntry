package com.openclaw.android.nativeentry.ui.workspace

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.outlined.Tune
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceChatTurnResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceConversationThreadDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceConversationMessageDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceConversationMessagesResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceConversationThreadsResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDefaultThreadId
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDemoWorkspaceId
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewApplyResponseDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDraftReviewPreviewDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspacePatchDraftDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspacePatchSummaryDto
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceReadOnlySnapshot
import com.openclaw.android.nativeentry.data.backend.SalesWorkspaceResponseDto
import com.openclaw.android.nativeentry.ui.shell.V1SectionState

@Composable
fun SalesWorkspaceScreen(
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    workspaceCreateState: V1SectionState<SalesWorkspaceResponseDto>,
    workspaceThreadState: V1SectionState<SalesWorkspaceConversationThreadsResponseDto>,
    selectedWorkspaceId: String = SalesWorkspaceDemoWorkspaceId,
    workspaceSelectorInput: String = SalesWorkspaceDemoWorkspaceId,
    selectedThreadId: String,
    workspaceMessageHistoryState: V1SectionState<SalesWorkspaceConversationMessagesResponseDto>,
    optimisticUserMessage: SalesWorkspaceConversationMessageDto?,
    draftReviewState: V1SectionState<SalesWorkspaceDraftReviewDto>,
    patchDraftApplyState: V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>,
    chatFirstTurnState: V1SectionState<SalesWorkspaceChatTurnResponseDto>,
    chatInput: String,
    chatMessageType: String,
    onRefreshClick: () -> Unit,
    onCreateWorkspaceClick: () -> Unit,
    onWorkspaceSelectorInputChange: (String) -> Unit = {},
    onSwitchWorkspaceClick: (String) -> Unit = {},
    onCreateThreadClick: (String) -> Unit,
    onThreadSelected: (String) -> Unit,
    onCreateDraftReviewClick: () -> Unit,
    onChatInputChange: (String) -> Unit,
    onChatMessageTypeChange: (String) -> Unit,
    onSubmitChatTurnClick: () -> Unit,
    onRetryChatTurnClick: () -> Unit = {},
    onAcceptDraftReviewClick: () -> Unit,
    onRejectDraftReviewClick: () -> Unit,
    onApplyDraftReviewClick: () -> Unit,
    modifier: Modifier = Modifier,
    initialShowSettings: Boolean = false,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(PaddingValues(horizontal = 16.dp, vertical = 12.dp)),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 1200.dp)
                .fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            when (workspaceState) {
                is V1SectionState.Loaded -> {
                    WorkspaceChatSurface(
                        snapshot = workspaceState.value,
                        threadState = workspaceThreadState,
                        selectedWorkspaceId = selectedWorkspaceId,
                        workspaceSelectorInput = workspaceSelectorInput,
                        selectedThreadId = selectedThreadId,
                        historyState = workspaceMessageHistoryState,
                        optimisticUserMessage = optimisticUserMessage,
                        draftReviewState = draftReviewState,
                        patchDraftApplyState = patchDraftApplyState,
                        chatFirstTurnState = chatFirstTurnState,
                        chatInput = chatInput,
                        chatMessageType = chatMessageType,
                        onRefreshClick = onRefreshClick,
                        onWorkspaceSelectorInputChange = onWorkspaceSelectorInputChange,
                        onSwitchWorkspaceClick = onSwitchWorkspaceClick,
                        onCreateThreadClick = onCreateThreadClick,
                        onThreadSelected = onThreadSelected,
                        onCreateDraftReviewClick = onCreateDraftReviewClick,
                        onChatInputChange = onChatInputChange,
                        onChatMessageTypeChange = onChatMessageTypeChange,
                        onSubmitChatTurnClick = onSubmitChatTurnClick,
                        onRetryChatTurnClick = onRetryChatTurnClick,
                        onAcceptDraftReviewClick = onAcceptDraftReviewClick,
                        onRejectDraftReviewClick = onRejectDraftReviewClick,
                        onApplyDraftReviewClick = onApplyDraftReviewClick,
                        modifier = Modifier.weight(1f),
                        initialShowSettings = initialShowSettings,
                    )
                }

                else -> {
                    WorkspaceChatHeader(
                        workspaceState = workspaceState,
                        onRefreshClick = onRefreshClick,
                    )
                    WorkspaceEntrySurface(
                        workspaceState = workspaceState,
                        createState = workspaceCreateState,
                        onCreateWorkspaceClick = onCreateWorkspaceClick,
                        modifier = Modifier.weight(1f),
                    )
                }
            }
        }
    }
}

@Composable
private fun WorkspaceChatHeader(
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    onRefreshClick: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            Text(
                text = "销售工作区",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = workspaceState.toWorkspaceStatusLabel(),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        OutlinedButton(onClick = onRefreshClick) {
            Text(text = "刷新")
        }
    }
}

@Composable
private fun WorkspaceEntrySurface(
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    createState: V1SectionState<SalesWorkspaceResponseDto>,
    onCreateWorkspaceClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        WorkspaceNotice(
            title = workspaceState.entryTitle(),
            message = workspaceState.entryMessage(),
        )
        WorkspaceOnboarding(
            workspaceState = workspaceState,
            createState = createState,
            onCreateWorkspaceClick = onCreateWorkspaceClick,
        )
    }
}

@Composable
private fun WorkspaceChatSurface(
    snapshot: SalesWorkspaceReadOnlySnapshot,
    threadState: V1SectionState<SalesWorkspaceConversationThreadsResponseDto>,
    selectedWorkspaceId: String,
    workspaceSelectorInput: String,
    selectedThreadId: String,
    historyState: V1SectionState<SalesWorkspaceConversationMessagesResponseDto>,
    optimisticUserMessage: SalesWorkspaceConversationMessageDto?,
    draftReviewState: V1SectionState<SalesWorkspaceDraftReviewDto>,
    patchDraftApplyState: V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>,
    chatFirstTurnState: V1SectionState<SalesWorkspaceChatTurnResponseDto>,
    chatInput: String,
    chatMessageType: String,
    onRefreshClick: () -> Unit,
    onWorkspaceSelectorInputChange: (String) -> Unit,
    onSwitchWorkspaceClick: (String) -> Unit,
    onCreateThreadClick: (String) -> Unit,
    onThreadSelected: (String) -> Unit,
    onCreateDraftReviewClick: () -> Unit,
    onChatInputChange: (String) -> Unit,
    onChatMessageTypeChange: (String) -> Unit,
    onSubmitChatTurnClick: () -> Unit,
    onRetryChatTurnClick: () -> Unit,
    onAcceptDraftReviewClick: () -> Unit,
    onRejectDraftReviewClick: () -> Unit,
    onApplyDraftReviewClick: () -> Unit,
    modifier: Modifier = Modifier,
    initialShowSettings: Boolean = false,
) {
    val isLoading = chatFirstTurnState is V1SectionState.Loading
    val latestTurn = (chatFirstTurnState as? V1SectionState.Loaded<SalesWorkspaceChatTurnResponseDto>)?.value
    val canSubmit = !isLoading && chatInput.isNotBlank()
    val transcriptScrollState = rememberScrollState()
    var showSettings by remember { mutableStateOf(initialShowSettings) }
    var showCreateThreadDialog by remember { mutableStateOf(false) }
    var newThreadTitle by remember { mutableStateOf("") }

    LaunchedEffect(historyState, chatFirstTurnState, transcriptScrollState.maxValue) {
        transcriptScrollState.scrollTo(transcriptScrollState.maxValue)
    }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        CompactWorkspaceHeader(
            snapshot = snapshot,
            threadState = threadState,
            selectedThreadId = selectedThreadId,
            isLoading = isLoading,
            showSettings = showSettings,
            onRefreshClick = onRefreshClick,
            onToggleSettingsClick = { showSettings = !showSettings },
        )

        ThreadSwitcher(
            threadState = threadState,
            selectedThreadId = selectedThreadId,
            onThreadSelected = onThreadSelected,
            onCreateThreadClick = {
                newThreadTitle = ""
                showCreateThreadDialog = true
            },
        )

        if (showCreateThreadDialog) {
            AlertDialog(
                onDismissRequest = { showCreateThreadDialog = false },
                title = { Text(text = "命名新对话") },
                text = {
                    OutlinedTextField(
                        value = newThreadTitle,
                        onValueChange = { newThreadTitle = it },
                        singleLine = true,
                        label = { Text(text = "对话名称") },
                        placeholder = { Text(text = "例如：连锁餐饮线索验证") },
                    )
                },
                dismissButton = {
                    OutlinedButton(onClick = { showCreateThreadDialog = false }) {
                        Text(text = "取消")
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            onCreateThreadClick(newThreadTitle.trim().ifBlank { "新对话" })
                            showCreateThreadDialog = false
                            newThreadTitle = ""
                        },
                    ) {
                        Text(text = "创建")
                    }
                },
            )
        }

        if (showSettings) {
            FoldedWorkspaceSettings(
                snapshot = snapshot,
                selectedWorkspaceId = selectedWorkspaceId,
                workspaceSelectorInput = workspaceSelectorInput,
                chatMessageType = chatMessageType,
                onWorkspaceSelectorInputChange = onWorkspaceSelectorInputChange,
                onSwitchWorkspaceClick = onSwitchWorkspaceClick,
                onChatMessageTypeChange = onChatMessageTypeChange,
            )
        }

        Surface(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            color = MaterialTheme.colorScheme.background,
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(transcriptScrollState)
                    .padding(horizontal = 4.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                ConversationTranscript(
                    historyState = historyState,
                    chatFirstTurnState = chatFirstTurnState,
                    latestTurn = latestTurn,
                    optimisticUserMessage = optimisticUserMessage?.takeIf { it.threadId == selectedThreadId },
                    draftReviewState = draftReviewState,
                    patchDraftApplyState = patchDraftApplyState,
                    workspaceVersion = snapshot.workspace.workspaceVersion,
                    onCreateDraftReviewClick = onCreateDraftReviewClick,
                    onAcceptDraftReviewClick = onAcceptDraftReviewClick,
                    onRejectDraftReviewClick = onRejectDraftReviewClick,
                    onApplyDraftReviewClick = onApplyDraftReviewClick,
                    onRetryChatTurnClick = onRetryChatTurnClick,
                )
            }
        }

        CompactChatComposer(
            chatInput = chatInput,
            chatMessageType = chatMessageType,
            canSubmit = canSubmit,
            isLoading = isLoading,
            onChatInputChange = onChatInputChange,
            onSubmitChatTurnClick = onSubmitChatTurnClick,
        )
    }
}

@Composable
private fun CompactWorkspaceHeader(
    snapshot: SalesWorkspaceReadOnlySnapshot,
    threadState: V1SectionState<SalesWorkspaceConversationThreadsResponseDto>,
    selectedThreadId: String,
    isLoading: Boolean,
    showSettings: Boolean,
    onRefreshClick: () -> Unit,
    onToggleSettingsClick: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            Text(
                text = selectedThreadTitle(threadState, selectedThreadId),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = if (isLoading) {
                    "Sales Agent 正在思考"
                } else {
                    "销售工作区 · v${snapshot.workspace.workspaceVersion}"
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
        Row(
            horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            OutlinedButton(
                onClick = onRefreshClick,
                modifier = Modifier.heightIn(min = 40.dp),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
            ) {
                Text(text = "刷新", style = MaterialTheme.typography.labelMedium)
            }
            Button(
                onClick = onToggleSettingsClick,
                modifier = Modifier.heightIn(min = 40.dp),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
            ) {
                Icon(
                    imageVector = Icons.Outlined.Tune,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                )
                Text(
                    text = if (showSettings) "收起" else "设置",
                    style = MaterialTheme.typography.labelMedium,
                )
            }
        }
    }
}

@Composable
private fun ThreadSwitcher(
    threadState: V1SectionState<SalesWorkspaceConversationThreadsResponseDto>,
    selectedThreadId: String,
    onThreadSelected: (String) -> Unit,
    onCreateThreadClick: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Row(
            modifier = Modifier
                .weight(1f)
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            val threads = (threadState as? V1SectionState.Loaded<SalesWorkspaceConversationThreadsResponseDto>)
                ?.value
                ?.threads
                .orEmpty()
                .ifEmpty {
                    listOf(
                        com.openclaw.android.nativeentry.data.backend.SalesWorkspaceConversationThreadDto(
                            id = SalesWorkspaceDefaultThreadId,
                            title = "主对话",
                            status = "active",
                        ),
                    )
                }
            threads.forEach { thread ->
                ChatMessageTypeButton(
                    label = thread.title.ifBlank { thread.id },
                    selected = thread.id == selectedThreadId,
                    onClick = { onThreadSelected(thread.id) },
                    modifier = Modifier.widthIn(min = 112.dp, max = 196.dp),
                )
            }
        }
        Button(
            onClick = onCreateThreadClick,
            modifier = Modifier.heightIn(min = 40.dp),
            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
        ) {
            Icon(
                imageVector = Icons.Filled.Add,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Text(text = "新对话")
        }
    }

    when (threadState) {
        V1SectionState.Loading -> TranscriptStatusText("正在同步对话列表。")
        is V1SectionState.Failed -> TranscriptStatusText("对话列表同步失败：${threadState.error.title}")
        V1SectionState.Empty,
        V1SectionState.Idle,
        is V1SectionState.Loaded -> Unit
    }
}

@Composable
private fun ConversationTranscript(
    historyState: V1SectionState<SalesWorkspaceConversationMessagesResponseDto>,
    chatFirstTurnState: V1SectionState<SalesWorkspaceChatTurnResponseDto>,
    latestTurn: SalesWorkspaceChatTurnResponseDto?,
    optimisticUserMessage: SalesWorkspaceConversationMessageDto?,
    draftReviewState: V1SectionState<SalesWorkspaceDraftReviewDto>,
    patchDraftApplyState: V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>,
    workspaceVersion: Int,
    onCreateDraftReviewClick: () -> Unit,
    onAcceptDraftReviewClick: () -> Unit,
    onRejectDraftReviewClick: () -> Unit,
    onApplyDraftReviewClick: () -> Unit,
    onRetryChatTurnClick: () -> Unit,
) {
    val messages = (historyState as? V1SectionState.Loaded<SalesWorkspaceConversationMessagesResponseDto>)
        ?.value
        ?.messages
        .orEmpty()
    val visibleMessages = buildList<SalesWorkspaceConversationMessageDto> {
        fun addIfMissing(message: SalesWorkspaceConversationMessageDto?) {
            if (message != null && none { it.id == message.id }) {
                add(message)
            }
        }
        messages.forEach(::addIfMissing)
        addIfMissing(optimisticUserMessage)
        addIfMissing(latestTurn?.conversationMessage)
        addIfMissing(latestTurn?.assistantMessage)
    }

    if (historyState is V1SectionState.Loading && visibleMessages.isEmpty()) {
        TranscriptStatusText("正在同步最近对话。")
    }

    if (historyState is V1SectionState.Failed && visibleMessages.isEmpty()) {
        AssistantErrorMessage(
            title = historyState.error.title,
            detail = historyState.error.detail,
        )
    }

    if (visibleMessages.isEmpty()) {
        AssistantWelcomeMessage()
    } else {
        visibleMessages.takeLast(24).forEach { message ->
            ConversationMessageBubble(message)
            if (message.id == latestTurn?.assistantMessage?.id) {
                latestTurn.draftReview?.let {
                    DraftReviewAttachment(
                        workspaceVersion = workspaceVersion,
                        draftReviewState = draftReviewState,
                        applyState = patchDraftApplyState,
                        onCreateDraftReviewClick = onCreateDraftReviewClick,
                        onAcceptDraftReviewClick = onAcceptDraftReviewClick,
                        onRejectDraftReviewClick = onRejectDraftReviewClick,
                        onApplyDraftReviewClick = onApplyDraftReviewClick,
                        showCreateDraftReviewButton = false,
                    )
                }
            }
        }
    }

    when (chatFirstTurnState) {
        V1SectionState.Loading -> AssistantThinkingMessage()
        is V1SectionState.Failed -> AssistantErrorMessage(
            title = chatFirstTurnState.error.title,
            detail = chatFirstTurnState.error.detail.toLlmFriendlyError(),
            onRetryClick = onRetryChatTurnClick.takeIf {
                chatFirstTurnState.error.detail.isRetryableLlmTurnError()
            },
        )
        V1SectionState.Empty -> TranscriptStatusText("本轮没有新的回复。")
        V1SectionState.Idle,
        is V1SectionState.Loaded -> Unit
    }
}

@Composable
private fun CompactChatComposer(
    chatInput: String,
    chatMessageType: String,
    canSubmit: Boolean,
    isLoading: Boolean,
    onChatInputChange: (String) -> Unit,
    onSubmitChatTurnClick: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .imePadding(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.Bottom,
            ) {
                OutlinedTextField(
                    value = chatInput,
                    onValueChange = onChatInputChange,
                    modifier = Modifier
                        .weight(1f)
                        .heightIn(min = 52.dp, max = 112.dp),
                    minLines = 1,
                    maxLines = 3,
                    enabled = !isLoading,
                    label = { Text(text = "对 Sales Agent 说") },
                    placeholder = { Text(text = "例如：我们做工业设备维保软件，帮工厂减少停机时间。") },
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(
                        onSend = {
                            if (canSubmit) {
                                onSubmitChatTurnClick()
                            }
                        },
                    ),
                )

                IconButton(
                    onClick = onSubmitChatTurnClick,
                    enabled = canSubmit,
                    modifier = Modifier
                        .size(52.dp),
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.Send,
                        contentDescription = if (isLoading) "思考中" else "发送",
                    )
                }
            }
            Text(
                text = "模式：${chatMessageType.toConversationTypeLabel()}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun FoldedWorkspaceSettings(
    snapshot: SalesWorkspaceReadOnlySnapshot,
    selectedWorkspaceId: String,
    workspaceSelectorInput: String,
    chatMessageType: String,
    onWorkspaceSelectorInputChange: (String) -> Unit,
    onSwitchWorkspaceClick: (String) -> Unit,
    onChatMessageTypeChange: (String) -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(max = 300.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
    ) {
        Column(
            modifier = Modifier
                .verticalScroll(rememberScrollState())
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = "开发测试工作区 ID",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.SemiBold,
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                OutlinedTextField(
                    value = workspaceSelectorInput,
                    onValueChange = onWorkspaceSelectorInputChange,
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    label = { Text(text = "Workspace ID") },
                    placeholder = { Text(text = SalesWorkspaceDemoWorkspaceId) },
                )
                Button(
                    onClick = { onSwitchWorkspaceClick(workspaceSelectorInput) },
                    enabled = workspaceSelectorInput.trim().isNotEmpty(),
                ) {
                    Text(text = "切换/创建")
                }
            }
            Text(
                text = "当前：$selectedWorkspaceId",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            HorizontalDivider()
            Text(
                text = "回复模式",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.SemiBold,
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                ChatMessageTypeButton(
                    label = "产品理解",
                    selected = chatMessageType == "product_profile_update",
                    onClick = { onChatMessageTypeChange("product_profile_update") },
                    modifier = Modifier.widthIn(min = 96.dp),
                )
                ChatMessageTypeButton(
                    label = "找客户建议",
                    selected = chatMessageType == "lead_direction_update",
                    onClick = { onChatMessageTypeChange("lead_direction_update") },
                    modifier = Modifier.widthIn(min = 116.dp),
                )
                ChatMessageTypeButton(
                    label = "产品+找客户",
                    selected = chatMessageType == "mixed_product_and_direction_update",
                    onClick = { onChatMessageTypeChange("mixed_product_and_direction_update") },
                    modifier = Modifier.widthIn(min = 126.dp),
                )
                ChatMessageTypeButton(
                    label = "解释当前判断",
                    selected = chatMessageType == "workspace_question",
                    onClick = { onChatMessageTypeChange("workspace_question") },
                    modifier = Modifier.widthIn(min = 132.dp),
                )
            }
            HorizontalDivider()
            Text(
                text = "工作区详情",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.SemiBold,
            )
            WorkspaceDetailsSection(snapshot)
        }
    }
}

@Composable
private fun AssistantWelcomeMessage() {
    ConversationMessageBubble(
        message = SalesWorkspaceConversationMessageDto(
            id = "local_welcome",
            threadId = SalesWorkspaceDefaultThreadId,
            role = "assistant",
            messageType = "welcome",
            content = "直接告诉我你卖什么，或问“我的客户是谁”“我该怎么找第一批客户”。我会先给建议，再把可保存的信息整理到工作区。",
        ),
    )
}

@Composable
private fun ConversationMessageBubble(message: SalesWorkspaceConversationMessageDto) {
    val isUser = message.role == "user"
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start,
    ) {
        Card(
            modifier = Modifier.widthIn(max = 620.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (isUser) {
                    MaterialTheme.colorScheme.primaryContainer
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                },
            ),
        ) {
            Column(
                modifier = Modifier.padding(14.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                if (!isUser) {
                    Text(
                        text = message.role.toConversationSpeaker(),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Text(text = message.content, style = MaterialTheme.typography.bodyMedium)
                if (isUser) {
                    Text(
                        text = message.messageType.toConversationTypeLabel(),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

@Composable
private fun AssistantThinkingMessage() {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Start) {
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
            Text(
                text = "Sales Agent 正在思考...",
                modifier = Modifier.padding(14.dp),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun AssistantErrorMessage(
    title: String,
    detail: String,
    onRetryClick: (() -> Unit)? = null,
) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Start) {
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)) {
            Column(
                modifier = Modifier.padding(14.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Text(text = title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                Text(text = detail, style = MaterialTheme.typography.bodyMedium)
                if (onRetryClick != null) {
                    OutlinedButton(onClick = onRetryClick) {
                        Text(text = "重试")
                    }
                }
            }
        }
    }
}

@Composable
private fun TranscriptStatusText(message: String) {
    Text(
        text = message,
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
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
            Text(
                text = label,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    } else {
        OutlinedButton(onClick = onClick, modifier = modifier) {
            Text(
                text = label,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun DraftReviewAttachment(
    workspaceVersion: Int,
    draftReviewState: V1SectionState<SalesWorkspaceDraftReviewDto>,
    applyState: V1SectionState<SalesWorkspaceDraftReviewApplyResponseDto>,
    onCreateDraftReviewClick: () -> Unit,
    onAcceptDraftReviewClick: () -> Unit,
    onRejectDraftReviewClick: () -> Unit,
    onApplyDraftReviewClick: () -> Unit,
    showCreateDraftReviewButton: Boolean,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            val draftReview = (draftReviewState as? V1SectionState.Loaded<SalesWorkspaceDraftReviewDto>)?.value
            val isApplied = draftReview?.status == "applied"
            Text(
                text = if (isApplied) "已沉淀到工作区" else "可保存到工作区",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = if (isApplied) {
                    "本轮有价值信息已自动更新到当前产品理解或获客方向卡。"
                } else {
                    "这是本轮对话整理出的保存建议；写入前不会改变正式工作区。"
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            PatchDraftReviewGate(
                workspaceVersion = workspaceVersion,
                draftReviewState = draftReviewState,
                applyState = applyState,
                onCreateDraftReviewClick = onCreateDraftReviewClick,
                onAcceptDraftReviewClick = onAcceptDraftReviewClick,
                onRejectDraftReviewClick = onRejectDraftReviewClick,
                onApplyDraftReviewClick = onApplyDraftReviewClick,
                showCreateDraftReviewButton = showCreateDraftReviewButton,
            )
        }
    }
}

@Composable
private fun WorkspaceDetailsSection(snapshot: SalesWorkspaceReadOnlySnapshot) {
    HorizontalDivider()
    Text(
        text = "详情 / 调试",
        style = MaterialTheme.typography.labelLarge,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    WorkspaceContent(snapshot)
}

@Composable
private fun WorkspaceOnboarding(
    workspaceState: V1SectionState<SalesWorkspaceReadOnlySnapshot>,
    createState: V1SectionState<SalesWorkspaceResponseDto>,
    onCreateWorkspaceClick: () -> Unit,
) {
    val isLoaded = workspaceState is V1SectionState.Loaded
    val isCreating = createState is V1SectionState.Loading
    WorkspaceCard(title = "销售工作区入口") {
        Text(
            text = "点击后进入默认销售工作区，再用自然语言描述产品和获客方向。",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Button(
            onClick = onCreateWorkspaceClick,
            enabled = !isLoaded && !isCreating,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = if (isCreating) "正在进入销售工作区" else "开始销售工作区")
        }
        when (createState) {
            V1SectionState.Idle -> Text(
                text = if (isLoaded) "已进入销售工作区，可以开始聊天。" else "首次使用时先进入销售工作区。",
                style = MaterialTheme.typography.bodyMedium,
            )
            V1SectionState.Loading -> Text(text = "正在创建或进入默认销售工作区。")
            V1SectionState.Empty -> Text(text = "尚未进入销售工作区。", style = MaterialTheme.typography.bodyMedium)
            is V1SectionState.Failed -> {
                Text(text = createState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = createState.error.detail, style = MaterialTheme.typography.bodyMedium)
            }
            is V1SectionState.Loaded -> {
                val workspace = createState.value.workspace
                Text(
                    text = "已进入 ${workspace.id}，version ${workspace.workspaceVersion}。",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
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
    showCreateDraftReviewButton: Boolean,
) {
    val draftReview = (draftReviewState as? V1SectionState.Loaded<SalesWorkspaceDraftReviewDto>)?.value
    val draftReviewIsCurrent = draftReview?.baseWorkspaceVersion == workspaceVersion
    val isDraftReviewLoading = draftReviewState is V1SectionState.Loading
    val isApplyLoading = applyState is V1SectionState.Loading
    val isApplied = draftReview?.status == "applied"
    val canReview = draftReview?.status == "previewed" && draftReviewIsCurrent && !isDraftReviewLoading && !isApplyLoading
    val canApply = draftReview?.status == "reviewed" && draftReviewIsCurrent && !isDraftReviewLoading && !isApplyLoading
    var showDetails by remember(draftReview?.id) { mutableStateOf(false) }

    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        if (showCreateDraftReviewButton && draftReviewState !is V1SectionState.Loaded) {
            Button(
                onClick = onCreateDraftReviewClick,
                enabled = !isDraftReviewLoading && !isApplyLoading,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = if (isDraftReviewLoading) "正在生成更新建议" else "生成可审阅更新")
            }
        }

        when (draftReviewState) {
            V1SectionState.Idle -> Text(text = "尚未生成可审阅更新。", style = MaterialTheme.typography.bodyMedium)
            V1SectionState.Loading -> Text(text = "正在生成预览。", style = MaterialTheme.typography.bodyMedium)
            V1SectionState.Empty -> Text(text = "本轮暂无可审阅更新。", style = MaterialTheme.typography.bodyMedium)
            is V1SectionState.Failed -> {
                Text(text = draftReviewState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = draftReviewState.error.detail, style = MaterialTheme.typography.bodyMedium)
            }
            is V1SectionState.Loaded -> {
                DraftReviewCompactSummary(draftReviewState.value, workspaceVersion)
                if (showDetails) {
                    DraftReviewDetails(draftReviewState.value, draftReviewIsCurrent)
                }
                OutlinedButton(
                    onClick = { showDetails = !showDetails },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = if (showDetails) "收起详情" else "查看更新详情")
                }
            }
        }

        if (!isApplied && (draftReview?.status == "previewed" || draftReview?.status == "reviewed" || isApplyLoading)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                OutlinedButton(
                    onClick = onAcceptDraftReviewClick,
                    enabled = canReview,
                    modifier = Modifier.weight(1f),
                ) {
                    Text(text = "采纳")
                }
                OutlinedButton(
                    onClick = onRejectDraftReviewClick,
                    enabled = canReview,
                    modifier = Modifier.weight(1f),
                ) {
                    Text(text = "不采纳")
                }
                Button(
                    onClick = onApplyDraftReviewClick,
                    enabled = canApply,
                    modifier = Modifier.weight(1f),
                ) {
                    Text(text = if (isApplyLoading) "写入中" else "写入")
                }
            }
        }

        if (draftReview != null && !draftReviewIsCurrent && draftReview.status in setOf("previewed", "reviewed")) {
            Text(
                text = "这条更新基于版本 ${draftReview.baseWorkspaceVersion}，当前工作区已是版本 $workspaceVersion。请刷新后重新生成。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error,
            )
        }

        when (applyState) {
            V1SectionState.Idle,
            V1SectionState.Empty -> Unit
            V1SectionState.Loading -> Text(text = "正在通过后端审阅门禁写入。", style = MaterialTheme.typography.bodyMedium)
            is V1SectionState.Failed -> {
                Text(text = applyState.error.title, style = MaterialTheme.typography.titleSmall)
                Text(text = applyState.error.detail, style = MaterialTheme.typography.bodyMedium)
            }
            is V1SectionState.Loaded -> PatchDraftApplyDetails(applyState.value)
        }
    }
}

@Composable
private fun DraftReviewCompactSummary(
    draftReview: SalesWorkspaceDraftReviewDto,
    workspaceVersion: Int,
) {
    val stateText = "状态：${draftReview.status.toDraftReviewStatusLabel()} · 当前工作区 v$workspaceVersion"
    Text(text = stateText, style = MaterialTheme.typography.bodyMedium)
    val summaryText = if (draftReview.status == "applied") {
        "已沉淀 ${draftReview.draft.operationCount} 项，当前卡片已更新到 v${draftReview.applyResult?.workspaceVersion ?: workspaceVersion}。"
    } else {
        "预计保存 ${draftReview.draft.operationCount} 项，预览后为 v${draftReview.preview.previewWorkspaceVersion}。"
    }
    Text(
        text = summaryText,
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    draftReview.applyResult?.workspaceVersion?.let { version ->
        Text(
            text = "已写入工作区 v$version。",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun DraftReviewDetails(
    draftReview: SalesWorkspaceDraftReviewDto,
    draftReviewIsCurrent: Boolean,
) {
    val topCandidate = draftReview.preview.previewTopCandidate
    Text(
        text = "更新建议状态：${draftReview.status.toDraftReviewStatusLabel()}",
        style = MaterialTheme.typography.bodyMedium,
    )
    Text(
        text = "预计改动：${draftReview.draft.operationCount} 项；预览后版本：${draftReview.preview.previewWorkspaceVersion}",
        style = MaterialTheme.typography.bodyMedium,
    )
    draftReview.review?.let { review ->
        Text(
            text = "当前决策：${review.decision.toDraftReviewDecisionLabel()}",
            style = MaterialTheme.typography.bodyMedium,
        )
        if (review.comment.isNotBlank()) {
            Text(text = review.comment, style = MaterialTheme.typography.bodySmall)
        }
    }
    val isApplied = draftReview.status == "applied"
    draftReview.applyResult?.let { result ->
        Text(text = "写入结果：${result.status.toDraftReviewApplyStatusLabel()}", style = MaterialTheme.typography.bodyMedium)
        result.workspaceVersion?.let {
            Text(text = "工作区已更新到版本 $it。", style = MaterialTheme.typography.bodySmall)
        }
        result.errorCode?.let {
            Text(text = "写入失败：${result.errorMessage.orEmpty()}", style = MaterialTheme.typography.bodySmall)
        }
    }
    val reviewFreshnessText = when {
        isApplied -> "这条更新已写入工作区。"
        draftReviewIsCurrent -> "这条更新仍匹配当前工作区。"
        else -> "这条更新已过期，不能写入。"
    }
    Text(
        text = reviewFreshnessText,
        style = MaterialTheme.typography.bodySmall,
        color = if (!isApplied && !draftReviewIsCurrent) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant,
    )
    if (topCandidate == null) {
        Text(text = "预览排序暂无候选。", style = MaterialTheme.typography.bodyMedium)
    } else {
        Text(
            text = "预览第一候选：#${topCandidate.rank} ${topCandidate.candidateName} · ${topCandidate.score}",
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
        text = "已写入工作区，当前版本 ${response.workspace.workspaceVersion}。",
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

    WorkspaceCard(title = "工作区") {
        Text(text = workspace.name, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
        Text(text = "目标：${workspace.goal.ifBlank { "-" }}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "状态：${workspace.status} · 版本 ${workspace.workspaceVersion}", style = MaterialTheme.typography.bodyMedium)
    }

    WorkspaceCard(title = "当前产品理解") {
        if (product == null) {
            Text(text = "暂无当前产品画像。", style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = product.productName, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
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

    WorkspaceCard(title = "ContextPack / Projection") {
        val contextPack = snapshot.contextPack
        if (contextPack == null) {
            Text(text = "暂无 ContextPack。", style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = "ContextPack：${contextPack.id}", style = MaterialTheme.typography.bodySmall)
            contextPack.topCandidates.take(3).forEach { candidate ->
                Text(
                    text = "#${candidate.rank} ${candidate.name} · ${candidate.score}",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
        val files = snapshot.projection?.files.orEmpty().keys.sorted()
        Text(
            text = if (files.isEmpty()) "暂无 projection 文件。" else "Projection：${files.joinToString()}",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun WorkspaceNotice(title: String, message: String) {
    WorkspaceCard(title = title) {
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
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
            )
            content()
        }
    }
}

private fun V1SectionState<SalesWorkspaceReadOnlySnapshot>.toWorkspaceStatusLabel(): String =
    when (this) {
        V1SectionState.Idle -> "尚未同步"
        V1SectionState.Loading -> "正在同步 Sales Workspace"
        V1SectionState.Empty -> "尚未进入工作区"
        is V1SectionState.Failed -> "连接或读取失败"
        is V1SectionState.Loaded -> "会话已连接 · v${value.workspace.workspaceVersion}"
    }

private fun V1SectionState<SalesWorkspaceReadOnlySnapshot>.entryTitle(): String =
    when (this) {
        V1SectionState.Idle -> "尚未读取工作区"
        V1SectionState.Loading -> "正在读取工作区"
        V1SectionState.Empty -> "还没有可展示的工作区"
        is V1SectionState.Failed -> error.title
        is V1SectionState.Loaded -> "已进入销售工作区"
    }

private fun V1SectionState<SalesWorkspaceReadOnlySnapshot>.entryMessage(): String =
    when (this) {
        V1SectionState.Idle -> "点击开始后进入默认销售工作区。"
        V1SectionState.Loading -> "正在连接后端并同步会话。"
        V1SectionState.Empty -> "点击开始销售工作区后即可进入对话。"
        is V1SectionState.Failed -> if (error.title == "默认销售工作区尚未创建") {
            error.detail
        } else {
            "${error.detail}\n请确认后端已启动，并已执行 adb reverse tcp:8013 tcp:8013。"
        }
        is V1SectionState.Loaded -> "可以开始对话。"
    }

private fun String.toLlmFriendlyError(): String =
    when {
        contains("tokenhub_api_key_missing") || contains("llm_runtime_unavailable") -> {
            "这轮生成超时或真实 LLM 暂不可用。刚才的输入已保留，请点重试；如果连续失败，再检查 backend/.env 或后端启动参数。"
        }
        else -> this
    }

private fun String.isRetryableLlmTurnError(): Boolean =
    contains("llm_runtime_unavailable") ||
        contains("tokenhub_request_timeout") ||
        contains("timeout", ignoreCase = true) ||
        contains("timed out", ignoreCase = true) ||
        contains("unavailable", ignoreCase = true)

private fun List<String>.joinToDisplayText(): String =
    if (isEmpty()) "-" else joinToString("、")

private fun String.toConversationSpeaker(): String =
    when (this) {
        "user" -> "你"
        "assistant" -> "Sales Agent"
        else -> this
    }

private fun String.toConversationTypeLabel(): String =
    when (this) {
        "product_profile_update" -> "产品理解"
        "lead_direction_update" -> "找客户建议"
        "mixed_product_and_direction_update" -> "产品+找客户"
        "workspace_question" -> "解释判断"
        "clarifying_question" -> "追问"
        "draft_summary" -> "更新建议"
        "welcome" -> "欢迎"
        "out_of_scope_v2_2" -> "超出范围"
        else -> this
    }

private fun selectedThreadTitle(
    threadState: V1SectionState<SalesWorkspaceConversationThreadsResponseDto>,
    selectedThreadId: String,
): String {
    val thread = (threadState as? V1SectionState.Loaded<SalesWorkspaceConversationThreadsResponseDto>)
        ?.value
        ?.threads
        ?.firstOrNull { it.id == selectedThreadId }
    return thread?.title?.takeIf { it.isNotBlank() }
        ?: if (selectedThreadId == SalesWorkspaceDefaultThreadId) "主对话" else selectedThreadId
}

private fun String.toDraftReviewStatusLabel(): String =
    when (this) {
        "previewed" -> "待确认"
        "reviewed" -> "已确认"
        "rejected" -> "已拒绝"
        "applied" -> "已写入"
        else -> this
    }

private fun String.toDraftReviewApplyStatusLabel(): String =
    when (this) {
        "applied" -> "已写入"
        "failed" -> "写入失败"
        else -> this
    }

private fun String.toDraftReviewDecisionLabel(): String =
    when (this) {
        "accept" -> "采纳"
        "reject" -> "不采纳"
        else -> this
    }

@Preview(name = "Workspace long transcript", widthDp = 360, heightDp = 800, showBackground = true)
@Composable
private fun WorkspaceLongTranscriptPhonePreview() {
    MaterialTheme {
        SalesWorkspaceScreen(
            workspaceState = V1SectionState.Loaded(sampleWorkspaceSnapshot()),
            workspaceCreateState = V1SectionState.Idle,
            workspaceThreadState = V1SectionState.Loaded(sampleThreads()),
            selectedThreadId = "thread_factory",
            workspaceMessageHistoryState = V1SectionState.Loaded(
                SalesWorkspaceConversationMessagesResponseDto(sampleConversationMessages()),
            ),
            optimisticUserMessage = null,
            draftReviewState = V1SectionState.Idle,
            patchDraftApplyState = V1SectionState.Idle,
            chatFirstTurnState = V1SectionState.Idle,
            chatInput = "",
            chatMessageType = "product_profile_update",
            onRefreshClick = {},
            onCreateWorkspaceClick = {},
            onCreateThreadClick = { _ -> },
            onThreadSelected = {},
            onCreateDraftReviewClick = {},
            onChatInputChange = {},
            onChatMessageTypeChange = {},
            onSubmitChatTurnClick = {},
            onAcceptDraftReviewClick = {},
            onRejectDraftReviewClick = {},
            onApplyDraftReviewClick = {},
        )
    }
}

@Preview(name = "Workspace empty welcome", widthDp = 360, heightDp = 800, showBackground = true)
@Composable
private fun WorkspaceEmptyWelcomePreview() {
    MaterialTheme {
        SalesWorkspaceScreen(
            workspaceState = V1SectionState.Loaded(sampleWorkspaceSnapshot()),
            workspaceCreateState = V1SectionState.Idle,
            workspaceThreadState = V1SectionState.Loaded(sampleThreads()),
            selectedThreadId = SalesWorkspaceDefaultThreadId,
            workspaceMessageHistoryState = V1SectionState.Loaded(SalesWorkspaceConversationMessagesResponseDto(emptyList())),
            optimisticUserMessage = null,
            draftReviewState = V1SectionState.Idle,
            patchDraftApplyState = V1SectionState.Idle,
            chatFirstTurnState = V1SectionState.Idle,
            chatInput = "",
            chatMessageType = "workspace_question",
            onRefreshClick = {},
            onCreateWorkspaceClick = {},
            onCreateThreadClick = { _ -> },
            onThreadSelected = {},
            onCreateDraftReviewClick = {},
            onChatInputChange = {},
            onChatMessageTypeChange = {},
            onSubmitChatTurnClick = {},
            onAcceptDraftReviewClick = {},
            onRejectDraftReviewClick = {},
            onApplyDraftReviewClick = {},
        )
    }
}

@Preview(name = "Workspace thinking", widthDp = 360, heightDp = 800, showBackground = true)
@Composable
private fun WorkspaceAssistantThinkingPreview() {
    MaterialTheme {
        SalesWorkspaceScreen(
            workspaceState = V1SectionState.Loaded(sampleWorkspaceSnapshot()),
            workspaceCreateState = V1SectionState.Idle,
            workspaceThreadState = V1SectionState.Loaded(sampleThreads()),
            selectedThreadId = "thread_food",
            workspaceMessageHistoryState = V1SectionState.Loaded(
                SalesWorkspaceConversationMessagesResponseDto(sampleConversationMessages().take(4)),
            ),
            optimisticUserMessage = SalesWorkspaceConversationMessageDto(
                id = "local_pending_preview",
                threadId = "thread_food",
                role = "user",
                messageType = "lead_direction_update",
                content = "我们补充一下客户主要是直营门店。",
            ),
            draftReviewState = V1SectionState.Idle,
            patchDraftApplyState = V1SectionState.Idle,
            chatFirstTurnState = V1SectionState.Loading,
            chatInput = "我们补充一下客户主要是直营门店。",
            chatMessageType = "lead_direction_update",
            onRefreshClick = {},
            onCreateWorkspaceClick = {},
            onCreateThreadClick = { _ -> },
            onThreadSelected = {},
            onCreateDraftReviewClick = {},
            onChatInputChange = {},
            onChatMessageTypeChange = {},
            onSubmitChatTurnClick = {},
            onAcceptDraftReviewClick = {},
            onRejectDraftReviewClick = {},
            onApplyDraftReviewClick = {},
        )
    }
}

@Preview(name = "Workspace folded settings", widthDp = 360, heightDp = 800, showBackground = true)
@Composable
private fun WorkspaceFoldedSettingsPreview() {
    MaterialTheme {
        WorkspaceChatSurface(
            snapshot = sampleWorkspaceSnapshot(),
            threadState = V1SectionState.Loaded(sampleThreads()),
            selectedWorkspaceId = SalesWorkspaceDemoWorkspaceId,
            workspaceSelectorInput = SalesWorkspaceDemoWorkspaceId,
            selectedThreadId = "thread_factory",
            historyState = V1SectionState.Loaded(
                SalesWorkspaceConversationMessagesResponseDto(sampleConversationMessages()),
            ),
            optimisticUserMessage = null,
            draftReviewState = V1SectionState.Idle,
            patchDraftApplyState = V1SectionState.Idle,
            chatFirstTurnState = V1SectionState.Idle,
            chatInput = "",
            chatMessageType = "mixed_product_and_direction_update",
            onRefreshClick = {},
            onWorkspaceSelectorInputChange = {},
            onSwitchWorkspaceClick = {},
            onCreateThreadClick = { _ -> },
            onThreadSelected = {},
            onCreateDraftReviewClick = {},
            onChatInputChange = {},
            onChatMessageTypeChange = {},
            onSubmitChatTurnClick = {},
            onRetryChatTurnClick = {},
            onAcceptDraftReviewClick = {},
            onRejectDraftReviewClick = {},
            onApplyDraftReviewClick = {},
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            initialShowSettings = true,
        )
    }
}

@Preview(name = "Draft review attachment", widthDp = 360, showBackground = true)
@Composable
private fun WorkspaceDraftReviewAttachmentPreview() {
    MaterialTheme {
        DraftReviewAttachment(
            workspaceVersion = 2,
            draftReviewState = V1SectionState.Loaded(sampleDraftReview()),
            applyState = V1SectionState.Idle,
            onCreateDraftReviewClick = {},
            onAcceptDraftReviewClick = {},
            onRejectDraftReviewClick = {},
            onApplyDraftReviewClick = {},
            showCreateDraftReviewButton = false,
        )
    }
}

private fun sampleWorkspaceSnapshot(): SalesWorkspaceReadOnlySnapshot =
    SalesWorkspaceReadOnlySnapshot(
        workspace = SalesWorkspaceDto(
            id = "ws_demo",
            name = "销售工作区",
            goal = "用对话澄清产品、客户和获客方向",
            status = "active",
            workspaceVersion = 2,
            currentProductProfileRevisionId = null,
            currentLeadDirectionVersionId = null,
            productProfileRevisions = emptyMap(),
            leadDirectionVersions = emptyMap(),
            rankingBoard = null,
        ),
        rankingBoard = null,
        projection = null,
        contextPack = null,
    )

private fun sampleThreads(): SalesWorkspaceConversationThreadsResponseDto =
    SalesWorkspaceConversationThreadsResponseDto(
        threads = listOf(
            SalesWorkspaceConversationThreadDto(
                id = SalesWorkspaceDefaultThreadId,
                title = "主对话",
                status = "active",
            ),
            SalesWorkspaceConversationThreadDto(
                id = "thread_factory",
                title = "工厂维保",
                status = "active",
            ),
            SalesWorkspaceConversationThreadDto(
                id = "thread_food",
                title = "连锁餐饮",
                status = "active",
            ),
        ),
    )

private fun sampleConversationMessages(): List<SalesWorkspaceConversationMessageDto> =
    listOf(
        SalesWorkspaceConversationMessageDto(
            id = "msg_1",
            threadId = "thread_factory",
            role = "assistant",
            messageType = "welcome",
            content = "可以直接告诉我你卖什么、客户是谁、现在想验证哪类销售方向。",
        ),
        SalesWorkspaceConversationMessageDto(
            id = "msg_2",
            threadId = "thread_factory",
            role = "user",
            messageType = "product_profile_update",
            content = "我们做工业设备维保软件，帮工厂减少停机时间。",
        ),
        SalesWorkspaceConversationMessageDto(
            id = "msg_3",
            threadId = "thread_factory",
            role = "assistant",
            messageType = "clarifying_question",
            content = "收到。为了把产品理解补完整，我需要确认：主要设备类型是什么，目标客户是终端工厂还是设备制造商，当前交付是 SaaS 还是本地部署？",
        ),
        SalesWorkspaceConversationMessageDto(
            id = "msg_4",
            threadId = "thread_factory",
            role = "user",
            messageType = "lead_direction_update",
            content = "优先面向华东的中大型制造工厂，设备运维团队比较成熟。",
        ),
        SalesWorkspaceConversationMessageDto(
            id = "msg_5",
            threadId = "thread_factory",
            role = "assistant",
            messageType = "draft_summary",
            content = "当前方向可以先聚焦有多产线、多设备类型、停机损失明确的制造工厂。下一步建议补充行业细分和已有客户案例。",
        ),
    )

private fun sampleDraftReview(): SalesWorkspaceDraftReviewDto =
    SalesWorkspaceDraftReviewDto(
        id = "review_preview",
        workspaceId = "ws_demo",
        status = "previewed",
        baseWorkspaceVersion = 2,
        draft = SalesWorkspacePatchDraftDto(
            id = "draft_preview",
            workspaceId = "ws_demo",
            baseWorkspaceVersion = 2,
            operationCount = 2,
            rawJson = "{}",
        ),
        preview = SalesWorkspaceDraftReviewPreviewDto(
            materializedPatch = SalesWorkspacePatchSummaryDto(
                id = "patch_preview",
                workspaceId = "ws_demo",
                baseWorkspaceVersion = 2,
                operationCount = 2,
            ),
            previewWorkspaceVersion = 3,
            previewRankingBoard = null,
            wouldMutate = true,
        ),
        review = null,
        applyResult = null,
    )
