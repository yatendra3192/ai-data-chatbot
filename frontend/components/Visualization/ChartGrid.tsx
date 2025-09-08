"use client";

import { DynamicChart } from "./DynamicChart";

interface ChartGridProps {
  visualizations?: any[];
  data?: any;
}

export function ChartGrid({ visualizations, data }: ChartGridProps) {
  console.log("[ChartGrid] Received visualizations:", visualizations?.length || 0);
  
  // If no visualizations, show placeholder
  if (!visualizations || visualizations.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">No Data Available</h3>
          <p className="text-gray-500">Ask a question to see visualizations</p>
        </div>
      </div>
    );
  }
  
  // Determine grid layout based on number of visualizations
  const gridCols = visualizations.length === 1 ? "grid-cols-1" : 
                   visualizations.length === 2 ? "grid-cols-1 md:grid-cols-2" :
                   visualizations.length === 3 ? "grid-cols-1 md:grid-cols-3" :
                   visualizations.length === 4 ? "grid-cols-1 md:grid-cols-2" :
                   visualizations.length === 5 ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" :
                   "grid-cols-1 md:grid-cols-2 lg:grid-cols-3";
  
  console.log("[ChartGrid] Rendering", visualizations.length, "charts with layout:", gridCols);
  
  return (
    <div className={`grid ${gridCols} gap-6`}>
      {visualizations.map((viz, index) => {
        console.log(`[ChartGrid] Rendering chart ${index + 1}:`, viz.type);
        return <DynamicChart key={index} visualization={viz} />;
      })}
    </div>
  );
}