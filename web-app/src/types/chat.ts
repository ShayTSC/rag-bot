export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  choices: {
    delta?: {
      content?: string;
    };
    message?: {
      role: string;
      content: string;
    };
    finish_reason: string | null;
  }[];
}
