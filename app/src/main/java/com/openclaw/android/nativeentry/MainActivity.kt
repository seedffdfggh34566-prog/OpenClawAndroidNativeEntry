package com.openclaw.android.nativeentry

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.openclaw.android.nativeentry.ui.OpenClawApp
import com.openclaw.android.nativeentry.ui.theme.OpenClawNativeEntryTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            OpenClawNativeEntryTheme {
                OpenClawApp()
            }
        }
    }
}

