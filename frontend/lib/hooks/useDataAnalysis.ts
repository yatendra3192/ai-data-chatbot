import { useState, useCallback, useEffect } from "react";
import { analyzeData } from "@/lib/api/dataAnalysis";

export function useDataAnalysis() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [textSummary, setTextSummary] = useState<string>("");
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [businessImpact, setBusinessImpact] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [sqlQuery, setSqlQuery] = useState<string>("");
  const [tableData, setTableData] = useState<any[]>([]);
  const [rowCount, setRowCount] = useState<number>(0);
  const [executionTime, setExecutionTime] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data on mount
  // useEffect(() => {
  //   sendQuery("Load initial dashboard data");
  // }, []);

  const sendQuery = useCallback(async (query: string, dataFile?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await analyzeData(query, dataFile);
      
      // Handle streaming response
      if (response.stream) {
        const reader = response.stream.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                console.log("[Stream] Received data with keys:", Object.keys(data));
                
                // Check for complete type - backend sends type not status
                if (data.type === 'complete' && data.data) {
                  console.log("[Stream] Complete response received");
                  const responseData = data.data; // The actual data is nested
                  
                  // Process all fields from the complete response
                  if (responseData.answer) {
                    console.log("[Stream] Answer received:", responseData.answer);
                    setAnalysis({ answer: responseData.answer, summary: responseData.answer });
                  }
                  if (responseData.text_summary) {
                    console.log("[Stream] Text summary received");
                    setTextSummary(responseData.text_summary);
                  }
                  if (responseData.visualizations) {
                    console.log("Received visualizations:", responseData.visualizations.length, "charts");
                    setVisualizations(responseData.visualizations);
                  }
                  if (responseData.sql_query) {
                    console.log("[Stream] SQL query received");
                    setSqlQuery(responseData.sql_query);
                  }
                  if (responseData.table_data) {
                    console.log("[Stream] Table data received:", responseData.table_data.length, "rows");
                    setTableData(responseData.table_data);
                  }
                  if (responseData.row_count !== undefined) {
                    console.log("[Stream] Row count:", responseData.row_count);
                    setRowCount(responseData.row_count);
                  }
                  if (responseData.execution_time !== undefined) {
                    console.log("[Stream] Execution time:", responseData.execution_time);
                    setExecutionTime(responseData.execution_time);
                  }
                  if (responseData.recommendations) {
                    setRecommendations(responseData.recommendations);
                  }
                  if (responseData.business_impact) {
                    setBusinessImpact(responseData.business_impact);
                  }
                }
                
                // Handle error type
                if (data.type === 'error') {
                  console.error("[Stream] Error:", data.error);
                  setError(data.error);
                }
              } catch (e) {
                console.error("Failed to parse:", e);
              }
            }
          }
        }
      } else {
        // Handle regular response
        setAnalysis(response.analysis);
        setVisualizations(response.visualizations || []);
        setBusinessImpact(response.business_impact);
        setRecommendations(response.recommendations || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
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
  };
}