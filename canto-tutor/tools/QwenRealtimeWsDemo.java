import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.WebSocket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Base64;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.CountDownLatch;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * No-SDK demo for qwen3-tts-flash-realtime using Java WebSocket.
 *
 * Usage:
 *   javac tools/QwenRealtimeWsDemo.java
 *   java -cp tools QwenRealtimeWsDemo "$DASHSCOPE_API_KEY" "你好，欢迎使用实时语音。" kiki out.pcm
 */
public class QwenRealtimeWsDemo {
    private static final Pattern TYPE_PATTERN = Pattern.compile("\\\"type\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"");
    private static final Pattern DELTA_PATTERN = Pattern.compile("\\\"delta\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"");

    private static String extract(Pattern pattern, String text) {
        Matcher m = pattern.matcher(text);
        return m.find() ? m.group(1) : "";
    }

    private static String jsonEscape(String value) {
        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: java QwenRealtimeWsDemo <api_key> <text> [voice] [output_pcm] [url] [model]");
            System.exit(1);
        }

        String apiKey = args[0];
        String text = args[1];
        String voice = args.length >= 3 ? args[2] : "kiki";
        Path outputPath = Path.of(args.length >= 4 ? args[3] : "out.pcm");
        String url = args.length >= 5 ? args[4] : "wss://dashscope.aliyuncs.com/api-ws/v1/realtime";
        String model = args.length >= 6 ? args[5] : "qwen3-tts-flash-realtime";

        Path parent = outputPath.toAbsolutePath().getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        var audioBuffer = new java.io.ByteArrayOutputStream();
        var done = new CountDownLatch(1);

        WebSocket.Listener listener = new WebSocket.Listener() {
            @Override
            public void onOpen(WebSocket webSocket) {
                String sessionUpdate = "{" +
                        "\\\"type\\\":\\\"session.update\\\"," +
                        "\\\"session\\\":{" +
                        "\\\"voice\\\":\\\"" + jsonEscape(voice) + "\\\"," +
                        "\\\"response_format\\\":\\\"pcm_24000hz_mono_16bit\\\"," +
                        "\\\"mode\\\":\\\"commit\\\"" +
                        "}" +
                        "}";
                String appendText = "{" +
                        "\\\"type\\\":\\\"input_text_buffer.append\\\"," +
                        "\\\"text\\\":\\\"" + jsonEscape(text) + "\\\"" +
                        "}";
                String commit = "{\\\"type\\\":\\\"input_text_buffer.commit\\\"}";

                webSocket.sendText(sessionUpdate, true);
                webSocket.sendText(appendText, true);
                webSocket.sendText(commit, true);
                webSocket.request(1);
            }

            @Override
            public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
                String message = data.toString();
                String type = extract(TYPE_PATTERN, message);

                if ("response.audio.delta".equals(type)) {
                    String delta = extract(DELTA_PATTERN, message);
                    if (!delta.isEmpty()) {
                        byte[] pcm = Base64.getDecoder().decode(delta);
                        audioBuffer.writeBytes(pcm);
                    }
                }

                if ("response.done".equals(type) || "session.finished".equals(type)) {
                    done.countDown();
                    webSocket.sendClose(WebSocket.NORMAL_CLOSURE, "done");
                } else {
                    webSocket.request(1);
                }
                return CompletableFuture.completedFuture(null);
            }

            @Override
            public void onError(WebSocket webSocket, Throwable error) {
                error.printStackTrace();
                done.countDown();
            }
        };

        HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
        client.newWebSocketBuilder()
                .header("Authorization", "Bearer " + apiKey)
                .header("X-DashScope-DataInspection", "enable")
                .header("X-DashScope-Model", model)
                .buildAsync(URI.create(url), listener)
                .join();

        done.await();
        Files.write(outputPath, audioBuffer.toByteArray());
        System.out.println("Saved PCM to: " + outputPath.toAbsolutePath());
    }
}
