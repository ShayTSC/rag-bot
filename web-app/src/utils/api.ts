import { Message } from "../types/chat";

const API_URL = "http://localhost:8000";
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

export async function streamChat(
  messages: Message[],
  onChunk: (chunk: string) => void
): Promise<void> {
  const response = await fetch(`${API_URL}/v1/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_TOKEN}`,
    },
    body: JSON.stringify({
      messages,
      stream: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Response body is null");
  }

  const reader = response.body.getReader();

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;
    if (!value) throw new Error("Response body value is null");

    const text = new TextDecoder().decode(value);
    const lines = text.split("\n");

    console.log(text);

    for (let i = 0; i < lines.length; i++) {
      try {
        const line = lines[i];

        if (line.startsWith("data: ")) {
          const payload = JSON.parse(line.slice(5));
          if (payload.choices?.[0]?.finish_reason === "stop") {
            continue;
          }
          const chunk = payload.choices?.[0]?.delta?.content;
          if (chunk) {
            if (chunk !== "\n") onChunk(chunk);
          }
        }
      } catch (error) {
        console.error("Error parsing line:", error);
      }
    }
  }
}
