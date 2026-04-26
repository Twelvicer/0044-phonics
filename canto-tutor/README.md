# canto-tutor

用于把粤语歌曲歌词按字切分、转注音、生成单字音频并按节奏对齐的基础工程脚手架。

## 目录结构

- `input/`: 输入文件（歌词、原曲、时间戳）
- `output/char_audio/`: TTS 单字原始音频输出目录
- `output/char_audio_stretched/`: 拉伸/对齐后的音频输出目录
- `utils/`: 各子模块（注音、TTS、节拍分析、对齐、音频处理、字典）
- `pipeline.py`: 主流程与 CLI 入口

## 使用

在 `canto-tutor/` 目录下运行：

```bash
python pipeline.py
```

当前为第一版 stub，可在各 `utils/*.py` 中逐步补全实现。
