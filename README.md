# Meizu 21 Note（M2468）内核源码清单

为**官方 LineageOS 23.2 源码树**提供 M2468 设备树、内核、外部驱动和 DTS 的 `repo` 本地清单。同步后由 Lineage 的标准构建规则从源码编译，不需要本机接入包、`prepare_layout.py` 或服务器信息采集步骤。

当前是源码 bring-up：已完成本地内核、386 个源码模块和 6 个 DT 的构建验证；已有源码内核运行至开机动画的证据，**音频修复候选尚未上机，尚无正常进入桌面和音频功能证据**。这不是魅族官方源码发布，也不是 LineageOS 官方支持声明。

## 服务器同步和编译

在已有的官方 `lineage-23.2` 源码树根目录执行。服务器已有的 `vendor/meizu/m2468` 等 vendor blobs 和其余 ROM 依赖继续使用；本组织不提供 dump、闭源 blobs 或预编译设备内核。

```bash
mkdir -p .repo/local_manifests
curl -fL https://raw.githubusercontent.com/meizu-sm8550-kernel/kernel_manifest/lineage-23.2/pinned.xml \
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

前四个仓库的开发分支均为 `lineage-23.2`。`pinned.xml` 固定一次发布的四个源码提交；`revisions.lock.json` 记录同一组值。`local_manifest.xml` 跟随四仓分支最新提交，编译器由ROM主清单提供。需要跟进开发分支时，将下载 URL 中的 `pinned.xml` 改为 `local_manifest.xml`，安装到**同一个**本地清单文件；不要同时安装两份。

清单按精确 `path` 替换表中项目，同时移除旧 `device/meizu/m2468-kernel` 预编译项目的 manifest 声明。`optional="true"` 允许这些旧项目不存在；同名但不同路径的项目不受影响。保留 `vendor/meizu/m2468`、其它设备项目和 ROM 默认的 `prebuilts/clang/host/linux-x86`。

Repo 按文件名字母顺序读取 `.repo/local_manifests/*.xml`。本清单应放在其它声明这些相同路径的本地清单之后；后续文件若再次声明相同路径，会报 duplicate path，应只调整冲突条目。清单移除的是项目声明，随后普通 `repo sync` 可能清理退出清单的旧 checkout；有本地修改时先在原仓库保存提交或备份。本流程不使用 `--force-sync`、`--force-remove-dirty` 或删除工作目录的命令。

这些行为已对照 [Repo 官方 manifest 格式](https://gerrit.googlesource.com/git-repo/+/7bba4ee47e72ccfe7838b62869029e2f7436ce39/docs/manifest-format.md) 和实际解析器验证：缺少旧项目、存在旧项目、相同项目名位于其它路径、ROM 默认 Clang 保留、旧独立 Clang 项目取消。

## 版本和工具链

ROM 构建规则以官方 **LineageOS 23.2** 为基准。内核源码基线来自 LineageOS SM8550 的 **`lineage-21` / Android 13 / Linux 5.15.211 / KMI generation 8**；仓库的发布分支名不代表内核已升级到与 ROM 同代的 Android 内核。上游提交和已核对的 ROM 构建规则提交见 [upstream.lock.json](upstream.lock.json)。

内核编译器使用 LineageOS 平台默认选择。设备树不设置 `TARGET_KERNEL_CLANG_VERSION` 或 `TARGET_KERNEL_CLANG_PATH`，官方规则使用 `LLVM_AOSP_PREBUILTS_VERSION` 与 ROM 自带的 `prebuilts/clang/host/linux-x86`。

本清单不拉取额外 Clang 仓库。保留旧 `prebuilts/clang/host/linux-x86-kernel` 路径的可选 `remove-project`，仅取消旧独立项目声明，不替换 ROM 默认工具链，也不运行本地目录删除命令。

`pinned.xml` 仅锁定上述四个源码项目，不锁定整个 LineageOS 平台或服务器已有 vendor。需要记录一次服务器完整构建输入，可在同步后运行：

```bash
repo manifest -r -o m2468-build-manifest.xml
```

## 已验证内容与功能缺口

- 本地已编译内核与 386 个源码模块，并验证 597 条 ELF 硬依赖边；这不涵盖 DT 供应者、固件、OEM init/sysfs 和启动依赖。
- M2468 的 1 个 DTB、5 个 DTBO 由源码经内核 Kbuild/dtc 构建。DTS 包含从该机原厂 DT 重建的字节属性；这是可构建的重建源码，不是原厂维护的带标签 DTS，也不代表设备语义全部恢复。
- 显示和 Goodix 触控包含针对 Note 的源码适配。HBM 只实现受限亮屏路径；FOD/AOD、黑屏切换及完整指纹联动没有完成运行验证。
- `jiiov_fingerprint` 以及魅族充电、温控、启动和其它 OEM 模块仍有源码缺口。通用高通驱动可编译不等于这些 OEM 功能已恢复。
- 尚未验证完整 ROM 构建、首次启动、分区镜像在真机上的加载和日常功能。已编译的模块数量不能作为整机兼容性结论。

## 来源与许可

内核、外部模块和平台 DTS 基于公开的 LineageOS/QCOM SM8550 仓库；设备树基于 [AstralSpun/android_device_meizu_m2468](https://cnb.cool/AstralSpun/android_device_meizu_m2468)。Note 显示/触控适配是在公开源码上重写兼容接口，参考该型号的 DT 和原厂接口行为；不是恢复出魅族原始 C 源码。各源码仓库保留其上游许可、版权声明和来源记录。

本 manifest 仓库中的清单、脚本和文档使用 Apache-2.0，见 [LICENSE](LICENSE)。这不改变被引用源码、AOSP 工具链或设备固件各自的许可。本组织不再分发设备 dump、闭源固件、用户空间 blobs 或原厂内核二进制。

## 维护发布锁

维护者在四个源码仓库提交完成后生成固定清单，正常服务器构建不需要运行此脚本：

```bash
python3 pin_revisions.py --repos-dir ..
```

该目录需包含表中的四个完整仓库名，且都在干净的 `lineage-23.2` 分支。也可用 `--revisions /path/to/revisions.json` 输入 JSON 对象，四个键为仓库名、值为真实的完整 40 位提交 SHA。发布时先推送源码提交，再发布与之对应的 `pinned.xml` 和 `revisions.lock.json`；不要填入占位 SHA。

可选的 `verify_manifest.py --repo-source /path/to/git-repo` 使用官方 Repo 解析器做离线组合检查，不执行 sync、不修改服务器源码，也不是构建前置步骤。

2026-10-06 音频更新：新增源码 CS35L43 功放模块，并按 Note 原厂接口修正 TX3/TX4 与 secondary MI2S 双功放链路；设备 vendor 加载清单同步更新。公开源码不包含原厂模块或调音固件。新候选须由用户构建并验证，编译/CRC 检查不代表已解决全部启动问题。
