# Phonics Pipeline

本项目用于歌词到逐字音频（含节拍与对齐信息）的处理流程。

## 统一日志输出

项目已在 `pipeline.py` 与 `utils/*.py` 采用统一日志格式（`logging` + `tqdm`），重点输出：

- 合成进度（例如：`正在合成第 15/200 个字...`）
- Beat 分析结果（BPM、beat 数量）
- 每句对齐与变速统计（目标时长、实际时长、变速比）

示例：

```bash
python pipeline.py
```

---

## Demo 验收（《海阔天空》前 4 句）

### 1) 样例输入

请在输入歌词文件中放入以下 4 句（按行）：

```text
今天我寒夜里看雪飘过
怀着冷却了的心窝飘远方
风雨里追赶雾里分不清影踪
天空海阔你与我可会变
```

### 2) 执行命令示例

```bash
python pipeline.py \
  --input demo/hktk_4lines.txt \
  --output demo/out \
  --char-data demo/out/char_data.json
```

> 若你当前版本尚未实现这些 CLI 参数，可先使用项目既有入口命令，只要能产出 `char_data.json` 与最终音频即可。

### 3) 用 Audacity 对照 `char_data.json` 时间戳

1. 打开 Audacity，导入输出音频（如 `demo/out/final.wav`）。
2. 打开 `char_data.json`，找到每个字的 `start` / `end` 时间（单位通常为秒）。
3. 在 Audacity 时间轴输入对应时间点，观察波形起始/结束位置是否与字音一致。
4. 重点抽查每句首尾字与快慢变化明显的字，记录偏差（建议阈值 ±80ms）。
5. 若偏差系统性提前/滞后，回看日志中的句级 `speed_ratio` 与 Beat 分析结果。

### 4) words.hk 查询“爱”的示例输出（文本）

可在验收记录中附上如下示例文本：

```text
查询词：爱
拼音（示例）：oi3
释义（示例）：喜爱；对人或事物有深厚感情
来源：words.hk 查询页面（人工核对）
```

> 如需截图，请在浏览器打开 words.hk 的“爱”词条页面并保存到 `docs/demo/words-hk-ai.png`，再在 README 中补上图片链接。
