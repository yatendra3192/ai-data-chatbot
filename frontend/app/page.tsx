"use client";

import { useState, useEffect } from "react";
import { Header } from "@/components/Layout/Header";
import { AnalysisSummary } from "@/components/Analytics/AnalysisSummary";
import { ChartGrid } from "@/components/Visualization/ChartGrid";
import { ChatInterface } from "@/components/Chat/ChatInterface";
import { QueryExamples } from "@/components/UI/QueryExamples";
import { ErrorMessage } from "@/components/UI/ErrorMessage";
import { LoadingSpinner } from "@/components/UI/LoadingSpinner";
import { useDataAnalysis } from "@/lib/hooks/useDataAnalysis";
import { History, Download, RefreshCw } from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState({
    quotes: 141461,
    revenue: 11700125.564,
    products: 92
  });
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([]);
  const [lastQuery, setLastQuery] = useState("");
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Processing your query...");

  const {
    analysis,
    textSummary,
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

  // Export functionality
  const handleExportData = () => {
    if (!analysis || visualizations.length === 0) return;
    
    const exportData = {
      timestamp: new Date().toISOString(),
      query: chatHistory[chatHistory.length - 2]?.content || "",
      analysis: analysis,
      visualizations: visualizations,
      recommendations: recommendations
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleRetry = () => {
    if (lastQuery) {
      handleSendQuery(lastQuery);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={stats} />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Action Bar */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <QueryExamples onSelectExample={handleSendQuery} />
            
            {/* Query History */}
            <div className="relative">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <History size={18} />
                <span className="text-sm font-medium">History</span>
              </button>
              
              {showHistory && queryHistory.length > 0 && (
                <div className="absolute top-full mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-64 overflow-y-auto">
                  <div className="p-2">
                    {queryHistory.map((query, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          handleSendQuery(query);
                          setShowHistory(false);
                        }}
                        className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-purple-50 hover:text-purple-700 rounded-md transition-colors"
                      >
                        {query}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Export Button */}
          {visualizations.length > 0 && (
            <button
              onClick={handleExportData}
              className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Download size={18} />
              <span className="text-sm font-medium">Export Results</span>
            </button>
          )}
        </div>
        
        {/* Error Display */}
        {error && (
          <ErrorMessage 
            error={error} 
            recommendations={recommendations}
            onRetry={handleRetry}
          />
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Analysis Summary */}
          <div className="lg:col-span-2 space-y-8">
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