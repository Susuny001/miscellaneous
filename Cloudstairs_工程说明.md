# 三段钢琴旋律——待本机验收草稿

此前提交 `1710e50` 的 20 分钟长编排不符合要求，且已被反馈打开时卡死，不能视为可用成品。本次修复候选按用户要求提交，供本机检查，尚未在 FL Studio 中实机验收。

“19–20 分钟”是创作与修整的用时要求，不是歌曲长度。本次按上传参考中的短段落形式重做：三段独立旋律，每段 8 小节，100 BPM，每段 19.2 秒；Playlist 顺次放置三段，仅为方便浏览，合计 57.6 秒。

| Pattern | 名称 | 调性 | 中段处理 |
| --- | --- | --- | --- |
| 1 | 窗影 | 降 D 大调 | 第 4 小节向上连接，第 5 小节进入高音应答 |
| 2 | 折线 | B 小调 | 第 4 小节逐级上行，第 5 小节转入高音区 |
| 3 | 晴隙 | C 大调 | 中段抬升音区，后段以三连音发展 |

右手以连续十六分音符、分解和弦音型和短句应答为主，左手使用持续低音与和弦支撑，参考上传工程的写法。三个段落的主旋律逐音写出，没有随机音高、随机和声或自动延长编排。局部连续音高比对未发现与所给参考相同的连续八音片段；这不替代听感判断，也不代表对全部既有音乐的检索。

## 工程候选文件

- `Cloudstairs_100BPM_Piano.flp`：保留上传参考的 FLEX / Austrian Grand Piano by UVI / Basic Soft 钢琴预设。
- `Cloudstairs_100BPM_Piano_FLKeys.flp`：用于排查加载问题的内置 FL Keys 版本，不加载 FLEX，不依赖外部采样路径。

两份工程都保留原始 FL Studio 25.1.5 工程的文件头、通道编号、初始化记录以及混音器等非音乐结构。每份仅启用一个钢琴通道，其余槽位禁用；兼容版将其余槽位替换为空 Sampler，不加载其他乐器。旧写入器对原结构的删减、通道重编号和自定义 Pattern 长度写入已移除。

当前仅完成了数据检查：三个 Pattern、三个 Playlist 片段、470 个音符、钢琴通道与预设、完整原始初始化记录、音符与 MIDI 的一致性，以及无卡键事件。当前环境没有 FL Studio，原生加载和实际音色播放仍待本机验证。因此这些文件是修复候选，不能把上述检查描述成“已确认能在 FL Studio 打开”。

配套 MIDI 是通用备份：`Cloudstairs_100BPM_Piano.mid` 包含三段；三个 `Theme_*.mid` 分别保存单段。主交付目标仍是 FLP。

## 源文件

`compose_cloudstairs.py` 保存逐音写明的三个旋律与和声；`Cloudstairs_score.json` 保存当前乐谱事件；`repair_cloudstairs_flp.py` 将这些音符写入完整的原始工程结构。重新生成需要 Python 3、mido 及完整模板：

```sh
python3 compose_cloudstairs.py --template /path/to/original_reference.flp
python3 repair_cloudstairs_flp.py --source /path/to/original_reference.flp
```

第二条命令同时生成原音色版与 FL Keys 兼容版。不会从模板导入原旋律。旧的单通道长曲工程会被拒绝作为模板；运行前请备份自行修改过的同名输出文件。

离线试听草稿采用 FluidR3 Acoustic Grand Piano 渲染，仅帮助判断音符与段落，不是 FLEX 原音色的实机录音。
