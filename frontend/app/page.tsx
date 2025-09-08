"use client";

import { useState, useEffect } from "react";
import { Header } from "@/components/Layout/Header";
import { AnalysisSummary } from "@/components/Analytics/AnalysisSummary";
import { ChartGrid } from "@/components/Visualization/ChartGrid";
import { ChatInterface } from "@/components/Chat/ChatInterface";
import { useDataAnalysis } from "@/lib/hooks/useDataAnalysis";

export default function Dashboard() {
  const [stats, setStats] = useState({
    quotes: 99,
    revenue: 11700125.564,
    products: 92
  });
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([]);
  const [lastQuery, setLastQuery] = useState("");

  const {
    analysis,
    visualizations,
    businessImpact,
    recommendations,
    isLoading,
    error,
    sendQuery
  } = useDataAnalysis();
  
  // Handle sending query
  const handleSendQuery = (query: string) => {
    setLastQuery(query);
    // Add user message to chat
    setChatHistory(prev => [...prev, { role: "user", content: query }]);
    sendQuery(query);
  };
  
  // Add response when analysis completes
  useEffect(() => {
    if (analysis?.summary && lastQuery && !isLoading) {
      // Add AI response to chat
      setChatHistory(prev => {
        // Check if response already added
        const lastMessage = prev[prev.length - 1];
        if (lastMessage && lastMessage.role === "user" && lastMessage.content === lastQuery) {
          return [...prev, { role: "assistant", content: analysis.summary }];
        }
        return prev;
      });
      setLastQuery(""); // Clear to prevent re-adding
    }
  }, [analysis, lastQuery, isLoading]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={stats} />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Analysis Summary */}
          <div className="lg:col-span-2 space-y-8">
            <AnalysisSummary 
              summary={analysis?.summary}
              recommendations={recommendations}
            />
            
            <ChartGrid 
              visualizations={visualizations}
              data={analysis?.metrics}
            />
          </div>

          {/* Right Column - Chat Interface */}
          <div className="lg:col-span-1">
            <ChatInterface
              onSendMessage={handleSendQuery}
              chatHistory={chatHistory}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}