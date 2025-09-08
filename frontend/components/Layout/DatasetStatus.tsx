import { useEffect, useState } from "react";
import { Database, HardDrive, Activity } from "lucide-react";

interface DatasetInfo {
  loaded_rows: number;
  total_rows: number;
  memory_usage: string;
}

interface DatasetsResponse {
  loaded: boolean;
  datasets: Record<string, DatasetInfo>;
  available_for_analysis: string[];
}

export function DatasetStatus() {
  const [datasets, setDatasets] = useState<DatasetsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatasetInfo();
  }, []);

  const fetchDatasetInfo = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/datasets-info");
      const data = await response.json();
      setDatasets(data);
    } catch (error) {
      console.error("Failed to fetch dataset info:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Activity className="w-4 h-4 animate-spin" />
        <span>Loading datasets...</span>
      </div>
    );
  }

  if (!datasets || !datasets.loaded) {
    return (
      <div className="flex items-center gap-2 text-sm text-red-400">
        <Database className="w-4 h-4" />
        <span>No datasets loaded</span>
      </div>
    );
  }

  const totalMemory = Object.values(datasets.datasets)
    .reduce((acc, ds) => {
      const mem = parseFloat(ds.memory_usage.replace(" MB", ""));
      return acc + mem;
    }, 0)
    .toFixed(2);

  const totalRows = Object.values(datasets.datasets)
    .reduce((acc, ds) => acc + ds.loaded_rows, 0);

  return (
    <div className="flex items-center gap-6">
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4 text-purple-400" />
        <span className="text-sm text-gray-300">
          {Object.keys(datasets.datasets).length} Datasets
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <HardDrive className="w-4 h-4 text-green-400" />
        <span className="text-sm text-gray-300">
          {totalMemory} MB
        </span>
      </div>

      <div className="hidden md:flex items-center gap-4">
        {Object.entries(datasets.datasets).map(([name, info]) => (
          <div key={name} className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-gray-400">
              {name}: {(info.loaded_rows / 1000).toFixed(0)}K rows
            </span>
          </div>
        ))}
      </div>

      <div className="text-xs text-gray-500">
        Total: {(totalRows / 1000).toFixed(0)}K records
      </div>
    </div>
  );
}