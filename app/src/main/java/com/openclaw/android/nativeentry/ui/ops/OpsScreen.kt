package com.openclaw.android.nativeentry.ui.ops

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
import com.openclaw.android.nativeentry.ui.home.GatewayCheckSnapshot
import com.openclaw.android.nativeentry.ui.home.GatewayStatusSummaryCard
import com.openclaw.android.nativeentry.ui.home.OpenClawLaunchSnapshot
import com.openclaw.android.nativeentry.ui.home.attemptedAtLabel

@Composable
fun OpsScreen(
    gatewaySnapshot: GatewayCheckSnapshot,
    launchSnapshot: OpenClawLaunchSnapshot,
    onRefreshGatewayStatus: () -> Unit,
    onStartOpenClawClick: () -> Unit,
    onOpenDashboardClick: () -> Unit,
    onViewDiagnosticsClick: () -> Unit,
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
                    text = "运维与诊断",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "这里保留 Gateway、Dashboard、日志与启动能力，作为 AI 销售助手控制入口的辅助运维区域。",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            GatewayStatusSummaryCard(
                snapshot = gatewaySnapshot,
                onRefreshClick = onRefreshGatewayStatus,
            )

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = "运行入口",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Button(
                        onClick = onStartOpenClawClick,
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !launchSnapshot.isLaunching,
                    ) {
                        Text(text = if (launchSnapshot.isLaunching) "启动中..." else "启动 OpenClaw")
                    }
                    OutlinedButton(
                        onClick = onOpenDashboardClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "打开 Dashboard 技术入口")
                    }
                    OutlinedButton(
                        onClick = onViewDiagnosticsClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(text = "查看详细诊断")
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "诊断摘要",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(text = "最近一次启动尝试：${launchSnapshot.attemptedAtLabel()}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "启动发起说明：${launchSnapshot.dispatchMessage}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "tmux 会话检测：${launchSnapshot.tmuxSessionMessage}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = "当前诊断：${launchSnapshot.finalMessage}", style = MaterialTheme.typography.bodyMedium)
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "当前说明",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(
                        text = "该区域保留现有可运行能力，但不再作为产品默认首页。后续真实产品流程仍以后端对象和正式页面为准。",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }
    }
}
