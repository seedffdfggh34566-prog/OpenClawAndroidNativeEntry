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

class V1BackendClient(
    private val baseUrl: String = V1BackendBaseUrl,
) {
    suspend fun createProductProfile(
        payload: ProductProfileCreateRequestDto,
    ): BackendReadResult<ProductProfileCreateResponseDto> =
        requestJson(
            method = "POST",
            path = "/product-profiles",
            body = payload.toJsonBody(),
            parser = ::parseProductProfileCreateResponse,
        )

    suspend fun createAnalysisRun(
        payload: AnalysisRunCreateRequestDto,
    ): BackendReadResult<AnalysisRunCreateResponseDto> =
        requestJson(
            method = "POST",
            path = "/analysis-runs",
            body = payload.toJsonBody(),
            parser = ::parseAnalysisRunCreateResponse,
        )

    suspend fun getAnalysisRun(id: String): BackendReadResult<AnalysisRunDetailResponseDto> =
        requestJson(
            method = "GET",
            path = "/analysis-runs/${id.encodePathSegment()}",
            parser = ::parseAnalysisRunDetailResponse,
        )

    suspend fun getHistory(): BackendReadResult<HistoryResponseDto> =
        requestJson(method = "GET", path = "/history", parser = ::parseHistoryResponse)

    suspend fun getProductProfile(id: String): BackendReadResult<ProductProfileDetailDto> =
        requestJson(
            method = "GET",
            path = "/product-profiles/${id.encodePathSegment()}",
            parser = ::parseProductProfileDetail,
        )

    suspend fun getReport(id: String): BackendReadResult<ReportDetailDto> =
        requestJson(
            method = "GET",
            path = "/reports/${id.encodePathSegment()}",
            parser = ::parseReportDetail,
        )

    suspend fun getLeadAnalysisResult(id: String): BackendReadResult<LeadAnalysisResultDetailDto> =
        requestJson(
            method = "GET",
            path = "/lead-analysis-results/${id.encodePathSegment()}",
            parser = ::parseLeadAnalysisResultDetail,
        )

    suspend fun confirmProductProfile(id: String): BackendReadResult<ProductProfileConfirmResponseDto> =
        requestJson(
            method = "POST",
            path = "/product-profiles/${id.encodePathSegment()}/confirm",
            parser = ::parseProductProfileConfirmResponse,
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
            return@withContext error.toBackendReadFailure()
        }

        try {
            if (body != null) {
                connection.outputStream.use { stream ->
                    stream.write(body.toByteArray(StandardCharsets.UTF_8))
                }
            }
            val statusCode = connection.responseCode
            val body = connection.bodyFor(statusCode)
            if (statusCode !in 200..299) {
                return@withContext BackendReadResult.Failure(
                    BackendReadError(
                        title = "后端返回 HTTP $statusCode",
                        detail = body.ifBlank { "请求 $path 未成功。" },
                    ),
                )
            }

            BackendReadResult.Success(parser(body))
        } catch (error: JSONException) {
            BackendReadResult.Failure(
                BackendReadError(
                    title = "后端响应解析失败",
                    detail = error.message ?: error.javaClass.simpleName,
                ),
            )
        } catch (error: Exception) {
            error.toBackendReadFailure()
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

private fun Exception.toBackendReadFailure(): BackendReadResult.Failure =
    BackendReadResult.Failure(
        BackendReadError(
            title = when (this) {
                is ConnectException,
                is NoRouteToHostException,
                is SocketTimeoutException -> "无法连接 V1 后端"
                else -> "V1 后端请求失败"
            },
            detail = when (this) {
                is ConnectException,
                is NoRouteToHostException,
                is SocketTimeoutException -> "请确认后端已在 127.0.0.1:8013 启动，并已执行 adb reverse tcp:8013 tcp:8013。"
                else -> message ?: javaClass.simpleName
            },
        ),
    )
