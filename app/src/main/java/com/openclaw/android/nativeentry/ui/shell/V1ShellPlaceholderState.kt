package com.openclaw.android.nativeentry.ui.shell

enum class PlaceholderHistoryEntryType {
    ProductProfile,
    AnalysisResult,
    AnalysisReport,
}

data class PlaceholderRunStatus(
    val stageTitle: String,
    val statusLabel: String,
    val updatedAt: String,
    val summary: String,
)

data class PlaceholderProductProfile(
    val name: String,
    val oneLineDescription: String,
    val statusLabel: String,
    val targetCustomers: String,
    val typicalUseCases: String,
    val coreAdvantages: List<String>,
    val missingInfo: List<String>,
)

data class PlaceholderAnalysisResult(
    val statusLabel: String,
    val updatedAt: String,
    val priorityIndustries: List<String>,
    val priorityCustomerTypes: List<String>,
    val recommendationReasons: List<String>,
    val risks: List<String>,
)

data class PlaceholderReportSection(
    val title: String,
    val body: String,
)

data class PlaceholderReport(
    val title: String,
    val versionLabel: String,
    val updatedAt: String,
    val summary: String,
    val nextSteps: List<String>,
    val sections: List<PlaceholderReportSection>,
)

data class PlaceholderHistoryEntry(
    val type: PlaceholderHistoryEntryType,
    val title: String,
    val subtitle: String,
    val statusLabel: String,
)

data class V1ShellPlaceholderState(
    val runStatus: PlaceholderRunStatus,
    val productProfile: PlaceholderProductProfile,
    val analysisResult: PlaceholderAnalysisResult,
    val report: PlaceholderReport,
    val historyEntries: List<PlaceholderHistoryEntry>,
)

fun sampleV1ShellPlaceholderState(): V1ShellPlaceholderState =
    V1ShellPlaceholderState(
        runStatus = PlaceholderRunStatus(
            stageTitle = "产品画像待确认",
            statusLabel = "running",
            updatedAt = "2026-04-21 10:20",
            summary = "系统已完成第一轮产品学习整理，当前等待你确认 ProductProfile 后继续生成获客分析结果。",
        ),
        productProfile = PlaceholderProductProfile(
            name = "AI 销售助手 V1",
            oneLineDescription = "面向中小团队的销售定位与获客分析助手。",
            statusLabel = "draft",
            targetCustomers = "中小企业老板、销售负责人、个人 BD",
            typicalUseCases = "澄清产品定位、判断优先行业、快速形成第一版分析材料",
            coreAdvantages = listOf(
                "通过对话快速收口产品理解",
                "把分析结果沉淀为可复看的结构化对象",
                "支持后续继续完善与重跑",
            ),
            missingInfo = listOf(
                "当前成交模式与价格区间",
                "优先销售区域",
                "已有客户反馈或验证信号",
            ),
        ),
        analysisResult = PlaceholderAnalysisResult(
            statusLabel = "published",
            updatedAt = "2026-04-21 10:32",
            priorityIndustries = listOf("企业服务", "教育培训", "本地生活服务商"),
            priorityCustomerTypes = listOf("创始人", "销售负责人", "商务拓展负责人"),
            recommendationReasons = listOf(
                "这类团队通常缺少标准化销售分析材料，最容易接受快速产出的结构化建议。",
                "目标用户对“先讲清产品、再找方向”的需求更强，和 V1 主线高度匹配。",
                "销售团队小、决策链短，便于快速验证分析建议是否有效。",
            ),
            risks = listOf(
                "若产品输入过于模糊，优先级建议会偏保守。",
                "当前结果仍是占位壳层，不代表真实后端分析输出。",
            ),
        ),
        report = PlaceholderReport(
            title = "AI 销售助手 V1 获客分析报告",
            versionLabel = "v0.1 placeholder",
            updatedAt = "2026-04-21 10:40",
            summary = "该报告展示产品理解摘要、优先行业方向、客户类型建议和下一步验证动作，用于演示 Android 控制壳层的信息组织方式。",
            nextSteps = listOf(
                "确认 ProductProfile 的关键字段",
                "补充成交模式与已知案例",
                "基于优先行业方向做下一轮分析",
            ),
            sections = listOf(
                PlaceholderReportSection(
                    title = "产品理解摘要",
                    body = "当前产品重点帮助用户先讲清楚卖什么、卖给谁，再形成一版可执行的获客分析结果。",
                ),
                PlaceholderReportSection(
                    title = "获客方向建议",
                    body = "优先覆盖需要快速澄清销售定位的小团队，先验证企业服务、教育培训和本地服务商方向。",
                ),
                PlaceholderReportSection(
                    title = "风险提醒",
                    body = "如果用户没有明确的购买动因和成交模式，后续建议会偏泛，需要在下一轮补充关键信息。",
                ),
            ),
        ),
        historyEntries = listOf(
            PlaceholderHistoryEntry(
                type = PlaceholderHistoryEntryType.ProductProfile,
                title = "ProductProfile 草稿",
                subtitle = "AI 销售助手 V1 · 待确认",
                statusLabel = "draft",
            ),
            PlaceholderHistoryEntry(
                type = PlaceholderHistoryEntryType.AnalysisResult,
                title = "LeadAnalysisResult",
                subtitle = "优先行业与客户类型建议",
                statusLabel = "published",
            ),
            PlaceholderHistoryEntry(
                type = PlaceholderHistoryEntryType.AnalysisReport,
                title = "AnalysisReport",
                subtitle = "结构化报告占位页",
                statusLabel = "published",
            ),
        ),
    )
