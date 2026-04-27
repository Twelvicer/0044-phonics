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

## 当前 TTS 接入现状

- 已支持 `qwen3-tts-flash-realtime`（DashScope Python SDK，commit 模式）与本地 `placeholder` 回退模式。
- 若选择 `qwen3-tts-flash-realtime`，会在启动时询问男声/女声并映射为固定音色：
  - `male -> Rocky`
  - `female -> kiki`
- 其余音色不使用。

### 运行示例（Qwen Realtime）

```bash
export DASHSCOPE_API_KEY="<your_api_key>"
# 默认走中国内地（北京）线路
python pipeline.py --tts-provider qwen3-tts-flash-realtime
```

或显式传入：

```bash
python pipeline.py --tts-provider qwen3-tts-flash-realtime --dashscope-api-key "<your_api_key>" --voice-gender male
```

如需新加坡线路，可覆盖 websocket 地址：

```bash
python pipeline.py --tts-provider qwen3-tts-flash-realtime --dashscope-url "wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime"
```


### 无法安装 Python SDK 时：Java 无依赖 WebSocket Demo

如果当前环境无法安装 `dashscope`（例如网络代理限制），可以先用 Java 25+ 的内置 WebSocket 试跑：

```bash
cd canto-tutor
javac tools/QwenRealtimeWsDemo.java
java -cp tools QwenRealtimeWsDemo "$DASHSCOPE_API_KEY" "你好，欢迎使用实时语音。" kiki output/demo.pcm
```

> 说明：示例从环境变量读取 Key，README 不写入任何明文 key。
