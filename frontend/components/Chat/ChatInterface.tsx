"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";

interface ChatInterfaceProps {
  onSendMessage: (message: string) => void;
  chatHistory: Array<{role: string, content: string}>;
  isLoading?: boolean;
}

export function ChatInterface({ 
  onSendMessage, 
  chatHistory,
  isLoading = false
}: ChatInterfaceProps) {
  const [message, setMessage] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  const suggestedPrompts = [
    "What are the top 5 customers by revenue?",
    "Which customers have the highest quote values?",
    "Show me customer revenue distribution"
  ];

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleSend = () => {
    if (!message.trim()) return;
    onSendMessage(message);
    setMessage("");
  };

  const handlePromptClick = (prompt: string) => {
    setMessage(prompt);
  };

  return (
    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl shadow-lg h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/20">
        <div className="flex items-center gap-2 text-white">
          <Bot className="w-6 h-6" />
          <h2 className="text-xl font-bold">AI Data Analyst Chat</h2>
        </div>
        <p className="text-white/80 text-sm mt-1">Ask questions about your data</p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.length === 0 ? (
          <div className="text-center text-white/60 py-8">
            <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Start a conversation by asking about your data</p>
          </div>
        ) : (
          chatHistory.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="p-2 bg-white/10 rounded-lg">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  msg.role === "user"
                    ? "bg-white text-gray-900"
                    : "bg-white/10 text-white"
                }`}
              >
                <pre className="whitespace-pre-wrap font-sans text-sm">{msg.content}</pre>
              </div>
              {msg.role === "user" && (
                <div className="p-2 bg-white/10 rounded-lg">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="p-2 bg-white/10 rounded-lg">
              <Bot className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div className="bg-white/10 text-white p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>

      {/* Suggested Prompts - Only show if no messages yet */}
      {chatHistory.length === 0 && (
        <div className="p-4 border-t border-white/20">
          <p className="text-white/60 text-xs mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedPrompts.map((prompt, index) => (
              <button
                key={index}
                onClick={() => handlePromptClick(prompt)}
                className="text-xs px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-white/20">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isLoading && handleSend()}
            placeholder="Ask about your data..."
            className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/60 focus:outline-none focus:border-white/40"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !message.trim()}
            className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}