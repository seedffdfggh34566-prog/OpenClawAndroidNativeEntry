package com.openclaw.android.nativeentry.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.openclaw.android.nativeentry.ui.shell.V1ShellPlaceholderState

@Composable
fun HomeScreen(
    placeholderState: V1ShellPlaceholderState,
    onStartAnalysisClick: () -> Unit,
    onContinueFlowClick: () -> Unit,
    onViewHistoryClick: () -> Unit,
    onViewLatestAnalysisClick: () -> Unit,
    onViewLatestReportClick: () -> Unit,
    onViewOpsClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.TopCenter,
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 760.dp)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(PaddingValues(horizontal = 24.dp, vertical = 28.dp)),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "AI 销售助手 V1",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "通过产品学习、获客分析和结构化报告，帮助你用更短时间明确下一步销售方向。",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            Button(
                onClick = onStartAnalysisClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "开始分析")
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "当前工作摘要",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(text = "阶段：${placeholderState.runStatus.stageTitle}", style = MaterialTheme.typography.bodyLarge)
                    Text(text = "状态：${placeholderState.runStatus.statusLabel}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "最近更新时间：${placeholderState.runStatus.updatedAt}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = placeholderState.runStatus.summary, style = MaterialTheme.typography.bodyMedium)
                    OutlinedButton(
                        onClick = onContinueFlowClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "继续当前流程")
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "最近结果入口",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(
                        text = "ProductProfile：${placeholderState.productProfile.name} (${placeholderState.productProfile.statusLabel})",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    OutlinedButton(
                        onClick = onViewLatestAnalysisClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "查看最新分析结果")
                    }
                    OutlinedButton(
                        onClick = onViewLatestReportClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "查看最新分析报告")
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "辅助入口",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    OutlinedButton(
                        onClick = onViewHistoryClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "查看历史与状态")
                    }
                    OutlinedButton(
                        onClick = onViewOpsClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "进入运维与诊断")
                    }
                }
            }
        }
    }
}
