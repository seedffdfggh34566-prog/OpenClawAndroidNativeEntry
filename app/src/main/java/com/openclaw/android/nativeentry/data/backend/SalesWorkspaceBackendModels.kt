package com.openclaw.android.nativeentry.data.backend

const val SalesWorkspaceDemoWorkspaceId = "ws_demo"

data class SalesWorkspaceReadOnlySnapshot(
    val workspace: SalesWorkspaceDto,
    val rankingBoard: SalesWorkspaceRankingBoardDto?,
    val projection: SalesWorkspaceProjectionDto?,
    val contextPack: SalesWorkspaceContextPackDto?,
)

data class SalesWorkspacePatchDraftPreviewDto(
    val patchDraft: SalesWorkspacePatchDraftDto,
    val patch: SalesWorkspacePatchSummaryDto,
    val previewWorkspaceVersion: Int,
    val previewRankingBoard: SalesWorkspaceRankingBoardDto?,
    val wouldMutate: Boolean,
) {
    val previewTopCandidate: SalesWorkspaceRankingItemDto?
        get() = previewRankingBoard?.rankedItems?.firstOrNull()
}

data class SalesWorkspaceDraftReviewDto(
    val id: String,
    val workspaceId: String,
    val status: String,
    val baseWorkspaceVersion: Int,
    val draft: SalesWorkspacePatchDraftDto,
    val preview: SalesWorkspaceDraftReviewPreviewDto,
    val review: SalesWorkspaceDraftReviewDecisionDto?,
    val applyResult: SalesWorkspaceDraftReviewApplyResultDto?,
)

data class SalesWorkspaceDraftReviewPreviewDto(
    val materializedPatch: SalesWorkspacePatchSummaryDto,
    val previewWorkspaceVersion: Int,
    val previewRankingBoard: SalesWorkspaceRankingBoardDto?,
    val wouldMutate: Boolean,
) {
    val previewTopCandidate: SalesWorkspaceRankingItemDto?
        get() = previewRankingBoard?.rankedItems?.firstOrNull()
}

data class SalesWorkspaceDraftReviewDecisionDto(
    val decision: String,
    val reviewedBy: String,
    val comment: String,
    val client: String,
)

data class SalesWorkspaceDraftReviewApplyResultDto(
    val status: String,
    val materializedPatchId: String?,
    val workspaceVersion: Int?,
    val topCandidateId: String?,
    val topCandidateName: String?,
    val topCandidateRank: Int?,
    val errorCode: String?,
    val errorMessage: String?,
)

data class SalesWorkspaceDraftReviewApplyResponseDto(
    val draftReview: SalesWorkspaceDraftReviewDto,
    val patch: SalesWorkspacePatchSummaryDto,
    val workspace: SalesWorkspaceDto,
    val rankingBoard: SalesWorkspaceRankingBoardDto?,
) {
    val topCandidate: SalesWorkspaceRankingItemDto?
        get() = rankingBoard?.rankedItems?.firstOrNull()
}

data class SalesWorkspaceChatTurnResponseDto(
    val conversationMessage: SalesWorkspaceConversationMessageDto,
    val agentRun: SalesWorkspaceAgentRunDto,
    val assistantMessage: SalesWorkspaceConversationMessageDto,
    val draftReview: SalesWorkspaceDraftReviewDto?,
    val patchDraft: SalesWorkspacePatchDraftDto?,
)

data class SalesWorkspaceConversationMessageDto(
    val id: String,
    val role: String,
    val messageType: String,
    val content: String,
)

data class SalesWorkspaceConversationMessagesResponseDto(
    val messages: List<SalesWorkspaceConversationMessageDto>,
)

data class SalesWorkspaceAgentRunDto(
    val id: String,
    val status: String,
    val inputRefs: List<String>,
    val outputRefs: List<String>,
)

data class SalesWorkspacePatchDraftDto(
    val id: String,
    val workspaceId: String,
    val baseWorkspaceVersion: Int,
    val operationCount: Int,
    val rawJson: String,
)

data class SalesWorkspacePatchSummaryDto(
    val id: String,
    val workspaceId: String,
    val baseWorkspaceVersion: Int,
    val operationCount: Int,
)

data class SalesWorkspaceResponseDto(
    val workspace: SalesWorkspaceDto,
)

data class SalesWorkspaceDto(
    val id: String,
    val name: String,
    val goal: String,
    val status: String,
    val workspaceVersion: Int,
    val currentProductProfileRevisionId: String?,
    val currentLeadDirectionVersionId: String?,
    val productProfileRevisions: Map<String, SalesWorkspaceProductProfileDto>,
    val leadDirectionVersions: Map<String, SalesWorkspaceLeadDirectionDto>,
    val rankingBoard: SalesWorkspaceRankingBoardDto?,
) {
    val currentProductProfile: SalesWorkspaceProductProfileDto?
        get() = productProfileRevisions[currentProductProfileRevisionId]

    val currentLeadDirection: SalesWorkspaceLeadDirectionDto?
        get() = leadDirectionVersions[currentLeadDirectionVersionId]
}

data class SalesWorkspaceProductProfileDto(
    val id: String,
    val productName: String,
    val oneLiner: String,
    val targetCustomers: List<String>,
    val painPoints: List<String>,
    val valueProps: List<String>,
)

data class SalesWorkspaceLeadDirectionDto(
    val id: String,
    val priorityIndustries: List<String>,
    val targetCustomerTypes: List<String>,
    val regions: List<String>,
    val changeReason: String,
)

data class SalesWorkspaceRankingBoardResponseDto(
    val rankingBoard: SalesWorkspaceRankingBoardDto,
)

data class SalesWorkspaceRankingBoardDto(
    val id: String,
    val workspaceVersion: Int,
    val rankedItems: List<SalesWorkspaceRankingItemDto>,
    val deltas: List<SalesWorkspaceRankingDeltaDto>,
)

data class SalesWorkspaceRankingItemDto(
    val candidateId: String,
    val candidateName: String,
    val rank: Int,
    val score: Int,
    val status: String,
    val reason: String,
)

data class SalesWorkspaceRankingDeltaDto(
    val candidateId: String,
    val previousRank: Int?,
    val newRank: Int,
    val previousScore: Int,
    val newScore: Int,
    val reason: String,
)

data class SalesWorkspaceProjectionDto(
    val workspaceVersion: Int,
    val files: Map<String, String>,
)

data class SalesWorkspaceContextPackResponseDto(
    val contextPack: SalesWorkspaceContextPackDto,
)

data class SalesWorkspaceContextPackDto(
    val id: String,
    val productSummary: String,
    val currentDirection: String,
    val topCandidates: List<SalesWorkspaceContextCandidateDto>,
    val recentRankingDelta: List<String>,
    val kernelBoundary: String,
)

data class SalesWorkspaceContextCandidateDto(
    val candidateId: String,
    val name: String,
    val rank: Int,
    val score: Int,
    val reason: String,
)
