package com.openclaw.android.nativeentry.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = SlateBlue,
    secondary = DeepTeal,
    background = Mist,
    surface = androidx.compose.ui.graphics.Color.White,
    surfaceVariant = SurfaceTint,
    onPrimary = androidx.compose.ui.graphics.Color.White,
    onSecondary = androidx.compose.ui.graphics.Color.White,
    onBackground = Ink,
    onSurface = Ink,
    onSurfaceVariant = MutedInk,
)

private val DarkColors = darkColorScheme(
    primary = SurfaceTint,
    secondary = DeepTeal,
)

@Composable
fun OpenClawNativeEntryTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = OpenClawTypography,
        content = content,
    )
}

