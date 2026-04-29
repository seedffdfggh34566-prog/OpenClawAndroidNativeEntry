package com.openclaw.android.nativeentry.data.backend

import org.json.JSONArray
import org.json.JSONObject

fun parseSalesWorkspaceResponse(rawJson: String): SalesWorkspaceResponseDto {
    val workspace = JSONObject(rawJson).getJSONObject("workspace")
    return SalesWorkspaceResponseDto(workspace = workspace.toSalesWorkspaceDto())
}

fun parseSalesWorkspaceRankingBoardResponse(rawJson: String): SalesWorkspaceRankingBoardResponseDto {
    val rankingBoard = JSONObject(rawJson).getJSONObject("ranking_board")
    return SalesWorkspaceRankingBoardResponseDto(rankingBoard = rankingBoard.toSalesWorkspaceRankingBoardDto())
}

fun parseSalesWorkspaceProjectionResponse(rawJson: String): SalesWorkspaceProjectionDto {
    val json = JSONObject(rawJson)
    return SalesWorkspaceProjectionDto(
        workspaceVersion = json.getInt("workspace_version"),
        files = json.getJSONObject("files").toStringMap(),
    )
}

fun parseSalesWorkspaceContextPackResponse(rawJson: String): SalesWorkspaceContextPackResponseDto {
    val contextPack = JSONObject(rawJson).getJSONObject("context_pack")
    return SalesWorkspaceContextPackResponseDto(contextPack = contextPack.toSalesWorkspaceContextPackDto())
}

fun parseSalesWorkspacePatchDraftPreviewResponse(rawJson: String): SalesWorkspacePatchDraftPreviewDto {
    val json = JSONObject(rawJson)
    return SalesWorkspacePatchDraftPreviewDto(
        patchDraft = json.getJSONObject("patch_draft").toSalesWorkspacePatchDraftDto(),
        patch = json.getJSONObject("patch").toSalesWorkspacePatchSummaryDto(),
        previewWorkspaceVersion = json.getInt("preview_workspace_version"),
        previewRankingBoard = json.optJSONObject("preview_ranking_board")?.toSalesWorkspaceRankingBoardDto(),
        wouldMutate = json.optBoolean("would_mutate"),
    )
}

fun parseSalesWorkspaceDraftReviewResponse(rawJson: String): SalesWorkspaceDraftReviewDto =
    JSONObject(rawJson).getJSONObject("draft_review").toSalesWorkspaceDraftReviewDto()

fun parseSalesWorkspaceDraftReviewApplyResponse(rawJson: String): SalesWorkspaceDraftReviewApplyResponseDto {
    val json = JSONObject(rawJson)
    return SalesWorkspaceDraftReviewApplyResponseDto(
        draftReview = json.getJSONObject("draft_review").toSalesWorkspaceDraftReviewDto(),
        patch = json.getJSONObject("patch").toSalesWorkspacePatchSummaryDto(),
        workspace = json.getJSONObject("workspace").toSalesWorkspaceDto(),
        rankingBoard = json.optJSONObject("ranking_board")?.toSalesWorkspaceRankingBoardDto(),
    )
}

fun parseSalesWorkspaceChatTurnResponse(rawJson: String): SalesWorkspaceChatTurnResponseDto {
    val json = JSONObject(rawJson)
    return SalesWorkspaceChatTurnResponseDto(
        conversationMessage = json.getJSONObject("conversation_message").toSalesWorkspaceConversationMessageDto(),
        agentRun = json.getJSONObject("agent_run").toSalesWorkspaceAgentRunDto(),
        assistantMessage = json.getJSONObject("assistant_message").toSalesWorkspaceConversationMessageDto(),
        draftReview = json.optJSONObject("draft_review")?.toSalesWorkspaceDraftReviewDto(),
        patchDraft = json.optJSONObject("patch_draft")?.toSalesWorkspacePatchDraftDto(),
    )
}

fun parseSalesWorkspaceConversationMessagesResponse(rawJson: String): SalesWorkspaceConversationMessagesResponseDto =
    SalesWorkspaceConversationMessagesResponseDto(
        messages = JSONObject(rawJson).optJSONArray("messages").toConversationMessages(),
    )

fun parseSalesWorkspaceConversationThreadsResponse(rawJson: String): SalesWorkspaceConversationThreadsResponseDto =
    SalesWorkspaceConversationThreadsResponseDto(
        threads = JSONObject(rawJson).optJSONArray("threads").toConversationThreads(),
    )

fun parseSalesWorkspaceConversationThreadResponse(rawJson: String): SalesWorkspaceConversationThreadDto =
    JSONObject(rawJson).getJSONObject("thread").toSalesWorkspaceConversationThreadDto()

private fun JSONObject.toSalesWorkspaceConversationMessageDto(): SalesWorkspaceConversationMessageDto =
    SalesWorkspaceConversationMessageDto(
        id = getString("id"),
        threadId = optString("thread_id", SalesWorkspaceDefaultThreadId),
        role = getString("role"),
        messageType = getString("message_type"),
        content = getString("content"),
    )

private fun JSONObject.toSalesWorkspaceConversationThreadDto(): SalesWorkspaceConversationThreadDto =
    SalesWorkspaceConversationThreadDto(
        id = getString("id"),
        title = getString("title"),
        status = getString("status"),
    )

private fun JSONArray?.toConversationMessages(): List<SalesWorkspaceConversationMessageDto> =
    buildList {
        val array = this@toConversationMessages ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toSalesWorkspaceConversationMessageDto())
        }
    }

private fun JSONArray?.toConversationThreads(): List<SalesWorkspaceConversationThreadDto> =
    buildList {
        val array = this@toConversationThreads ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toSalesWorkspaceConversationThreadDto())
        }
    }

private fun JSONObject.toSalesWorkspaceAgentRunDto(): SalesWorkspaceAgentRunDto =
    SalesWorkspaceAgentRunDto(
        id = getString("id"),
        status = getString("status"),
        inputRefs = optJSONArray("input_refs").toStringList(),
        outputRefs = optJSONArray("output_refs").toStringList(),
    )

private fun JSONObject.toSalesWorkspaceDraftReviewDto(): SalesWorkspaceDraftReviewDto =
    SalesWorkspaceDraftReviewDto(
        id = getString("id"),
        workspaceId = getString("workspace_id"),
        status = getString("status"),
        baseWorkspaceVersion = getInt("base_workspace_version"),
        draft = getJSONObject("draft").toSalesWorkspacePatchDraftDto(),
        preview = getJSONObject("preview").toSalesWorkspaceDraftReviewPreviewDto(),
        review = optJSONObject("review")?.toSalesWorkspaceDraftReviewDecisionDto(),
        applyResult = optJSONObject("apply_result")?.toSalesWorkspaceDraftReviewApplyResultDto(),
    )

private fun JSONObject.toSalesWorkspaceDraftReviewPreviewDto(): SalesWorkspaceDraftReviewPreviewDto =
    SalesWorkspaceDraftReviewPreviewDto(
        materializedPatch = getJSONObject("materialized_patch").toSalesWorkspacePatchSummaryDto(),
        previewWorkspaceVersion = getInt("preview_workspace_version"),
        previewRankingBoard = optJSONObject("preview_ranking_board")?.toSalesWorkspaceRankingBoardDto(),
        wouldMutate = optBoolean("would_mutate"),
    )

private fun JSONObject.toSalesWorkspaceDraftReviewDecisionDto(): SalesWorkspaceDraftReviewDecisionDto =
    SalesWorkspaceDraftReviewDecisionDto(
        decision = getString("decision"),
        reviewedBy = optString("reviewed_by"),
        comment = optString("comment"),
        client = optString("client"),
    )

private fun JSONObject.toSalesWorkspaceDraftReviewApplyResultDto(): SalesWorkspaceDraftReviewApplyResultDto {
    val rankingImpact = optJSONObject("ranking_impact_summary")
    return SalesWorkspaceDraftReviewApplyResultDto(
        status = getString("status"),
        materializedPatchId = optNullableString("materialized_patch_id"),
        workspaceVersion = if (isNull("workspace_version")) null else optInt("workspace_version"),
        topCandidateId = rankingImpact?.optNullableString("top_candidate_id"),
        topCandidateName = rankingImpact?.optNullableString("top_candidate_name"),
        topCandidateRank = if (rankingImpact == null || rankingImpact.isNull("top_candidate_rank")) {
            null
        } else {
            rankingImpact.optInt("top_candidate_rank")
        },
        errorCode = optNullableString("error_code"),
        errorMessage = optNullableString("error_message"),
    )
}

private fun JSONObject.toSalesWorkspacePatchDraftDto(): SalesWorkspacePatchDraftDto =
    SalesWorkspacePatchDraftDto(
        id = getString("id"),
        workspaceId = getString("workspace_id"),
        baseWorkspaceVersion = getInt("base_workspace_version"),
        operationCount = optJSONArray("operations")?.length() ?: 0,
        rawJson = toString(),
    )

private fun JSONObject.toSalesWorkspacePatchSummaryDto(): SalesWorkspacePatchSummaryDto =
    SalesWorkspacePatchSummaryDto(
        id = getString("id"),
        workspaceId = getString("workspace_id"),
        baseWorkspaceVersion = getInt("base_workspace_version"),
        operationCount = optJSONArray("operations")?.length() ?: 0,
    )

private fun JSONObject.toSalesWorkspaceDto(): SalesWorkspaceDto =
    SalesWorkspaceDto(
        id = getString("id"),
        name = getString("name"),
        goal = optString("goal"),
        status = getString("status"),
        workspaceVersion = getInt("workspace_version"),
        currentProductProfileRevisionId = optNullableString("current_product_profile_revision_id"),
        currentLeadDirectionVersionId = optNullableString("current_lead_direction_version_id"),
        productProfileRevisions = optJSONObject("product_profile_revisions").toObjectMap {
            it.toSalesWorkspaceProductProfileDto()
        },
        leadDirectionVersions = optJSONObject("lead_direction_versions").toObjectMap {
            it.toSalesWorkspaceLeadDirectionDto()
        },
        rankingBoard = optJSONObject("ranking_board")?.toSalesWorkspaceRankingBoardDto(),
    )

private fun JSONObject.toSalesWorkspaceProductProfileDto(): SalesWorkspaceProductProfileDto =
    SalesWorkspaceProductProfileDto(
        id = getString("id"),
        productName = getString("product_name"),
        oneLiner = optString("one_liner"),
        targetCustomers = optJSONArray("target_customers").toStringList(),
        painPoints = optJSONArray("pain_points").toStringList(),
        valueProps = optJSONArray("value_props").toStringList(),
    )

private fun JSONObject.toSalesWorkspaceLeadDirectionDto(): SalesWorkspaceLeadDirectionDto =
    SalesWorkspaceLeadDirectionDto(
        id = getString("id"),
        priorityIndustries = optJSONArray("priority_industries").toStringList(),
        targetCustomerTypes = optJSONArray("target_customer_types").toStringList(),
        regions = optJSONArray("regions").toStringList(),
        changeReason = optString("change_reason"),
    )

private fun JSONObject.toSalesWorkspaceRankingBoardDto(): SalesWorkspaceRankingBoardDto =
    SalesWorkspaceRankingBoardDto(
        id = getString("id"),
        workspaceVersion = getInt("workspace_version"),
        rankedItems = optJSONArray("ranked_items").toRankingItems(),
        deltas = optJSONArray("deltas").toRankingDeltas(),
    )

private fun JSONObject.toSalesWorkspaceRankingItemDto(): SalesWorkspaceRankingItemDto =
    SalesWorkspaceRankingItemDto(
        candidateId = getString("candidate_id"),
        candidateName = getString("candidate_name"),
        rank = getInt("rank"),
        score = getInt("score"),
        status = getString("status"),
        reason = optString("reason"),
    )

private fun JSONObject.toSalesWorkspaceRankingDeltaDto(): SalesWorkspaceRankingDeltaDto =
    SalesWorkspaceRankingDeltaDto(
        candidateId = getString("candidate_id"),
        previousRank = if (isNull("previous_rank")) null else optInt("previous_rank"),
        newRank = getInt("new_rank"),
        previousScore = getInt("previous_score"),
        newScore = getInt("new_score"),
        reason = optString("reason"),
    )

private fun JSONObject.toSalesWorkspaceContextPackDto(): SalesWorkspaceContextPackDto =
    SalesWorkspaceContextPackDto(
        id = getString("id"),
        productSummary = optString("product_summary"),
        currentDirection = optString("current_direction"),
        topCandidates = optJSONArray("top_candidates").toContextCandidates(),
        recentRankingDelta = optJSONArray("recent_ranking_delta").toStringList(),
        kernelBoundary = optString("kernel_boundary"),
    )

private fun JSONObject.toSalesWorkspaceContextCandidateDto(): SalesWorkspaceContextCandidateDto =
    SalesWorkspaceContextCandidateDto(
        candidateId = getString("candidate_id"),
        name = getString("name"),
        rank = getInt("rank"),
        score = getInt("score"),
        reason = optString("reason"),
    )

private fun JSONArray?.toRankingItems(): List<SalesWorkspaceRankingItemDto> =
    buildList {
        val array = this@toRankingItems ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toSalesWorkspaceRankingItemDto())
        }
    }

private fun JSONArray?.toRankingDeltas(): List<SalesWorkspaceRankingDeltaDto> =
    buildList {
        val array = this@toRankingDeltas ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toSalesWorkspaceRankingDeltaDto())
        }
    }

private fun JSONArray?.toContextCandidates(): List<SalesWorkspaceContextCandidateDto> =
    buildList {
        val array = this@toContextCandidates ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getJSONObject(index).toSalesWorkspaceContextCandidateDto())
        }
    }

private fun JSONArray?.toStringList(): List<String> =
    buildList {
        val array = this@toStringList ?: return@buildList
        for (index in 0 until array.length()) {
            add(array.getString(index))
        }
    }

private fun JSONObject?.toStringMap(): Map<String, String> =
    buildMap {
        val json = this@toStringMap ?: return@buildMap
        val keys = json.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            put(key, json.optString(key))
        }
    }

private fun <T> JSONObject?.toObjectMap(mapper: (JSONObject) -> T): Map<String, T> =
    buildMap {
        val json = this@toObjectMap ?: return@buildMap
        val keys = json.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            put(key, mapper(json.getJSONObject(key)))
        }
    }

private fun JSONObject.optNullableString(name: String): String? =
    if (isNull(name)) null else optString(name)
