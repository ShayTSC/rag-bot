import React from "react";
import { Message } from "../types/chat";

interface Props {
  message: Message;
}

const ChatMessage: React.FC<Props> = ({ message }) => {
  return (
    <div
      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          message.role === "user"
            ? "bg-blue-500 text-white"
            : "bg-gray-200 text-gray-800"
        }`}
      >
        <p className={`whitespace-pre-wrap ${message.content || 'animate-bounce'}`}>{message.content || "Thinking..."}</p>
      </div>
    </div>
  );
};

export default ChatMessage;
