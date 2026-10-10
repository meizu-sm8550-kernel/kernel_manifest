# M2468 提交与命名约定

本组织保留平台名称 `meizu-sm8550-kernel`，当前只维护 `m2468`。产品名“魅族 21 Note”可用于介绍设备，代码中的设备代号统一为 `m2468`，英文描述可写 `M2468`。

## 提交格式

采用与 M2481 仓库一致的形式：

```text
<subsystem>: <Capitalized imperative description>

Explain the problem and the resulting behavior when the title alone
is insufficient. State the scope and relevant validation accurately.
```

标题尽量控制在 72 字符以内，不加句号。动词使用 `Add`、`Fix`、`Restore`、`Enable`、`Use` 等；正文按约 72 列换行。已有作者、来源和真实签署信息应保留，不补造签署或测试结论。

| 范围 | 标题示例 |
| --- | --- |
| 内核配置 | `arm64: configs: Enable M2468 PM8008 camera regulators` |
| 内核驱动 | `input: qcom-hv-haptics: Restore M2468 persisted boot period` |
| 显示 | `display-drivers: Use M2468 ILI7838E banked ESD checks` |
| 触控 | `touch-drivers: goodix: Normalize M2468 coordinate units` |
| 音频 | `audio-kernel: Add M2468 CS35L43 support` |
| 设备树 | `devicetree: Declare the M2468 RC0 PCI bus type` |
| Android 设备配置 | `m2468: Use the platform default Clang toolchain` |
| 清单 | `manifest: Record M2468 haptics fixes` |

一条提交聚焦一个子系统内的一项修改。相关测试和接口说明随实现提交；显示、触控、WLAN 等独立适配分开提交。后续修复写明具体行为，避免含糊的 `fix issues` 或把发布日志当作实现说明。

## 兼容性边界

自有标识示例为 `dsi_m2468_hbm`、`goodix_m2468_request_work`、`M2468_HBM_OFF`。测试路径和环境变量同步使用 `m2468` / `M2468`。

不要机械替换原厂 DT 属性、compatible、固件名、sysfs 节点、ioctl/netlink 值或 OTA 兼容别名 `meizu21Note`。上游注释中表示“注意”的英文 `Note` 也不是设备代号。历史文件名和原始构建记录保留可追溯性。

## 验证与历史维护

提交前运行受影响驱动的已有主机测试和所需构建检查；清单改动使用 `verify_manifest.py` 核对。准确区分源码检查、编译结果和设备运行反馈。

历史重整保留原上游基线、作者与提交映射。源码 SHA 改变后同步更新审计记录；两个 XML 继续跟随源码分支，不改为锁定 SHA。
