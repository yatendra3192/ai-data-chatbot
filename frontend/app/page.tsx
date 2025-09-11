"use client";

import { useState, useEffect } from "react";
import { Header } from "@/components/Layout/Header";
import { AnalysisSummary } from "@/components/Analytics/AnalysisSummary";
import { ChartGrid } from "@/components/Visualization/ChartGrid";
import { TableView } from "@/components/Visualization/TableView";
import { ChatInterface } from "@/components/Chat/ChatInterface";
import { ErrorMessage } from "@/components/UI/ErrorMessage";
import { LoadingSpinner } from "@/components/UI/LoadingSpinner";
import { useDataAnalysis } from "@/lib/hooks/useDataAnalysis";

export default function Dashboard() {
  const [stats, setStats] = useState({
    quotes: 141461,
    revenue: 11700125.564,
    products: 92
  });
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([]);
  const [lastQuery, setLastQuery] = useState("");
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const [loadingMessage, setLoadingMessage] = useState("Processing your query...");
  const [activeTab, setActiveTab] = useState<"chat" | "table">("chat");

  const {
    analysis,
    textSummary,
    visualizations,
    businessImpact,
    recommendations,
    sqlQuery,
    tableData,
    rowCount,
    executionTime,
    isLoading,
    error,
    sendQuery
  } = useDataAnalysis();
  
  // Handle sending query
  const handleSendQuery = (query: string) => {
    setLastQuery(query);
    setLoadingMessage("Analyzing your query...");
    
    // Add to query history
    setQueryHistory(prev => {
      const updated = [query, ...prev.filter(q => q !== query)].slice(0, 10);
      // Save to localStorage
      localStorage.setItem('queryHistory', JSON.stringify(updated));
      return updated;
    });
    
    // Add user message to chat
    setChatHistory(prev => [...prev, { role: "user", content: query }]);
    sendQuery(query);
  };
  
  // Load query history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('queryHistory');
    if (saved) {
      setQueryHistory(JSON.parse(saved));
    }
  }, []);
  
  // Update loading message based on time
  useEffect(() => {
    if (isLoading) {
      const timer = setTimeout(() => {
        setLoadingMessage("Generating visualizations...");
      }, 2000);
      
      const timer2 = setTimeout(() => {
        setLoadingMessage("Preparing insights...");
      }, 4000);
      
      return () => {
        clearTimeout(timer);
        clearTimeout(timer2);
      };
    }
  }, [isLoading]);
  
  // Add response when analysis completes
  useEffect(() => {
    // Check for either analysis.answer (from backend) or analysis.summary
    const responseText = analysis?.answer || analysis?.summary;
    if (responseText && lastQuery && !isLoading) {
      // Combine answer with text summary if available
      let fullResponse = responseText;
      if (textSummary) {
        fullResponse = `${responseText}\n\n**Detailed Results:**\n${textSummary}`;
      }
      
      // Add AI response to chat
      setChatHistory(prev => {
        // Check if response already added
        const lastMessage = prev[prev.length - 1];
        if (lastMessage && lastMessage.role === "user" && lastMessage.content === lastQuery) {
          return [...prev, { role: "assistant", content: fullResponse }];
        }
        return prev;
      });
      setLastQuery(""); // Clear to prevent re-adding
    }
  }, [analysis, textSummary, lastQuery, isLoading]);


  const handleRetry = () => {
    if (lastQuery) {
      handleSendQuery(lastQuery);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={stats} />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Error Display */}
        {error && (
          <ErrorMessage 
            error={error} 
            recommendations={recommendations}
            onRetry={handleRetry}
          />
        )}
        
        {/* Content based on active tab */}
        {activeTab === "chat" ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Analysis Summary with Tab Navigation */}
            <div className="lg:col-span-2 space-y-6">
              {/* Tab Navigation */}
              <div className="flex space-x-1 bg-white rounded-lg shadow-sm p-1">
                <button
                  onClick={() => setActiveTab("chat")}
                  className="flex-1 px-4 py-2 rounded-md font-medium transition-colors bg-purple-600 text-white"
                >
                  Chat & Visualizations
                </button>
                <button
                  onClick={() => setActiveTab("table")}
                  className="flex-1 px-4 py-2 rounded-md font-medium transition-colors text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                >
                  Table View
                </button>
              </div>

              {isLoading ? (
                <div className="bg-white rounded-lg shadow p-8">
                  <LoadingSpinner message={loadingMessage} size="lg" />
                </div>
              ) : (
                <>
                  <AnalysisSummary 
                    summary={analysis?.summary}
                    recommendations={recommendations}
                  />
                  
                  <ChartGrid 
                    visualizations={visualizations}
                    data={analysis?.metrics}
                  />
                </>
              )}
            </div>

            {/* Right Column - Chat Interface */}
            <div className="lg:col-span-1">
              <div className="sticky top-4">
                <ChatInterface
                  onSendMessage={handleSendQuery}
                  chatHistory={chatHistory}
                  isLoading={isLoading}
                  queryHistory={queryHistory}
                />
              </div>
            </div>
          </div>
        ) : (
          /* Table View Tab */
          <div className="space-y-6">
            {/* Tab Navigation */}
            <div className="flex space-x-1 bg-white rounded-lg shadow-sm p-1">
              <button
                onClick={() => setActiveTab("chat")}
                className="flex-1 px-4 py-2 rounded-md font-medium transition-colors text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                Chat & Visualizations
              </button>
              <button
                onClick={() => setActiveTab("table")}
                className="flex-1 px-4 py-2 rounded-md font-medium transition-colors bg-purple-600 text-white"
              >
                Table View
              </button>
            </div>

            {isLoading ? (
              <div className="bg-white rounded-lg shadow p-8">
                <LoadingSpinner message={loadingMessage} size="lg" />
              </div>
            ) : (
              <TableView
                sqlQuery={sqlQuery}
                data={tableData}
                rowCount={rowCount}
                executionTime={executionTime}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}