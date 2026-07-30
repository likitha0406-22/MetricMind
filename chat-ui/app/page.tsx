"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm your AI assistant.",
    },
  ]);

  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input,
    };

    const botMessage: Message = {
      role: "assistant",
      content: "This will be replaced with LangChain later.",
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
    setInput("");
  };

  return (
    <main className="min-h-screen bg-gray-100 text-black flex flex-col">
      <h1 className="text-3xl font-bold text-center text-gray-900 py-5">
        MetricMind AI Chat
      </h1>

      <div className="flex-1 overflow-y-auto p-5">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex mb-4 ${
              msg.role === "user"
                ? "justify-end"
                : "justify-start"
            }`}
          >
            <div
              className={`max-w-[70%] px-4 py-3 rounded-2xl shadow ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-black"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t bg-white p-4 flex gap-3">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage();
            }
          }}
        />

        <button
          onClick={sendMessage}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-xl"
        >
          Send
        </button>
      </div>
    </main>
  );
}