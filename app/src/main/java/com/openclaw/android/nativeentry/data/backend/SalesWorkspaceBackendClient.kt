package com.openclaw.android.nativeentry.data.backend

import java.io.BufferedReader
import java.io.InputStream
import java.io.InputStreamReader
import java.net.ConnectException
import java.net.HttpURLConnection
import java.net.NoRouteToHostException
import java.net.SocketTimeoutException
import java.net.URL
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONException
import org.json.JSONObject

class SalesWorkspaceBackendClient(
    private val baseUrl: String = V1BackendBaseUrl,
) {
    suspend fun getReadOnlySnapshot(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
    ): BackendReadResult<SalesWorkspaceReadOnlySnapshot> = withContext(Dispatchers.IO) {
        val workspace = when (val result = getWorkspace(workspaceId)) {
            is BackendReadResult.Failure -> return@withContext result
            is BackendReadResult.Success -> result.value.workspace
        }
        val rankingBoard = when (val result = getRankingBoard(workspaceId)) {
            is BackendReadResult.Failure -> {
                if (result.error.isMissingCandidateRankingBoard()) {
                    null
                } else {
                    return@withContext result
                }
            }
            is BackendReadResult.Success -> result.value.rankingBoard
        }
        val projection = when (val result = getProjection(workspaceId)) {
            is BackendReadResult.Failure -> return@withContext result
            is BackendReadResult.Success -> result.value
        }
        val contextPack = when (val result = createContextPack(workspaceId)) {
            is BackendReadResult.Failure -> return@withContext result
            is BackendReadResult.Success -> result.value.contextPack
        }
        BackendReadResult.Success(
            SalesWorkspaceReadOnlySnapshot(
                workspace = workspace,
                rankingBoard = rankingBoard,
                projection = projection,
                contextPack = contextPack,
            ),
        )
    }

    suspend fun previewRuntimePatchDraft(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
        baseWorkspaceVersion: Int,
        instruction: String = "add one deterministic runtime candidate",
    ): BackendReadResult<SalesWorkspacePatchDraftPreviewDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/runtime/patch-drafts/prototype/preview",
            body = JSONObject()
                .put("base_workspace_version", baseWorkspaceVersion)
                .put("instruction", instruction)
                .toString(),
            parser = ::parseSalesWorkspacePatchDraftPreviewResponse,
        )

    suspend fun createDraftReviewFromRuntimePreview(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
        baseWorkspaceVersion: Int,
        instruction: String = "add one deterministic runtime candidate",
    ): BackendReadResult<SalesWorkspaceDraftReviewDto> = withContext(Dispatchers.IO) {
        val preview = when (
            val result = previewRuntimePatchDraft(
                workspaceId = workspaceId,
                baseWorkspaceVersion = baseWorkspaceVersion,
                instruction = instruction,
            )
        ) {
            is BackendReadResult.Failure -> return@withContext result
            is BackendReadResult.Success -> result.value
        }
        createDraftReview(workspaceId = workspaceId, patchDraft = preview.patchDraft)
    }

    suspend fun reviewDraftReview(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
        draftReviewId: String,
        decision: String,
    ): BackendReadResult<SalesWorkspaceDraftReviewDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/draft-reviews/${draftReviewId.encodePathSegment()}/review",
            body = JSONObject()
                .put("decision", decision)
                .put("reviewed_by", "android_demo_user")
                .put("client", "android")
                .toString(),
            parser = ::parseSalesWorkspaceDraftReviewResponse,
        )

    suspend fun rejectDraftReview(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
        draftReviewId: String,
    ): BackendReadResult<SalesWorkspaceDraftReviewDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/draft-reviews/${draftReviewId.encodePathSegment()}/reject",
            body = JSONObject()
                .put("rejected_by", "android_demo_user")
                .put("reason", "Rejected from Android prototype review UI.")
                .toString(),
            parser = ::parseSalesWorkspaceDraftReviewResponse,
        )

    suspend fun applyDraftReview(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
        draftReviewId: String,
    ): BackendReadResult<SalesWorkspaceDraftReviewApplyResponseDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/draft-reviews/${draftReviewId.encodePathSegment()}/apply",
            body = JSONObject()
                .put("requested_by", "android_demo_user")
                .toString(),
            parser = ::parseSalesWorkspaceDraftReviewApplyResponse,
        )

    suspend fun runChatFirstSalesAgentTurn(
        workspaceId: String = SalesWorkspaceDemoWorkspaceId,
        baseWorkspaceVersion: Int,
        messageType: String,
        content: String,
    ): BackendReadResult<SalesWorkspaceChatTurnResponseDto> = withContext(Dispatchers.IO) {
        val message = when (
            val result = createConversationMessage(
                workspaceId = workspaceId,
                messageType = messageType,
                content = content,
            )
        ) {
            is BackendReadResult.Failure -> return@withContext result
            is BackendReadResult.Success -> result.value
        }
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/agent-runs/sales-agent-turns",
            body = JSONObject()
                .put("message_id", message.id)
                .put("base_workspace_version", baseWorkspaceVersion)
                .put("instruction", "handle Android chat-first workspace input")
                .toString(),
            parser = ::parseSalesWorkspaceChatTurnResponse,
        )
    }

    private suspend fun createConversationMessage(
        workspaceId: String,
        messageType: String,
        content: String,
    ): BackendReadResult<SalesWorkspaceConversationMessageDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/messages",
            body = JSONObject()
                .put("message_type", messageType)
                .put("content", content)
                .toString(),
            parser = { rawJson ->
                JSONObject(rawJson)
                    .getJSONObject("message")
                    .let { messageJson ->
                        SalesWorkspaceConversationMessageDto(
                            id = messageJson.getString("id"),
                            role = messageJson.getString("role"),
                            messageType = messageJson.getString("message_type"),
                            content = messageJson.getString("content"),
                        )
                    }
            },
        )

    private suspend fun createDraftReview(
        workspaceId: String,
        patchDraft: SalesWorkspacePatchDraftDto,
    ): BackendReadResult<SalesWorkspaceDraftReviewDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/draft-reviews",
            body = JSONObject()
                .put("patch_draft", JSONObject(patchDraft.rawJson))
                .toString(),
            parser = ::parseSalesWorkspaceDraftReviewResponse,
        )

    private suspend fun getWorkspace(workspaceId: String): BackendReadResult<SalesWorkspaceResponseDto> =
        requestJson(
            method = "GET",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}",
            parser = ::parseSalesWorkspaceResponse,
        )

    private suspend fun getRankingBoard(workspaceId: String): BackendReadResult<SalesWorkspaceRankingBoardResponseDto> =
        requestJson(
            method = "GET",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/ranking-board/current",
            parser = ::parseSalesWorkspaceRankingBoardResponse,
        )

    private suspend fun getProjection(workspaceId: String): BackendReadResult<SalesWorkspaceProjectionDto> =
        requestJson(
            method = "GET",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/projection",
            parser = ::parseSalesWorkspaceProjectionResponse,
        )

    private suspend fun createContextPack(workspaceId: String): BackendReadResult<SalesWorkspaceContextPackResponseDto> =
        requestJson(
            method = "POST",
            path = "/sales-workspaces/${workspaceId.encodePathSegment()}/context-packs",
            body = JSONObject()
                .put("task_type", "research_round")
                .put("token_budget_chars", 6000)
                .put("top_n_candidates", 5)
                .toString(),
            parser = ::parseSalesWorkspaceContextPackResponse,
        )

    private suspend fun <T> requestJson(
        method: String,
        path: String,
        body: String? = null,
        parser: (String) -> T,
    ): BackendReadResult<T> = withContext(Dispatchers.IO) {
        val connection = try {
            (URL(baseUrl.trimEnd('/') + path).openConnection() as HttpURLConnection).apply {
                requestMethod = method
                connectTimeout = 3_000
                readTimeout = 5_000
                instanceFollowRedirects = false
                useCaches = false
                setRequestProperty("Accept", "application/json")
                setRequestProperty("Cache-Control", "no-cache")
                setRequestProperty("Pragma", "no-cache")
                setRequestProperty("Connection", "close")
                if (body != null) {
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=utf-8")
                }
            }
        } catch (error: Exception) {
            return@withContext error.toSalesWorkspaceReadFailure()
        }

        try {
            if (body != null) {
                connection.outputStream.use { stream ->
                    stream.write(body.toByteArray(StandardCharsets.UTF_8))
                }
            }
            val statusCode = connection.responseCode
            val responseBody = connection.bodyFor(statusCode)
            if (statusCode !in 200..299) {
                return@withContext BackendReadResult.Failure(
                    BackendReadError(
                        title = "Sales Workspace API 返回 HTTP $statusCode",
                        detail = responseBody.ifBlank { "请求 $path 未成功。" },
                    ),
                )
            }

            BackendReadResult.Success(parser(responseBody))
        } catch (error: JSONException) {
            BackendReadResult.Failure(
                BackendReadError(
                    title = "Sales Workspace 响应解析失败",
                    detail = error.message ?: error.javaClass.simpleName,
                ),
            )
        } catch (error: Exception) {
            error.toSalesWorkspaceReadFailure()
        } finally {
            connection.disconnect()
        }
    }
}

private fun HttpURLConnection.bodyFor(statusCode: Int): String {
    val stream = if (statusCode in 200..299) inputStream else errorStream ?: inputStream
    return stream.readUtf8()
}

private fun InputStream.readUtf8(): String =
    BufferedReader(InputStreamReader(this, StandardCharsets.UTF_8)).use { it.readText() }

private fun String.encodePathSegment(): String =
    URLEncoder.encode(this, StandardCharsets.UTF_8.name())

private fun Exception.toSalesWorkspaceReadFailure(): BackendReadResult.Failure =
    BackendReadResult.Failure(
        BackendReadError(
            title = when (this) {
                is ConnectException,
                is NoRouteToHostException,
                is SocketTimeoutException -> "无法连接 Sales Workspace 后端"
                else -> "Sales Workspace 后端请求失败"
            },
            detail = when (this) {
                is ConnectException,
                is NoRouteToHostException,
                is SocketTimeoutException -> "请确认后端已在 127.0.0.1:8013 启动，已执行 adb reverse tcp:8013 tcp:8013，并已创建 ws_demo workspace。候选排序 demo 才需要额外 seed 数据。"
                else -> message ?: javaClass.simpleName
            },
        ),
    )

private fun BackendReadError.isMissingCandidateRankingBoard(): Boolean =
    title.contains("HTTP 404") && detail.contains("candidate_ranking_board")
