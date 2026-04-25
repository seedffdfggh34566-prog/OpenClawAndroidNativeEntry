package com.openclaw.android.nativeentry.ui.shell

import com.openclaw.android.nativeentry.data.backend.BackendReadError
import com.openclaw.android.nativeentry.data.backend.AnalysisRunDetailResponseDto
import com.openclaw.android.nativeentry.data.backend.HistoryResponseDto
import com.openclaw.android.nativeentry.data.backend.LeadAnalysisResultDetailDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileConfirmResponseDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileCreateResponseDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileDetailDto
import com.openclaw.android.nativeentry.data.backend.ProductProfileEnrichResponseDto
import com.openclaw.android.nativeentry.data.backend.ReportDetailDto
import com.openclaw.android.nativeentry.data.backend.V1BackendBaseUrl

data class V1BackendUiState(
    val history: V1SectionState<HistoryResponseDto> = V1SectionState.Loading,
    val productProfile: V1SectionState<ProductProfileDetailDto> = V1SectionState.Idle,
    val report: V1SectionState<ReportDetailDto> = V1SectionState.Idle,
    val analysisResult: V1SectionState<LeadAnalysisResultDetailDto> = V1SectionState.Idle,
    val productProfileCreate: V1SectionState<ProductProfileCreateResponseDto> = V1SectionState.Idle,
    val productProfileEnrich: V1SectionState<ProductProfileEnrichResponseDto> = V1SectionState.Idle,
    val productProfileConfirm: V1SectionState<ProductProfileConfirmResponseDto> = V1SectionState.Idle,
    val productLearningRun: V1SectionState<AnalysisRunDetailResponseDto> = V1SectionState.Idle,
    val analysisRun: V1SectionState<AnalysisRunDetailResponseDto> = V1SectionState.Idle,
    val reportRun: V1SectionState<AnalysisRunDetailResponseDto> = V1SectionState.Idle,
    val isDebugFallbackEnabled: Boolean = false,
    val backendBaseUrl: String = V1BackendBaseUrl,
)

sealed interface V1SectionState<out T> {
    data object Idle : V1SectionState<Nothing>
    data object Loading : V1SectionState<Nothing>
    data object Empty : V1SectionState<Nothing>
    data class Loaded<T>(val value: T) : V1SectionState<T>
    data class Failed(val error: BackendReadError) : V1SectionState<Nothing>
}
