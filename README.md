# Meizu 21 Note（M2468）内核源码清单

为**官方 LineageOS 23.2 源码树**提供 M2468 设备树、内核、外部驱动和 DTS 的 `repo` 本地清单。同步后由 Lineage 的标准构建规则从源码编译，不需要本机接入包、`prepare_layout.py` 或服务器信息采集步骤。

当前是源码 bring-up：已完成本地内核、386 个源码模块和 6 个 DT 的构建验证。2026-10-06 用户报告进入系统，只读 ADB 确认 `sys.boot_completed=1`、M2468 声卡、两颗 CS35L43 和 AudioFlinger/AudioPolicy 已注册；观察的 ROM 为 LineageOS 24.0 / Android 17 / SDK 37，内核为 5.15.211，不能视为官方 23.2 整 ROM 验证。音频播放/录音及日常功能仍待验证。这不是魅族官方源码发布，也不是 LineageOS 官方支持声明。

2026-10-06 最新：用户确认音量下误截图和无法熄屏已修好，后续空闲输入采样未见旧电源键风暴。另已分别提交两项待实机验证的修复：设备配置默认关闭同步调试 UART 控制台；M2468 RC0 新增 `device_type = "pci"`，纠正当前 OF 解析器把 PCI ranges 误当普通 flags 的问题。后者保留全部原厂属性，六份 DT 与五组 overlay 合并仅有这一项属性增加，不能再称候选与原厂全属性完全相同。两项已离线验证；启动提速、PCI BAR 分配、Wi-Fi 驱动绑定和联网仍待新镜像验证。

已有分支跟随清单的服务器，在现有 ROM 根目录执行 `repo sync -c device/meizu/m2468 kernel/meizu/sm8550-devicetrees` 后 `mka bacon`。无需重新下载 XML、清理 out 或更改 ROM 默认 Clang。

## 服务器同步和编译

在已有的官方 `lineage-23.2` 源码树根目录执行。服务器已有的 `vendor/meizu/m2468` 等 vendor blobs 和其余 ROM 依赖继续使用；本组织不提供 dump、闭源 blobs 或预编译设备内核。

```bash
mkdir -p .repo/local_manifests
curl -fL https://raw.githubusercontent.com/meizu-sm8550-kernel/kernel_manifest/lineage-23.2/local_manifest.xml \
  -o .repo/local_manifests/zzzz-meizu-m2468.xml
repo sync -c -j8

source build/envsetup.sh
breakfast m2468 userdebug
mka kernel dtboimage bootimage vendorbootimage vendor_dlkmimage system_dlkmimage
```

构建完整 ROM 使用同一个已选择的产品：

```bash
mka bacon
```

标准产物目录是 `out/target/product/m2468/`，使用自定义 `OUT_DIR` 时以 `$OUT` 为准。上述命令是构建入口，尚未以完整服务器构建验证全部产物。不要把模块和 DTS 编译通过理解成可正常开机或可日用。

`breakfast m2468 userdebug` 会读取当前树的 `vendor/lineage/vars/aosp_target_release`，再调用三段式 `lunch`。不在命令中硬编码 release 名称。构建入口依据官方 [envsetup.sh](https://github.com/LineageOS/android_vendor_lineage/blob/686d8669737d2207208ea21075320840b5ec8463/build/envsetup.sh)、[kernel.mk](https://github.com/LineageOS/android_vendor_lineage/blob/686d8669737d2207208ea21075320840b5ec8463/build/tasks/kernel.mk) 和 [core/main.mk](https://github.com/LineageOS/android_build/blob/e5aaa62172df0f321e68133fa30f42316376bfe8/core/main.mk)。

若服务器尚无 ROM 源码树，先按 [LineageOS 官方清单说明](https://github.com/LineageOS/android/tree/lineage-23.2) 在空目录初始化，再执行上面的本地清单同步步骤：

```bash
repo init -u https://github.com/LineageOS/android.git -b lineage-23.2 --git-lfs
```

本仓库只是本地清单覆盖层，不能替代官方 ROM manifest；只同步本仓库列出的项目不会得到完整 ROM 源码或 vendor blobs。

## 清单范围

| 仓库 | ROM 源码树路径 |
| --- | --- |
| `android_kernel_meizu_sm8550` | `kernel/meizu/sm8550` |
| `android_kernel_meizu_sm8550-modules` | `kernel/meizu/sm8550-modules` |
| `android_kernel_meizu_sm8550-devicetrees` | `kernel/meizu/sm8550-devicetrees` |
| `android_device_meizu_m2468` | `device/meizu/m2468` |

前四个仓库的当前默认分支均为 `lineage-23.2`。`local_manifest.xml` 跟随该分支的最新提交，项目上不指定 revision，也不固定提交 SHA；专用 remote 统一指定 `refs/heads/lineage-23.2`，避免继承 ROM 主清单的 `avium-16.2` 或其它分支。每次 `repo sync -c` 都同步该源码分支最新提交。

旧下载地址 `pinned.xml` 保留为 `local_manifest.xml` 的同内容兼容入口，**现在也不锁定提交**。两者安装到同一个 `.repo/local_manifests/zzzz-meizu-m2468.xml`，不要重复安装。`revisions.lock.json` 仅记录某次发布的 SHA 用于审计，不控制 repo 同步版本。

清单只添加表中四个源码项目，不含任何 `remove-project`。其它清单声明的项目保持原样，包括 `vendor/meizu/m2468`、其它设备项目、ROM 默认 Clang，以及可能存在的旧 prebuilt 或独立 Clang 项目。

四个源码路径应各声明一次。若主清单或另一份 local manifest 已声明相同路径，Repo 会报告 `duplicate path`；应将已有声明整理为一个入口。本清单不会自动覆盖或移除它们，XML 文件排序也不能消除重复声明。

这些行为已对照 [Repo 官方 manifest 格式](https://gerrit.googlesource.com/git-repo/+/7bba4ee47e72ccfe7838b62869029e2f7436ce39/docs/manifest-format.md) 和实际解析器验证：正常添加、保留不同路径的旧项目、相同名字位于其它路径、主清单和本地清单的重复路径报错。两个入口各覆盖三种 ROM 分支、四种布局，共24组场景。

## 版本和工具链

ROM 构建规则以官方 **LineageOS 23.2** 为基准。内核源码基线来自 LineageOS SM8550 的 **`lineage-21` / Android 13 / Linux 5.15.211 / KMI generation 8**；仓库的发布分支名不代表内核已升级到与 ROM 同代的 Android 内核。上游提交和已核对的 ROM 构建规则提交见 [upstream.lock.json](upstream.lock.json)。

内核编译器使用 LineageOS 平台默认选择。设备树不设置 `TARGET_KERNEL_CLANG_VERSION` 或 `TARGET_KERNEL_CLANG_PATH`，官方规则使用 `LLVM_AOSP_PREBUILTS_VERSION` 与 ROM 自带的 `prebuilts/clang/host/linux-x86`。

本清单不声明额外 Clang 仓库，也不移除其它清单可能声明的 Clang 项目。内核继续使用 ROM 默认工具链。

两个 XML 均不固定提交 SHA。需要记录一次服务器实际同步到的完整构建输入，可在同步后运行：

```bash
repo manifest -r -o m2468-build-manifest.xml
```

## 已验证内容与功能缺口

- 本地已编译内核与 386 个源码模块，并验证 597 条 ELF 硬依赖边；这不涵盖 DT 供应者、固件、OEM init/sysfs 和启动依赖。
- M2468 的 1 个 DTB、5 个 DTBO 由源码经内核 Kbuild/dtc 构建。DTS 包含从该机原厂 DT 重建的字节属性；这是可构建的重建源码，不是原厂维护的带标签 DTS，也不代表设备语义全部恢复。
- 显示和 Goodix 触控包含针对 M2468 的源码适配。HBM 只实现受限亮屏路径；FOD/AOD、黑屏切换及完整指纹联动没有完成运行验证。
- `jiiov_fingerprint` 以及魅族充电、温控、启动和其它 OEM 模块仍有源码缺口。通用高通驱动可编译不等于这些 OEM 功能已恢复。
- 已确认上述设备完成启动；未在本地验证完整 ROM 构建，也未验证所有模块加载、外设和日常功能。已编译的模块数量不能作为整机兼容性结论。

## 来源与许可

内核、外部模块和平台 DTS 基于公开的 LineageOS/QCOM SM8550 仓库；设备树基于 [AstralSpun/android_device_meizu_m2468](https://cnb.cool/AstralSpun/android_device_meizu_m2468)。M2468 显示/触控适配是在公开源码上重写兼容接口，参考该型号的 DT 和原厂接口行为；不是恢复出魅族原始 C 源码。各源码仓库保留其上游许可、版权声明和来源记录。

本 manifest 仓库中的清单、脚本和文档使用 Apache-2.0，见 [LICENSE](LICENSE)。这不改变被引用源码、AOSP 工具链或设备固件各自的许可。本组织不再分发设备 dump、闭源固件、用户空间 blobs 或原厂内核二进制。

## 维护发布记录

维护者在源码提交发布后更新审计记录；脚本保留旧名称以兼容维护流程，但不再生成提交固定清单。正常服务器构建不需要运行此脚本：

```bash
python3 pin_revisions.py --repos-dir ..
```

该目录需包含表中的四个完整仓库名，且都在干净的 `lineage-23.2` 分支。也可用 `--revisions /path/to/revisions.json` 输入 JSON 对象，四个键为仓库名、值为真实的完整 40 位提交 SHA。源码提交推送后，服务器普通 `repo sync -c` 即可取得更新，无需为每个新 SHA 重新下载 XML。维护者仍更新 `revisions.lock.json` 中的发布记录；脚本同时保持两个 XML 入口同内容，不会恢复项目 revision，并拒绝含 `remove-project` 的输入。不要填入占位 SHA。

可选的 `verify_manifest.py --repo-source /path/to/git-repo` 使用官方 Repo 解析器做离线组合检查，不执行 sync、不修改服务器源码，也不是构建前置步骤。

2026-10-06 音频更新：新增源码 CS35L43 功放模块，并按 M2468 原厂接口修正 TX3/TX4 与 secondary MI2S 双功放链路；设备 vendor 加载清单同步更新。公开源码不包含原厂模块或调音固件。新候选须由用户构建并验证，编译/CRC 检查不代表已解决全部启动问题。

2026-10-06 首轮黑屏修复：按 M2468 原厂接口补齐 ILI7838E ESD 分页读取和状态判定，保留异常恢复。用户更新后反馈黑闪消失，后续只读采样的保留日志中未见原 ESD 错误或 PANEL_DEAD；这不代表所有显示场景均已验证。

2026-10-06 第二轮按键修复：内核驱动为 M2468 的 `qcom,use-bark` 节点恢复独立中断处理和上升沿，不再通过普通按键路径生成虚假 KEY_POWER；probe 与恢复路径使用同一分派。普通电源键/音量下、DT 和 PMIC 复位配置保持。通过真实 C 路径回归及复用既有基础产物的单模块编译、CRC/CFI 检查，候选尚未上机；熄屏、实体按键、负载及长按复位仍待验证。原厂长按复位前的显示关闭回调未恢复，WLAN 等其它问题未由此修复。
