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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun HomeScreen(
    gatewaySnapshot: GatewayCheckSnapshot,
    launchSnapshot: OpenClawLaunchSnapshot,
    onRefreshGatewayStatus: () -> Unit,
    onStartOpenClawClick: () -> Unit,
    onEnterChatClick: () -> Unit,
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
                    text = "OpenClaw Native Entry",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "A native Android entry point for an existing OpenClaw host environment.",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            GatewayStatusSummaryCard(
                snapshot = gatewaySnapshot,
                onRefreshClick = onRefreshGatewayStatus,
            )

            Button(
                onClick = onStartOpenClawClick,
                modifier = Modifier.fillMaxWidth(),
                enabled = !launchSnapshot.isLaunching,
            ) {
                Text(text = if (launchSnapshot.isLaunching) "启动中..." else "启动 OpenClaw")
            }

            OutlinedButton(
                onClick = onEnterChatClick,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = "进入聊天")
            }
        }
    }
}
