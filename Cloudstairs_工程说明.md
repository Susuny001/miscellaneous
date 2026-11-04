# 云阶 / Cloudstairs

主交付是 **`Cloudstairs_100BPM_Piano.flp`**，可编辑的 FL Studio 工程。

- 固定 100 BPM，4/4，500 小节，编排长度 20:00。
- 全曲一个钢琴乐器通道；主旋律、伴奏、低音均使用同一钢琴。
- 三个原创主题：窗边的回声、未寄出的信、越过云沿，配有变奏、连接与尾声。
- 09:16.800 开始逐步抬升音区，09:55.200 进入高音主题。
- 所有音乐音符重新创作；参考用于钢琴音色与分解和弦、短音型、应答等写法，没有把参考的旋律段落搬进工程。

## 打开工程

使用 FL Studio 25.1.5 或兼容的新版本打开 `.flp`，在 Song 模式播放完整 Playlist。工程包含 19 个已命名的 Pattern，可直接进入 Piano roll 修改。

音色保留上传参考工程中的 **FLEX → Austrian Grand Piano by UVI → Basic Soft**。需要本机安装相应 FLEX 音色库；工程中保存的是插件预设状态，不包含厂商采样库。若缺少该库，请先通过 FL Studio/FLEX 安装已有参考使用的音色库。

| 段落 | 完整编排中的起点 | 独立 MIDI |
| --- | --- | --- |
| 窗边的回声 | 00:19.200 | `Cloudstairs_100BPM_Piano_Theme_A.mid` |
| 未寄出的信 | 04:48.000 | `Cloudstairs_100BPM_Piano_Theme_B.mid` |
| 越过云沿 | 09:55.200 | `Cloudstairs_100BPM_Piano_Theme_C_High.mid` |

`Cloudstairs_100BPM_Piano.mid` 是完整编排的通用备份。MIDI 不携带 FLEX 音色，主交付仍是 `.flp`。

## 已完成的检查

工程包含 6,923 个音符、19 个连续且无空缺的 Playlist 片段和一个 FLEX 钢琴通道；所有音高、起点、长度与力度均与 `Cloudstairs_score.json` 逐项核对。100 BPM 下总编排为 1,200 秒。相同琴键没有重叠触发，重新生成工程不会累积重复元数据。

对本次提供的参考进行了主旋律连续音高比对，未发现连续六个及以上音高相同的片段。这只是针对该参考的局部比对，不代表对所有既有音乐的检索。

当前云环境未安装 FL Studio。上述检查是文件结构、独立解码器和音符数据检查，**尚未在 FL Studio 界面实际打开或调用 FLEX 试听验证**。离线钢琴渲染已完成，但它使用 FluidR3 的 Acoustic Grand Piano，不能作为 FLEX 原音色的实机验证。

## 可复现源文件

`compose_cloudstairs.py` 保存三个主题与完整编排规则；`Cloudstairs_score.json` 保存本版全部音符。生成 MIDI 需要 Python 3 和 `mido==1.3.3`。在仓库根目录运行：

```sh
python3 compose_cloudstairs.py
```

该命令会重建同名工程、MIDI 和乐谱数据；若已经手工编辑工程，请先备份，或使用 `--out` 指向其他目录并用 `--template` 指定本工程。脚本只复用模板中的钢琴预设和非音乐配置，不导入模板的音符。

如需自行离线渲染，额外安装 numpy、soundfile、pyfluidsynth 和系统 libfluidsynth，传入 `--soundfont /path/to/FluidR3_GM.sf2 --render /path/to/output.wav`。FluidR3 由 Frank Wen 等制作，采用 MIT 许可；仓库未附带该采样库。
