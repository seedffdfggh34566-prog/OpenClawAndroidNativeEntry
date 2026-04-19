# OpenClaw Dashboard `static {}` 改动说明

## 结论先行

这次处理并不是“直接把前端产物里的 `static {}` 手工删除”。

实际做法是：

1. 只修改了 Dashboard 的构建配置文件 `openclaw-main/ui/vite.config.ts`
2. 在 `build` 配置中新增了更保守的 `target`
3. 重新构建 Dashboard 前端产物
4. 用新的构建产物替换设备上的 `dist/control-ui`

因此，`static {}` 的消失来自“构建器重新生成了更低目标环境兼容的等价产物”，而不是“把某段初始化逻辑硬删掉”。

## 具体改动

改动文件：

- `openclaw-main/ui/vite.config.ts`

改动内容：

```ts
build: {
  target: ["chrome64", "edge79", "firefox67", "safari12"],
  outDir: path.resolve(here, "../dist/control-ui"),
  emptyOutDir: true,
  sourcemap: true,
  chunkSizeWarningLimit: 1024,
}
```

其中，新增的是：

```ts
target: ["chrome64", "edge79", "firefox67", "safari12"]
```

## 为什么会出现 `static {}`

旧产物 `index-Ij2djnNX.js` 中的 `static {}` 不是业务代码手写，而是构建后生成的现代 JavaScript 语法。

通过 sourcemap 反查，命中来源是：

- `ui/src/ui/components/resizable-divider.ts`

对应源码模式是：

- `@customElement("resizable-divider")`
- 多个 `@property(...)`
- `static styles = css\`...\``

构建后，这类 Lit 组件静态成员初始化在旧入口 bundle 中被表达成了 `static { ... }` 形式。

## `static {}` 在原来的产物里起什么作用

这次命中的 `static {}` 主要承担的是“类静态初始化”职责，尤其是给组件类挂上静态样式。

在当前命中的组件里，它的作用可以理解为：

- 在类定义完成后，为类设置 `styles`
- 让 Lit 在运行时能够读取这个组件的静态样式

这不是无关紧要的空代码。对 `resizable-divider` 这种组件来说，如果相关初始化真的丢了，可能会导致：

- 分隔条样式丢失
- hover / dragging 样式失效
- 分隔条可见性或交互反馈异常

## 这次改动为什么不是“危险删逻辑”

因为这次没有手工编辑旧 bundle，也没有直接删除 `static {}` 代码块。

真实发生的是：

- 降低构建 target
- 重新 build
- 由构建器生成一个不再使用 `static {}` 的等价产物

也就是说，变化的是“语法表达方式”，不是“要执行的初始化语义”。

这也是为什么：

- 旧设备上的 `Unexpected token '{'` 消失了
- 页面开始可以正常渲染
- 但没有立刻因为“删掉关键逻辑”而导致 Dashboard 整体坏掉

## 对运行产生了什么实际影响

### 正向影响

这次改动直接解决了 HarmonyOS / Huawei WebView 11 上的 parser 级报错：

- 旧现象：`Unexpected token '{'`
- 旧页面状态：兼容性失败页
- 新现象：`static {}` 不再出现在新入口产物中
- 新页面状态：Dashboard 可以实际渲染

实际真机结果已经验证：

- 页面标题可见
- WebView 内已有真实内容
- `DOM probe` 的 `textLength` 从 `0` 变成了非零
- 不再停留在“设备兼容性失败”

### 未改变的部分

这次改动不会改变以下内容：

- Dashboard 业务逻辑
- Gateway token 是否正确
- connect 请求的语义
- Android 壳层行为
- WebView 配置

因此，这次改动只能解决“前端 bundle 解析失败”，不能自动解决后续的网关连接失败。

## 如果当时是直接删掉 `static {}`，会有什么风险

如果是手工直接改旧 bundle，把 `static {}` 整段删掉，而没有补等价逻辑，风险包括：

1. 组件静态样式丢失
2. 类初始化顺序被破坏
3. UI 行为异常但不一定立即崩溃
4. 引入难以定位的前端回归 bug

所以，“硬删产物里的 `static {}`”不是推荐方案。

## 替代方式比较

### 方案 A：调整构建 target

这是本次采用的方案。

优点：

- 改动面最小
- 不改业务源码
- 更接近官方构建链的正确用法

风险：

- 可能暴露下一个旧环境兼容点

### 方案 B：局部改源码写法

例如把 `static styles = css\`...\`` 改写为更保守的等价形式。

优点：

- 可以定点规避某个组件的现代语法输出

风险：

- 容易引入局部回归
- 需要仔细处理 Lit / 装饰器 / 类初始化顺序

### 方案 C：引入更重的 legacy/transpile 补偿链

例如再加 Babel / legacy 插件。

优点：

- 可以更系统地压低前端产物语法级别

风险：

- 构建复杂度更高
- 回归面更大

## 最终结论

这次前端改动的本质不是“删掉 `static {}`”，而是：

- 通过修改 `vite.config.ts` 的 `build.target`
- 让 Vite 重新产出一份不再包含 `static {}` 的兼容性更强的 bundle

因此：

- 这是一次构建级兼容修正
- 不是手工删除类初始化逻辑
- 直接副作用较小、可控
- 真机结果证明它成功跨过了原来的前端解析阻塞点

