"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Lightbulb, History, ChevronDown } from "lucide-react";

interface ChatInterfaceProps {
  onSendMessage: (message: string) => void;
  chatHistory: Array<{role: string, content: string}>;
  isLoading?: boolean;
  queryHistory?: string[];
}

export function ChatInterface({ 
  onSendMessage, 
  chatHistory,
  isLoading = false,
  queryHistory = []
}: ChatInterfaceProps) {
  const [message, setMessage] = useState("");
  const [showExamples, setShowExamples] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const exampleQueries = [
    {
      category: "Sales Analysis",
      queries: [
        "What are the top 5 customers by revenue?",
        "Show monthly sales trends for this year",
        "What is the average order value by status?",
        "Show sales distribution by city"
      ]
    },
    {
      category: "Product Analysis",
      queries: [
        "Which products generate the most revenue?",
        "Show top 10 products by quantity sold",
        "What is the product distribution by type?",
        "Show product sales trends over time"
      ]
    },
    {
      category: "Customer Insights",
      queries: [
        "Show customer distribution by country",
        "Who are the most active customers?",
        "What is the customer retention rate?",
        "Show new customers by month"
      ]
    }
  ];

  const suggestedPrompts: string[] = [];

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
    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl shadow-lg h-[calc(100vh-120px)] max-h-[calc(100vh-120px)] min-h-[500px] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/20 flex-shrink-0">
        <div className="flex items-center gap-2 text-white">
          <Bot className="w-6 h-6" />
          <h2 className="text-xl font-bold">AI Data Analyst Chat</h2>
        </div>
        <p className="text-white/80 text-sm mt-1">Ask questions about your data</p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
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
        <div className="p-4 border-t border-white/20 flex-shrink-0">
          <p className="text-white/60 text-xs mb-3">Try asking:</p>
          
          {/* Example Queries Button */}
          <div className="mb-3">
            <button
              onClick={() => {
                setShowExamples(!showExamples);
              }}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors"
            >
              <Lightbulb size={14} />
              <span>Example Queries</span>
              <ChevronDown size={12} className={`transform transition-transform ${showExamples ? 'rotate-180' : ''}`} />
            </button>
          </div>

          {/* Example Queries Dropdown */}
          {showExamples && (
            <div className="mb-3 bg-white/5 rounded-lg p-2 max-h-48 overflow-y-auto">
              {exampleQueries.map((category) => (
                <div key={category.category} className="mb-2">
                  <button
                    onClick={() => setSelectedCategory(
                      selectedCategory === category.category ? null : category.category
                    )}
                    className="w-full text-left px-2 py-1 text-xs font-semibold text-white/80 hover:text-white flex items-center justify-between"
                  >
                    <span>{category.category}</span>
                    <ChevronDown size={10} className={`transform transition-transform ${
                      selectedCategory === category.category ? 'rotate-180' : ''
                    }`} />
                  </button>
                  
                  {selectedCategory === category.category && (
                    <div className="mt-1 ml-2">
                      {category.queries.map((query, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            handlePromptClick(query);
                            setShowExamples(false);
                            setSelectedCategory(null);
                          }}
                          className="w-full text-left px-2 py-1 text-xs text-white/60 hover:text-white hover:bg-white/10 rounded transition-colors"
                        >
                          {query}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-white/20 flex-shrink-0 relative">
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
          {queryHistory.length > 0 && (
            <button
              onClick={() => {
                setShowHistory(!showHistory);
                setShowExamples(false);
              }}
              className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors flex items-center gap-1.5"
              title="Query History"
            >
              <History size={18} />
            </button>
          )}
          <button
            onClick={handleSend}
            disabled={isLoading || !message.trim()}
            className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {/* History Dropdown - Now appears above input */}
        {showHistory && queryHistory.length > 0 && (
          <div className="absolute bottom-full mb-2 right-4 left-4 bg-white/10 backdrop-blur-md rounded-lg p-2 max-h-48 overflow-y-auto border border-white/20">
            {queryHistory.slice(0, 10).map((query, idx) => (
              <button
                key={idx}
                onClick={() => {
                  handlePromptClick(query);
                  setShowHistory(false);
                }}
                className="w-full text-left px-3 py-2 text-sm text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}