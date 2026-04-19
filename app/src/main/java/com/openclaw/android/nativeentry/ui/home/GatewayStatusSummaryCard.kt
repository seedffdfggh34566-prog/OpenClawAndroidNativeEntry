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
fun GatewayStatusSummaryCard(
    snapshot: GatewayCheckSnapshot,
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
                    enabled = snapshot.status !is GatewayStatus.Checking,
                ) {
                    Text(text = if (snapshot.status is GatewayStatus.Checking) "检测中" else "重新检测")
                }
            }

            Text(
                text = "检测地址：${snapshot.endpoint}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "最近更新：${snapshot.lastCheckedLabel()}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = snapshot.status.title(),
                style = MaterialTheme.typography.bodyLarge,
                color = statusColor(snapshot.status),
            )
            Text(
                text = snapshot.status.description(),
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
