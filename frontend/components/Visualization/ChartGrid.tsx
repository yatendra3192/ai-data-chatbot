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
  
  // Use vertical layout (single column) for better visibility
  // Each chart will be full width and have more height
  const gridCols = "grid-cols-1";
  
  console.log("[ChartGrid] Rendering", visualizations.length, "charts with vertical layout");
  
  return (
    <div className={`grid ${gridCols} gap-8`}>
      {visualizations.map((viz, index) => {
        console.log(`[ChartGrid] Rendering chart ${index + 1}:`, viz.type);
        // Wrap each chart in a larger container for better visibility
        return (
          <div key={index} className="w-full">
            <DynamicChart visualization={viz} />
          </div>
        );
      })}
    </div>
  );
}