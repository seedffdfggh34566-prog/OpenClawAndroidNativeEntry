# 阶段性交接：Android CLI Knowledge Base 试点接入

更新时间：2026-04-23

## 1. 本次改了什么

- 在 `jianglab` 上安装了 Android CLI
- 验证了 `android --version`、`android -h`
- 验证了 `android docs search` / `android docs fetch`
- 更新 `docs/how-to/operate/jianglab_codex_ops.md`
- 新增本 task 记录

---

## 2. 为什么这么定

- 当前仓库已经在规则层接入 Android Knowledge Base，但此前还不能从命令行实际访问
- 当前 `adb` 已可用，而 Android CLI 适合作为 Android 文档 grounding 的推荐增强入口
- 官方安装脚本默认落到 `/usr/local/bin`，当前环境没有无密码 sudo，因此改用官方 Linux 二进制直链安装到已在 `PATH` 中的 `/home/yulin/bin`
- 试点成功后，Android CLI 可以升级为推荐增强工具，但仍不替代现有主链路

---

## 3. 本次验证了什么

1. `android` 命令已可用：`/home/yulin/bin/android`
2. `android --version` 返回 `0.7.15232955`
3. `android -h` 正常输出命令帮助
4. `android info` 正常识别：
   - `sdk: /usr/lib/android-sdk`
   - `version: 0.7.15232955`
5. `android docs search` 成功返回与当前仓库相关的 `kb://...` 结果
6. `android docs fetch` 成功拉取文档内容
7. `git diff --check` 通过

---

## 4. 样例结果摘要

本次至少验证了以下 3 类查询：

1. Compose screenshot testing
   - 搜索返回 `kb://android/training/testing/ui-tests/screenshot`
   - fetch 结果明确指出 screenshot testing 是验证 Compose UI 视觉属性的推荐方式
2. `AndroidManifest.xml` / exported / permission / deep link
   - 搜索返回 exported component 与 deep link 相关官方文档
   - fetch 结果可直接支撑 Manifest / permission 风险判断
3. Navigation Compose / architecture guidance
   - 搜索返回 `kb://android/develop/ui/compose/navigation`
   - fetch 结果能支撑 Navigation Compose 相关建议

---

## 5. 已知限制

- 首次并发运行 `android docs search` 时，Knowledge Base 索引初始化可能发生竞争，建议首次使用串行执行
- 命令会打印 Java foreign linker warning，但当前不影响 `docs search/fetch` 正常工作
- 当前只试点了 Knowledge Base 访问能力，没有继续试点其他 Android CLI 子命令

---

## 6. 结论与推荐下一步

结论：

1. Android CLI 已经值得纳入当前仓库的**推荐增强工具**
2. 它应继续保持“可选增强”定位，不替代 `adb + gradle + docs + task/handoff`

推荐下一步：

1. 后续 Android 相关研究、架构判断和最新 guidance 查询时，优先考虑 `android docs search/fetch`
2. 观察一段实际使用情况后，再决定是否把 `android docs` 的使用方式补回 Android 相关 Skill specs
