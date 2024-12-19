import React, { useEffect, useReducer, useRef } from "react";
import { Message } from "../types/chat";
import { streamChat } from "../utils/api";
import ChatMessage from "./ChatMessage";
import MessageInput from "./MessageInput";

type ChatState = {
  messages: Message[];
  isLoading: boolean;
};

type ChatAction =
  | { type: "ADD_MESSAGE"; payload: Message }
  | { type: "UPDATE_LAST_MESSAGE"; payload: string }
  | { type: "SET_LOADING"; payload: boolean };

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case "ADD_MESSAGE":
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };
    case "UPDATE_LAST_MESSAGE":
      return {
        ...state,
        messages: state.messages.map((msg, index) =>
          index === state.messages.length - 1
            ? { ...msg, content: msg.content + action.payload }
            : msg
        ),
      };
    case "SET_LOADING":
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

const Chat: React.FC = () => {
  const [state, dispatch] = useReducer(chatReducer, {
    messages: [],
    isLoading: false,
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

  const handleSend = async (content: string) => {
    const userMessage: Message = { role: "user", content };
    dispatch({ type: "ADD_MESSAGE", payload: userMessage });
    dispatch({ type: "SET_LOADING", payload: true });

    const assistantMessage: Message = { role: "assistant", content: "" };
    dispatch({ type: "ADD_MESSAGE", payload: assistantMessage });

    try {
      await streamChat([userMessage], (chunk) => {
        dispatch({ type: "UPDATE_LAST_MESSAGE", payload: chunk });
      });
    } catch (error) {
      console.error("Error in chat:", error);
    } finally {
      dispatch({ type: "SET_LOADING", payload: false });
    }
  };

  return (
    <div className="flex h-screen flex-col">
      <div className="flex-1 overflow-y-auto p-4">
        {state.messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t p-4">
        <MessageInput onSend={handleSend} disabled={state.isLoading} />
      </div>
    </div>
  );
};

export default Chat;
