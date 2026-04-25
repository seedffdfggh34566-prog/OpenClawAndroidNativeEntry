package com.openclaw.android.nativeentry.data.backend

const val V1BackendBaseUrl = "http://127.0.0.1:8013"

sealed interface BackendReadResult<out T> {
    data class Success<T>(val value: T) : BackendReadResult<T>
    data class Failure(val error: BackendReadError) : BackendReadResult<Nothing>
}

data class BackendReadError(
    val title: String,
    val detail: String,
)

data class ObjectRefDto(
    val objectType: String,
    val objectId: String,
    val version: Int?,
)

data class CurrentRunDto(
    val id: String,
    val runType: String,
    val status: String,
    val triggerSource: String,
    val startedAt: String?,
    val endedAt: String?,
    val errorMessage: String?,
)

data class ProductProfileSummaryDto(
    val id: String,
    val name: String,
    val oneLineDescription: String,
    val status: String,
    val learningStage: String,
    val version: Int,
    val updatedAt: String,
)

data class ProductProfileCreateRequestDto(
    val name: String,
    val oneLineDescription: String,
    val sourceNotes: String?,
)

data class ProductProfileCreateResponseDto(
    val productProfile: ProductProfileSummaryDto,
    val currentRun: AgentRunDto?,
    val links: Map<String, String>,
)

data class ProductProfileEnrichRequestDto(
    val supplementalNotes: String,
    val triggerSource: String,
)

data class ProductProfileEnrichResponseDto(
    val agentRun: AgentRunDto,
)

data class ProductProfileConfirmResponseDto(
    val productProfile: ProductProfileSummaryDto,
)

data class AnalysisRunCreateRequestDto(
    val runType: String,
    val productProfileId: String,
    val leadAnalysisResultId: String?,
    val triggerSource: String,
)

data class AgentRunDto(
    val id: String,
    val runType: String,
    val status: String,
    val triggeredBy: String,
    val triggerSource: String,
    val inputRefs: List<ObjectRefDto>,
    val outputRefs: List<ObjectRefDto>,
    val startedAt: String?,
    val endedAt: String?,
    val errorMessage: String?,
) {
    val isTerminal: Boolean
        get() = status == "succeeded" || status == "failed" || status == "cancelled"
}

data class AnalysisRunCreateResponseDto(
    val agentRun: AgentRunDto,
)

data class AnalysisRunDetailResponseDto(
    val agentRun: AgentRunDto,
    val resultSummary: Map<String, String>,
)

data class LatestAnalysisResultSummaryDto(
    val id: String,
    val status: String,
    val title: String,
    val updatedAt: String,
)

data class LeadAnalysisResultDetailDto(
    val id: String,
    val productProfileId: String,
    val createdByAgentRunId: String,
    val title: String,
    val analysisScope: String,
    val summary: String,
    val priorityIndustries: List<String>,
    val priorityCustomerTypes: List<String>,
    val scenarioOpportunities: List<String>,
    val rankingExplanations: List<String>,
    val recommendations: List<String>,
    val risks: List<String>,
    val limitations: List<String>,
    val status: String,
    val version: Int,
    val createdAt: String,
    val updatedAt: String,
)

data class LatestReportSummaryDto(
    val id: String,
    val status: String,
    val title: String,
    val updatedAt: String,
)

data class RecentHistoryItemDto(
    val objectType: String,
    val id: String,
    val title: String,
    val status: String,
    val updatedAt: String,
)

data class HistoryResponseDto(
    val currentRun: CurrentRunDto?,
    val latestProductProfile: ProductProfileSummaryDto?,
    val latestAnalysisResult: LatestAnalysisResultSummaryDto?,
    val latestReport: LatestReportSummaryDto?,
    val recentItems: List<RecentHistoryItemDto>,
) {
    val isEmpty: Boolean
        get() = currentRun == null &&
            latestProductProfile == null &&
            latestAnalysisResult == null &&
            latestReport == null &&
            recentItems.isEmpty()
}

data class ProductProfileDetailDto(
    val id: String,
    val name: String,
    val oneLineDescription: String,
    val status: String,
    val learningStage: String,
    val version: Int,
    val targetCustomers: List<String>,
    val targetIndustries: List<String>,
    val typicalUseCases: List<String>,
    val painPointsSolved: List<String>,
    val coreAdvantages: List<String>,
    val deliveryModel: String,
    val constraints: List<String>,
    val missingFields: List<String>,
    val createdAt: String,
    val updatedAt: String,
)

data class ReportSectionDto(
    val title: String,
    val body: String,
)

data class ReportDetailDto(
    val id: String,
    val productProfileId: String,
    val leadAnalysisResultId: String,
    val status: String,
    val title: String,
    val summary: String,
    val sections: List<ReportSectionDto>,
    val version: Int,
    val updatedAt: String,
)
