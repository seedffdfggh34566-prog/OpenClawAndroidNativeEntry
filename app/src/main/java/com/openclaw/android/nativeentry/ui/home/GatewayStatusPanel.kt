package com.openclaw.android.nativeentry.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun GatewayStatusPanel(
    status: GatewayStatus,
    onRefreshClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "Gateway 状态",
                    style = MaterialTheme.typography.titleMedium,
                )
                TextButton(
                    onClick = onRefreshClick,
                    enabled = status !is GatewayStatus.Checking,
                ) {
                    Text(text = if (status is GatewayStatus.Checking) "检测中" else "重新检测")
                }
            }

            Text(
                text = "检测地址：$GatewayEndpoint",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Text(
                text = statusTitle(status),
                style = MaterialTheme.typography.bodyLarge,
                color = statusColor(status),
            )

            Text(
                text = statusDescription(status),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun statusColor(status: GatewayStatus): Color = when (status) {
    GatewayStatus.Checking -> MaterialTheme.colorScheme.primary
    is GatewayStatus.Running -> MaterialTheme.colorScheme.secondary
    GatewayStatus.Unreachable -> MaterialTheme.colorScheme.error
    is GatewayStatus.Failed -> MaterialTheme.colorScheme.error
}

private fun statusTitle(status: GatewayStatus): String = when (status) {
    GatewayStatus.Checking -> "状态：检测中"
    is GatewayStatus.Running -> "状态：已连接 / 运行中"
    GatewayStatus.Unreachable -> "状态：无法连接"
    is GatewayStatus.Failed -> "状态：检测失败"
}

private fun statusDescription(status: GatewayStatus): String = when (status) {
    GatewayStatus.Checking -> "正在检测本机 Gateway，请稍候。"
    is GatewayStatus.Running -> "已收到本机 Gateway 响应（HTTP ${status.statusCode}），说明服务正在监听该地址。"
    GatewayStatus.Unreachable -> "当前无法连接到 127.0.0.1:18789，请确认设备上的 Gateway 是否已启动。"
    is GatewayStatus.Failed -> "检测过程中发生异常：${status.message}"
}
