package com.openclaw.android.nativeentry.data.backend

const val SalesWorkspaceDemoWorkspaceId = "ws_demo"

data class SalesWorkspaceReadOnlySnapshot(
    val workspace: SalesWorkspaceDto,
    val rankingBoard: SalesWorkspaceRankingBoardDto?,
    val projection: SalesWorkspaceProjectionDto?,
    val contextPack: SalesWorkspaceContextPackDto?,
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
