package com.openclaw.android.nativeentry.termux

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Bundle

internal const val TermuxResultExtraRequestId = "request_id"
internal const val TermuxResultExtraCommandKind = "command_kind"

class TermuxCommandResultReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val requestId = intent.getIntExtra(TermuxResultExtraRequestId, -1)
        if (requestId == -1) return

        val commandKind = intent.getStringExtra(TermuxResultExtraCommandKind).orEmpty()
        val rootExtras = intent.extras
        val resultBundle = findResultBundle(intent.extras)

        PendingOpenClawTermuxResults.complete(
            requestId = requestId,
            result = OpenClawTermuxCommandResult(
                commandKind = commandKind,
                requestId = requestId,
                exitCode = findInt(resultBundle, rootExtras, "exit_code"),
                stdout = findString(resultBundle, rootExtras, "stdout"),
                stderr = findString(resultBundle, rootExtras, "stderr"),
                errorMessage = findString(resultBundle, rootExtras, "errmsg")
                    ?: findString(resultBundle, rootExtras, "error"),
            ),
        )
    }

    private fun findResultBundle(extras: Bundle?): Bundle? {
        if (extras == null) return null
        extras.keySet().forEach { key ->
            val value = extras.get(key)
            if (value is Bundle) {
                return value
            }
        }
        return null
    }

    private fun findString(primary: Bundle?, fallback: Bundle?, keyHint: String): String? {
        val matchPrimary = primary.findMatchingKey(keyHint)
        if (matchPrimary != null) {
            return primary?.getString(matchPrimary)
        }

        val matchFallback = fallback.findMatchingKey(
            keyHint = keyHint,
            excludedKeys = setOf(TermuxResultExtraRequestId, TermuxResultExtraCommandKind),
        ) ?: return null
        return fallback?.getString(matchFallback)
    }

    private fun findInt(primary: Bundle?, fallback: Bundle?, keyHint: String): Int? {
        val matchPrimary = primary.findMatchingKey(keyHint)
        if (matchPrimary != null) {
            return primary?.readIntValue(matchPrimary)
        }

        val matchFallback = fallback.findMatchingKey(
            keyHint = keyHint,
            excludedKeys = setOf(TermuxResultExtraRequestId, TermuxResultExtraCommandKind),
        ) ?: return null
        return fallback?.readIntValue(matchFallback)
    }

    private fun Bundle?.findMatchingKey(
        keyHint: String,
        excludedKeys: Set<String> = emptySet(),
    ): String? {
        if (this == null) return null
        val candidates = keySet().filter { key ->
            key !in excludedKeys &&
                key.contains(keyHint, ignoreCase = true) &&
                !(keyHint == "stdout" && key.contains("original_length", ignoreCase = true)) &&
                !(keyHint == "stderr" && key.contains("original_length", ignoreCase = true))
        }
        return candidates.minWithOrNull(
            compareBy<String> { !it.endsWith(keyHint, ignoreCase = true) }
                .thenBy { it.length },
        )
    }

    private fun Bundle.readIntValue(key: String): Int? =
        when (val value = get(key)) {
            is Int -> value
            is Long -> value.toInt()
            is String -> value.toIntOrNull()
            else -> null
        }
}
