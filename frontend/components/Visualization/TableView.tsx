"use client";

import { useState } from "react";
import { Copy, Check, Database, FileCode } from "lucide-react";

interface TableViewProps {
  sqlQuery: string;
  data: any[];
  rowCount: number;
  executionTime: number;
}

export function TableView({ sqlQuery, data, rowCount, executionTime }: TableViewProps) {
  const [copiedSql, setCopiedSql] = useState(false);
  const [showFullQuery, setShowFullQuery] = useState(false);
  
  const handleCopySql = () => {
    navigator.clipboard.writeText(sqlQuery);
    setCopiedSql(true);
    setTimeout(() => setCopiedSql(false), 2000);
  };
  
  // Get column headers from first row of data
  const columns = data && data.length > 0 ? Object.keys(data[0]) : [];
  
  // Format cell value for display
  const formatCellValue = (value: any) => {
    if (value === null || value === undefined) return "-";
    if (typeof value === "number") {
      // Format numbers with commas
      if (value % 1 !== 0) {
        return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
      }
      return value.toLocaleString();
    }
    if (typeof value === "boolean") return value ? "Yes" : "No";
    return String(value);
  };
  
  return (
    <div className="space-y-6">
      {/* SQL Query Section */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">SQL Query</h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {rowCount} rows • {executionTime}s
            </span>
            <button
              onClick={handleCopySql}
              className="flex items-center gap-2 px-3 py-1.5 text-sm bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
            >
              {copiedSql ? (
                <>
                  <Check className="w-4 h-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy SQL
                </>
              )}
            </button>
          </div>
        </div>
        
        <div className="relative">
          <pre className={`bg-gray-50 rounded-lg p-4 text-sm font-mono text-gray-700 overflow-x-auto ${!showFullQuery && sqlQuery.length > 200 ? 'max-h-20 overflow-hidden' : ''}`}>
            {sqlQuery}
          </pre>
          {sqlQuery.length > 200 && (
            <button
              onClick={() => setShowFullQuery(!showFullQuery)}
              className="absolute bottom-2 right-2 text-xs bg-white px-2 py-1 rounded border border-gray-200 hover:bg-gray-50"
            >
              {showFullQuery ? "Show less" : "Show more"}
            </button>
          )}
        </div>
      </div>
      
      {/* Data Table Section */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900">Query Results</h3>
        </div>
        
        {data && data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {columns.map((column) => (
                    <th
                      key={column}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {column.replace(/_/g, " ")}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.slice(0, 100).map((row, rowIndex) => (
                  <tr key={rowIndex} className="hover:bg-gray-50">
                    {columns.map((column) => (
                      <td
                        key={column}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                      >
                        {formatCellValue(row[column])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {data.length > 100 && (
              <div className="mt-4 text-sm text-gray-500 text-center">
                Showing first 100 rows of {data.length} total rows
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No data available. Run a query to see results.
          </div>
        )}
      </div>
    </div>
  );
}