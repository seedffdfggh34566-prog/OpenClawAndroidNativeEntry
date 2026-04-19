package com.openclaw.android.nativeentry.ui.logs

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.openclaw.android.nativeentry.ui.home.GatewayCheckSnapshot
import com.openclaw.android.nativeentry.ui.home.OpenClawLaunchSnapshot
import com.openclaw.android.nativeentry.ui.home.attemptedAtLabel
import com.openclaw.android.nativeentry.ui.home.diagnosticDetail
import com.openclaw.android.nativeentry.ui.home.diagnosticStatus
import com.openclaw.android.nativeentry.ui.home.lastCheckedLabel

@Composable
fun LogsScreen(
    gatewaySnapshot: GatewayCheckSnapshot,
    launchSnapshot: OpenClawLaunchSnapshot,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.TopCenter,
    ) {
        Card(
            modifier = Modifier
                .widthIn(max = 760.dp)
                .fillMaxWidth()
                .padding(horizontal = 24.dp, vertical = 28.dp),
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = "Logs",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "当前提供最小诊断信息，帮助确认 Gateway 检测结果是否已刷新。",
                    style = MaterialTheme.typography.bodyLarge,
                )
                Text(
                    text = "最近一次检测时间：${gatewaySnapshot.lastCheckedLabel()}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "检测地址：${gatewaySnapshot.endpoint}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "检测结果：${gatewaySnapshot.status.diagnosticStatus()}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "结果详情：${gatewaySnapshot.status.diagnosticDetail()}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "最近一次启动尝试：${launchSnapshot.attemptedAtLabel()}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "启动动作发起：${launchDispatchLabel(launchSnapshot)}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "启动发起说明：${launchSnapshot.dispatchMessage}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "外部启动日志：${launchSnapshot.logFilePath}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "脚本退出码：${launchSnapshot.bootExitCode?.toString() ?: "暂无"}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "tmux 会话检测：${launchSnapshot.tmuxSessionMessage}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "轮询状态：${if (launchSnapshot.pollingStarted) "已开始" else "未开始"}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "最终连接结果：${launchFinalLabel(launchSnapshot)}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "启动诊断：${launchSnapshot.finalMessage}",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
}

private fun launchDispatchLabel(snapshot: OpenClawLaunchSnapshot): String = when (snapshot.dispatchSucceeded) {
    true -> "已成功发起"
    false -> "发起失败"
    null -> "尚未尝试"
}

private fun launchFinalLabel(snapshot: OpenClawLaunchSnapshot): String = when (snapshot.connectionSucceeded) {
    true -> "已连接成功"
    false -> "未连接成功"
    null -> if (snapshot.isLaunching) "启动中" else "尚未完成"
}
