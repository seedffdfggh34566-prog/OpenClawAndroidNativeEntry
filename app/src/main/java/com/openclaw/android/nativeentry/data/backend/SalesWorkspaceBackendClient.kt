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
            is BackendReadResult.Failure -> return@withContext result
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
                is SocketTimeoutException -> "请确认后端已在 127.0.0.1:8013 启动，demo 数据已 seed，并已执行 adb reverse tcp:8013 tcp:8013。"
                else -> message ?: javaClass.simpleName
            },
        ),
    )
