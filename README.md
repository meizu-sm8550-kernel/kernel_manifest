# meizu-sm8550-kernel

**当前仅支持 m2468（魅族 21 Note）**，平台为 Qualcomm SM8550 / Kalama。`sm8550` 是平台名称，不表示已适配其它魅族 SM8550 设备；M2481（魅族 21 Pro）不在此项目支持范围内。

本仓库提供 Android 源码树的本地清单，统一同步设备配置、内核、外置驱动和设备树源码。源码分支为 `lineage-23.2`，内核基线为 Android 13 / Linux 5.15.211 / KMI generation 8。源码分支名与内核版本分别管理。

## 仓库布局

| 仓库 | ROM 源码树路径 |
| --- | --- |
| [android_kernel_meizu_sm8550](https://github.com/meizu-sm8550-kernel/android_kernel_meizu_sm8550) | `kernel/meizu/sm8550` |
| [android_kernel_meizu_sm8550-modules](https://github.com/meizu-sm8550-kernel/android_kernel_meizu_sm8550-modules) | `kernel/meizu/sm8550-modules` |
| [android_kernel_meizu_sm8550-devicetrees](https://github.com/meizu-sm8550-kernel/android_kernel_meizu_sm8550-devicetrees) | `kernel/meizu/sm8550-devicetrees` |
| [android_device_meizu_m2468](https://github.com/meizu-sm8550-kernel/android_device_meizu_m2468) | `device/meizu/m2468` |

组织不提供设备 dump、闭源固件、用户空间 blobs 或原厂内核二进制。构建仍需配套 ROM 源码及已有的 `vendor/meizu/m2468` 等依赖。

## 同步和构建

在已有的 LineageOS 23.2 源码树根目录安装清单：

```bash
mkdir -p .repo/local_manifests
curl -fL https://raw.githubusercontent.com/meizu-sm8550-kernel/kernel_manifest/lineage-23.2/local_manifest.xml \
  -o .repo/local_manifests/zzzz-meizu-m2468.xml
repo sync -c -j8

source build/envsetup.sh
breakfast m2468 userdebug
mka kernel dtboimage bootimage vendorbootimage vendor_dlkmimage system_dlkmimage
```

构建完整 ROM 使用同一已选择的产品执行 `mka bacon`。默认产物目录为 `out/target/product/m2468/`，自定义 `OUT_DIR` 时以 `$OUT` 为准。内核沿用 ROM 默认 Clang，不设置设备专用 Clang 版本，也不额外同步编译器。

这些是已有构建入口；本地未完成整 ROM 编译验证。此前用户设备运行的是 LineageOS 24.0 / Android 17，不应据此声称验证了官方 LineageOS 23.2 整 ROM。

## 清单行为

`local_manifest.xml` 通过专用 remote 跟随 `refs/heads/lineage-23.2`。四个 project 不固定 SHA，不继承 ROM 主清单的分支，也不包含 `remove-project`。

`pinned.xml` 是同内容的兼容入口，名称虽保留，当前也跟随分支。两个入口只安装其中一个。相同源码路径应只声明一次；其它清单重复声明时需先整理冲突。

[revisions.lock.json](revisions.lock.json) 记录发布时的四个源码 SHA，仅用于追溯，不控制 `repo sync`。需要记录某次实际构建输入，可在同步后执行：

```bash
repo manifest -r -o m2468-build-manifest.xml
```

## 适配与验证范围

适配包含设备 DT、PM8008 供电、电源键复位预警、振动、显示与背光、Goodix 触控、CS35L43、JIIOV、闪光灯及 WLAN 配套修改。已有启动和部分外设的用户反馈；这不代表全部场景和外设均验证通过。

本次提交整理保持既有功能，主机回归覆盖背光、触控、振动和指纹，清单使用真实 Repo 解析器检查。完整 AOD、各显示模式、音频及其它 OEM 行为仍需分别进行设备验证。此前各轮结果与限制保存在 [历史记录](docs/m2468-bringup-history.md)，上游来源见 [upstream.lock.json](upstream.lock.json)。

包含坐标缩放的 Goodix 驱动要求 ROM 移除旧 inputflinger 除以 10 的补丁，避免重复缩放。原补丁文件名 `0001-Fix-touch-on-Meizu-21-Note.patch` 仅作为历史引用保留。

## 提交和设备命名

设备路径、配置和新代码使用 `m2468` / `M2468`，提交按子系统组织，标题使用首字母大写的动作描述，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

2026-10-10 已重整下游适配历史，旧新提交对应关系见 [commit map](history/2026-10-10-commit-map.json)。五个仓库均保留 `archive/m2468-before-cleanup-20261010` 恢复分支。上游提交未重写。

已有源码 checkout 的提交号会改变。如果同步报告历史分叉，先保存自己的提交和未提交修改，再将本地分支迁移到新的 `origin/lineage-23.2`；不要将旧适配系列合并回新历史。本次没有修改 XML 内容，无需重新下载清单。

## 维护审计记录

源码发布后，维护者可执行 `python3 pin_revisions.py --repos-dir ..`；该目录应包含四个完整仓库名，且位于干净的 `lineage-23.2` 分支。也可用 `--revisions /path/to/revisions.json` 提供仓库名到完整 SHA 的对象。

`python3 verify_manifest.py --repo-source /path/to/git-repo` 使用官方 Repo 解析器执行离线组合检查。它不执行同步，也不是正常构建的前置步骤。

清单、脚本和本仓库文档采用 [Apache-2.0](LICENSE)；各源码仓库保留上游许可和版权声明。
