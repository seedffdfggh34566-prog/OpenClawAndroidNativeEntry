package com.openclaw.android.nativeentry.data.backend

import org.json.JSONArray
import org.json.JSONObject

fun parseHistoryResponse(rawJson: String): HistoryResponseDto {
    val json = JSONObject(rawJson)
    return HistoryResponseDto(
        currentRun = json.optJSONObject("current_run")?.toCurrentRunDto(),
        latestProductProfile = json.optJSONObject("latest_product_profile")?.toProductProfileSummaryDto(),
        latestAnalysisResult = json.optJSONObject("latest_analysis_result")?.toLatestAnalysisResultSummaryDto(),
        latestReport = json.optJSONObject("latest_report")?.toLatestReportSummaryDto(),
        recentItems = json.optJSONArray("recent_items").toHistoryItemList(),
    )
}

fun parseProductProfileDetail(rawJson: String): ProductProfileDetailDto {
    val profile = JSONObject(rawJson).getJSONObject("product_profile")
    return ProductProfileDetailDto(
        id = profile.getString("id"),
        name = profile.getString("name"),
        oneLineDescription = profile.getString("one_line_description"),
        status = profile.getString("status"),
        learningStage = profile.getString("learning_stage"),
        version = profile.getInt("version"),
        targetCustomers = profile.optJSONArray("target_customers").toStringList(),
        targetIndustries = profile.optJSONArray("target_industries").toStringList(),
        typicalUseCases = profile.optJSONArray("typical_use_cases").toStringList(),
        painPointsSolved = profile.optJSONArray("pain_points_solved").toStringList(),
        coreAdvantages = profile.optJSONArray("core_advantages").toStringList(),
        deliveryModel = profile.optString("delivery_model"),
        constraints = profile.optJSONArray("constraints").toStringList(),
        missingFields = profile.optJSONArray("missing_fields").toStringList(),
        createdAt = profile.getString("created_at"),
        updatedAt = profile.getString("updated_at"),
    )
}

fun parseProductProfileCreateResponse(rawJson: String): ProductProfileCreateResponseDto {
    val json = JSONObject(rawJson)
    return ProductProfileCreateResponseDto(
        productProfile = json.getJSONObject("product_profile").toProductProfileSummaryDto(),
        currentRun = json.optJSONObject("current_run")?.toAgentRunDto(),
        links = json.optJSONObject("links").toStringMap(),
    )
}

fun parseProductProfileEnrichResponse(rawJson: String): ProductProfileEnrichResponseDto {
    val json = JSONObject(rawJson)
    return ProductProfileEnrichResponseDto(
        agentRun = json.getJSONObject("agent_run").toAgentRunDto(),
    )
}

fun parseProductProfileConfirmResponse(rawJson: String): ProductProfileConfirmResponseDto {
    val json = JSONObject(rawJson)
    return ProductProfileConfirmResponseDto(
        productProfile = json.getJSONObject("product_profile").toProductProfileSummaryDto(),
    )
}

fun ProductProfileCreateRequestDto.toJsonBody(): String {
    val json = JSONObject()
        .put("name", name)
        .put("one_line_description", oneLineDescription)

    if (sourceNotes.isNullOrBlank()) {
        json.put("source_notes", JSONObject.NULL)
    } else {
        json.put("source_notes", sourceNotes)
    }

    return json.toString()
}

fun ProductProfileEnrichRequestDto.toJsonBody(): String =
    JSONObject()
        .put("supplemental_notes", supplementalNotes)
        .put("trigger_source", triggerSource)
        .toString()

fun parseAnalysisRunCreateResponse(rawJson: String): AnalysisRunCreateResponseDto {
    val json = JSONObject(rawJson)
    return AnalysisRunCreateResponseDto(
        agentRun = json.getJSONObject("agent_run").toAgentRunDto(),
    )
}

fun parseAnalysisRunDetailResponse(rawJson: String): AnalysisRunDetailResponseDto {
    val json = JSONObject(rawJson)
    return AnalysisRunDetailResponseDto(
        agentRun = json.getJSONObject("agent_run").toAgentRunDto(),
        resultSummary = json.optJSONObject("result_summary").toStringMap(),
    )
}

fun AnalysisRunCreateRequestDto.toJsonBody(): String {
    val json = JSONObject()
        .put("run_type", runType)
        .put("product_profile_id", productProfileId)
        .put("trigger_source", triggerSource)

    if (leadAnalysisResultId.isNullOrBlank()) {
        json.put("lead_analysis_result_id", JSONObject.NULL)
    } else {
        json.put("lead_analysis_result_id", leadAnalysisResultId)
    }

    return json.toString()
}

fun parseReportDetail(rawJson: String): ReportDetailDto {
    val report = JSONObject(rawJson).getJSONObject("report")
    return ReportDetailDto(
        id = report.getString("id"),
        productProfileId = report.getString("product_profile_id"),
        leadAnalysisResultId = report.getString("lead_analysis_result_id"),
        status = report.getString("status"),
        title = report.getString("title"),
        summary = report.getString("summary"),
        sections = report.optJSONArray("sections").toReportSections(),
        version = report.getInt("version"),
        updatedAt = report.getString("updated_at"),
    )
}

fun parseLeadAnalysisResultDetail(rawJson: String): LeadAnalysisResultDetailDto {
    val result = JSONObject(rawJson).getJSONObject("lead_analysis_result")
    return LeadAnalysisResultDetailDto(
        id = result.getString("id"),
        productProfileId = result.getString("product_profile_id"),
        createdByAgentRunId = result.getString("created_by_agent_run_id"),
        title = result.getString("title"),
        analysisScope = result.getString("analysis_scope"),
        summary = result.getString("summary"),
        priorityIndustries = result.optJSONArray("priority_industries").toStringList(),
        priorityCustomerTypes = result.optJSONArray("priority_customer_types").toStringList(),
        scenarioOpportunities = result.optJSONArray("scenario_opportunities").toStringList(),
        rankingExplanations = result.optJSONArray("ranking_explanations").toStringList(),
        recommendations = result.optJSONArray("recommendations").toStringList(),
        risks = result.optJSONArray("risks").toStringList(),
        limitations = result.optJSONArray("limitations").toStringList(),
        status = result.getString("status"),
        version = result.getInt("version"),
        createdAt = result.getString("created_at"),
        updatedAt = result.getString("updated_at"),
    )
}

private fun JSONObject.toCurrentRunDto(): CurrentRunDto =
    CurrentRunDto(
        id = getString("id"),
        runType = getString("run_type"),
        status = getString("status"),
        triggerSource = getString("trigger_source"),
        startedAt = optNullableString("started_at"),
        endedAt = optNullableString("ended_at"),
        errorMessage = optNullableString("error_message"),
    )

private fun JSONObject.toAgentRunDto(): AgentRunDto =
    AgentRunDto(
        id = getString("id"),
        runType = getString("run_type"),
        status = getString("status"),
        triggeredBy = getString("triggered_by"),
        triggerSource = getString("trigger_source"),
        inputRefs = optJSONArray("input_refs").toObjectRefList(),
        outputRefs = optJSONArray("output_refs").toObjectRefList(),
        startedAt = optNullableString("started_at"),
        endedAt = optNullableString("ended_at"),
        errorMessage = optNullableString("error_message"),
    )

private fun JSONObject.toObjectRefDto(): ObjectRefDto =
    ObjectRefDto(
        objectType = getString("object_type"),
        objectId = getString("object_id"),
        version = if (isNull("version")) null else optInt("version"),
    )

private fun JSONObject.toProductProfileSummaryDto(): ProductProfileSummaryDto =
    ProductProfileSummaryDto(
        id = getString("id"),
        name = getString("name"),
        oneLineDescription = getString("one_line_description"),
        status = getString("status"),
        learningStage = getString("learning_stage"),
        version = getInt("version"),
        updatedAt = getString("updated_at"),
    )

private fun JSONObject.toLatestAnalysisResultSummaryDto(): LatestAnalysisResultSummaryDto =
    LatestAnalysisResultSummaryDto(
        id = getString("id"),
        status = getString("status"),
        title = getString("title"),
        updatedAt = getString("updated_at"),
    )

private fun JSONObject.toLatestReportSummaryDto(): LatestReportSummaryDto =
    LatestReportSummaryDto(
        id = getString("id"),
        status = getString("status"),
        title = getString("title"),
        updatedAt = getString("updated_at"),
    )

private fun JSONObject.toRecentHistoryItemDto(): RecentHistoryItemDto =
    RecentHistoryItemDto(
        objectType = getString("object_type"),
        id = getString("id"),
        title = getString("title"),
        status = getString("status"),
        updatedAt = getString("updated_at"),
    )

private fun JSONArray?.toHistoryItemList(): List<RecentHistoryItemDto> =
    buildList {
        val array = this@toHistoryItemList ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toRecentHistoryItemDto())
        }
    }

private fun JSONArray?.toObjectRefList(): List<ObjectRefDto> =
    buildList {
        val array = this@toObjectRefList ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toObjectRefDto())
        }
    }

private fun JSONArray?.toStringList(): List<String> =
    buildList {
        val array = this@toStringList ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getString(index))
        }
    }

private fun JSONArray?.toReportSections(): List<ReportSectionDto> =
    buildList {
        val array = this@toReportSections ?: return@buildList
        for (index in 0 until array.length()) {
            val section = array.getJSONObject(index)
            add(
                ReportSectionDto(
                    title = section.getString("title"),
                    body = section.getString("body"),
                ),
            )
        }
    }

private fun JSONObject.optNullableString(name: String): String? =
    if (isNull(name)) null else optString(name)

private fun JSONObject?.toStringMap(): Map<String, String> =
    buildMap {
        val json = this@toStringMap ?: return@buildMap
        val keys = json.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            put(key, json.optString(key))
        }
    }
