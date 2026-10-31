# WARM CORRIDOR · DELUXE v3 MUSIC

320 米 / 32 段 / 96 盏精细圆灯。包含原创模块化模型、9 张 1024px PBR 贴图、7 份原创环境音效与 1 首原创立体声配乐、灯光过渡、第一人称玩家、示例场景与全部 C# / Shader 源码。

## 先运行

1. 在 Unity 使用 Assets → Import Package → Custom Package 导入 `WarmCorridor_Deluxe_v3_Music.unitypackage`，勾选全部资源。
2. 打开 `Assets/WarmCorridor/Scenes/WarmCorridorDemo.unity`，点击 Play。走廊在运行时生成，编辑视图暂时没有走廊是正常的。
3. WASD / 方向键移动，鼠标转视角，Shift 冲刺，Space 跳跃，Esc 释放鼠标，点击画面恢复，R 重启。
4. 若要在 Play 前逐个编辑模型，选 Tools → Warm Corridor → Create Editable Demo Scene。它保存新场景，不覆盖原示例。

从 v1 升级时，本包会更新相同 `Assets/WarmCorridor` 路径；先备份自己修改过的文件。请打开更新后的示例场景，旧的自行保存场景可能仍保留旧序列化参数；旧 Editable 场景建议重新生成。自己的关卡物体请放在 GeneratedWorld 之外，重建按钮会替换该节点。

按 Unity 2021.3+ API 编写，面向 Built-in / URP，推荐 Unity 2022.3 LTS 或 Unity 6。没有 HDRP 专用实现；新 Input System 和旧 Input Manager 均支持，无需额外 Input Actions、Cinemachine、VFX Graph 或商店资源。

## 视觉与氛围

- 石材地砖的真实倒角与分缝、上下分色墙板、阴缝、铜色细压条、吊顶板、通风格栅、带螺钉的检修盖。
- 圆灯具有分层金属壳、精细倒角、铜色嵌圈、螺钉和独立发光面；不再只用一个圆柱体代表整盏灯。
- 原创地面、墙面、墙板、吊顶 Albedo / Normal 贴图，地面附 Metallic / Smoothness 遮罩；模型有 UV 和明确法线。
- 琥珀预热渐变到暖黄色，独立的灯罩发光、柔光晕与低强度光柱；所有效果跟随相同亮度包络。
- 只在玩家附近生成少量漂浮微尘，并随当前段亮度改变可见度；远处使用暗色距离雾。
- 部分灯投射柔阴影；远处阴影和真实灯光渐渐淡出，避免硬切。
- 无缝通风底噪、四种石地脚步、轻微点亮 / 熄灭声。脚步按实际移动距离且落地状态触发，撞墙和传送不会疯狂补播。
- 极简角落文字和细进度线，操作提示自动淡去，不用大块 HUD 遮住走廊。

光晕和光柱使用深度测试的加法 Shader 近似柔光散射，不是物理体积雾，也不依赖后处理 Bloom。若目标项目已有后处理，可自行叠加轻量 Bloom；先降低本包 haloIntensity，避免叠加过曝。

## 配乐：《灯醒之前》 / Before the Light

新增原创 128 秒立体声 ambient 循环。八组缓慢和弦、温暖的持续音色、稀疏柔音键盘、低频支撑和长混响，没有鼓组或人声。音符与混响尾音循环衔接，适合反复行走；单独 WAV 是可循环母带，MP3 仅供试听。

示例场景和完整 Rig 预制体已添加 CorridorMusicPlayer，Play 后音乐会用 5 秒淡入。音乐是独立的 2D 立体声声部，不占用脚步 / 开关灯的空间音源池，也不替代通风环境声。

| CorridorMusicPlayer 参数 | 作用 |
| --- | --- |
| playMusic / musicClip | 音乐开关 / 换成自己的配乐 |
| useIncludedMusic | 自动加载附带原创 WAV |
| musicVolume | 默认 0.28，降低以给脚步和灯声留空间 |
| fadeInSeconds / fadeOutSeconds | 默认 5 秒淡入 / 3 秒淡出 |
| loop | 默认循环；关闭后只播放一次 |
| followSoundscapeMasterVolume | 默认跟随 Soundscape 总音量 |
| muteWhenUnfocused / pauseWithGame | 失焦或游戏暂停时淡出并暂停，恢复后继续当前位置 |
| fadeWhenCursorReleased | 可选 Esc 释放鼠标时淡出；默认不启用 |

音乐源 WAV 为立体声 PCM，导入时不合并为单声道，并采用 Streaming 加载。`Resources/WarmCorridor/Audio/CorridorAmbientMusic.wav` 可在其他场景单独使用；若已有旧版 Editable 场景，只需在系统根物体添加 CorridorMusicPlayer，不必重建模型。右键组件的 Restart Music 可从头淡入。

## 灯光如何缓开缓关

默认玩家走到本地 Z=5.8 米时，下一段（10–20 米）所有灯**同时开始**点亮；之后每隔 10 米触发下一段。提前距离为 4.2 米。

默认渐亮 1.4 秒，渐暗 2.6 秒，采用可编辑 S 曲线，并有短响应平滑。灯先呈较暗琥珀色，再过渡到稳定暖黄；中途回头、重新激活时，从当前亮度继续，不跳到全黑或全亮。第一段在开场也渐亮。

默认 `keepPassedSegmentsLit=false`：离开某段感应范围后等待 6 秒，再缓缓熄灭。往回走会重新感应；下一段仍提前开始亮。开启 `keepPassedSegmentsLit` 可让走过的段持续亮。

实际灯光只渲染玩家附近的区域，距离裁剪也经过空间与时间淡化；已点亮的远处灯罩仍保留发光面。轻微呼吸变化只有约 0.8%，不是闪烁灯，设为 0 可完全关闭。

## 公开参数在哪里调

主物体 `Warm Corridor - DELUXE music settings` 上：

| 组件 / 字段 | 默认 / 作用 |
| --- | --- |
| WarmCorridorDemo.segmentCount / segmentLength | 32 段 × 10 米，可调 2–200 段 |
| corridorWidth / corridorHeight | 4.2 / 3.2 米 |
| lightsPerSegment / lampRadius | 每段 3 灯，半径 0.22 米 |
| activateAheadDistance | 提前 4.2 米感应 |
| fadeInSeconds / fadeOutSeconds | 渐亮 1.4 秒 / 渐暗 2.6 秒 |
| fadeInCurve / fadeOutCurve | Inspector 内可直接编辑亮度曲线 |
| fadeFirstSectionOnStart | 开场第一段也渐亮 |
| keepPassedSegmentsLit / turnOffDelay | 默认不永久保留，离开后等待 6 秒 |
| warmUpColor / warmColor / colorWarmUp | 预热琥珀色、稳定暖黄色、色彩预热开关 |
| lightIntensity / lightRange / lensEmission | 强度 3.2 / 范围 7.5 米 / 灯罩发光 3 |
| addSoftHalos / haloRadius / haloIntensity | 柔光开关 / 半径 0.55 米 / 强度 0.22 |
| addLightShafts / shaftLength / shaftBottomRadius | 散射近似开关 / 长度 1.65 米 / 底部半径 0.7 米 |
| shaftIntensity | 光柱强度 0.012，建议保持很低 |
| breathingAmount | 微弱亮度呼吸 0.008；0 为完全稳定 |
| maxLightRenderDistance / lightDistanceFadeBand | 灯光距离 28 米 / 边缘 6 米渐隐 |
| maxShadowRenderDistance / shadowEveryNthLight | 阴影距离 14 米 / 每 3 个真实灯投影一个 |
| lightShadows / lightEveryNthFixture | Soft 柔阴影；设 None 可减负 / 灯的真实光源间隔 |
| ambientColor / fogColor / enableFog / fogDensity | 暗部、雾色、距离雾开关与浓度 |
| panelMaterial / brassMaterial 等 | 单独替换墙板、铜件、地面等材质 |
| useDetailedSurfaceTextures | 是否将附带 PBR 贴图应用于主材质 |
| CorridorAtmosphere | 微尘开关、数量、大小、漂移、亮度、颜色 |
| CorridorSoundscape | 总音量、通风 / 脚步 / 开关音量、步距、音源池、空间范围、替换自己的 AudioClip |
| CorridorHUD | UI、准星、操作提示、感应提示开关，操作提示显示时长 |

玩家子物体 `First Person Player - settings`：FirstPersonWalker 可调走路 / 冲刺速度、加速度、跳跃、重力、眼高、FOV、灵敏度、身体碰撞体和走路晃动。新输入系统使用 mouseSensitivity，旧输入使用 legacyMouseSensitivity。

几何、灯数、模型、光晕半径 / 光柱形状更改后，用主组件底部 Build / Rebuild Corridor 重建，或勾选 rebuildOnPlay 后重新进入 Play。感应、颜色、亮度、曲线、延迟、柔光强度可在 Play 实时调。音源池数量和部分粒子初始化参数在下次进入 Play 生效。

Play 里的临时参数不会自动保存，退出后重新填写需要保留的值。重建会移除 GeneratedWorld 中的手工修改；自己的物体请放在其外。所有系统根节点请保持缩放 (1,1,1)。

## 在自己的项目复用

- `Prefabs/WarmCorridorRig.prefab` 是完整系统，已含玩家和相机；拖入空场景即可。不要再放重复的玩家、相机和 Audio Listener。
- `Prefabs/FirstPersonPlayer.prefab` 可单独使用。
- `Resources/WarmCorridor` 有两份原创 OBJ、MTL、纹理、声音和保证 Shader 构建引用的柔光材质。
- 自定义模块原生尺寸约定：宽 4.2、高 3.2、长 10 米，段首地面中心为原点，沿 +Z；圆灯直径 0.4、厚 0.1 米，发光面朝 -Y。
- 已有场景中的太阳光、过亮的环境光和其他相机会改变效果，请先在本包独立示例中验收。

创建独立游戏前，先用菜单生成并保存 Editable 场景，将其加入 Build Settings / Build Profiles。编辑器会把生成的材质和光柱网格保存为资产，避免重开后失去临时资源；不要仅在 Play 中生成后直接退出保存。

切换 Built-in / URP 后，如旧材质变粉，清空主组件旧材质引用再重建，或重新生成 Editable 场景。URP 推荐 Forward+；Forward 可提高 Additional Lights 的 Per Object Limit。低性能设备可先关闭 lightShadows 和 addLightShafts、降低 maxLightRenderDistance / particlesPerSecond，或把 lightEveryNthFixture 设为 2。原始高精度模型仍保留。

## 验证边界

已检查 C# 编译、曲线包络与感应联动、模型完整性、音频格式 / 接缝、纹理与资源引用、unitypackage 结构。编译与运行逻辑检查使用明确的 Unity API 测试替身；过渡数值类还直接编译运行验证多帧率渐变与反转连续性。

制作环境没有 Unity Editor，所以尚未声称真实 Unity 导入、Shader 编译、物理、渲染、性能或最终构建已通过。请在目标 Unity 项目中先运行示例。附带的模型预览由 Blender 渲染，不是 Unity 实机截图。

本包模型、贴图、声音与代码均为本次原创制作，可在自己的 Unity 项目中使用、修改。
