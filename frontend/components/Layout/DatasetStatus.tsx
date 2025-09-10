import { useEffect, useState } from "react";
import { Database, HardDrive, Activity } from "lucide-react";

interface Dataset {
  name: string;
  rows: number;
  columns: number;
  sample_columns: string[];
}

interface DatasetsResponse {
  datasets: Dataset[];
  totalRows: number;
  status: string;
  backend: string;
  error?: string;
}

export function DatasetStatus() {
  const [datasets, setDatasets] = useState<DatasetsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatasetInfo();
  }, []);

  const fetchDatasetInfo = async () => {
    try {
      const response = await fetch("/api/datasets-info");
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

  if (!datasets || !datasets.datasets || datasets.datasets.length === 0) {
    return (
      <div className="flex items-center gap-2 text-sm text-red-400">
        <Database className="w-4 h-4" />
        <span>No datasets loaded</span>
      </div>
    );
  }

  const totalRows = datasets.totalRows || 0;
  const datasetCount = datasets.datasets ? datasets.datasets.length : 0;

  return (
    <div className="flex items-center gap-6">
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4 text-purple-400" />
        <span className="text-sm text-gray-300">
          {datasetCount} Datasets
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <HardDrive className="w-4 h-4 text-green-400" />
        <span className="text-sm text-gray-300">
          {datasets.backend || 'SQLite'}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <Activity className="w-4 h-4 text-blue-400" />
        <span className="text-sm text-gray-300">
          {totalRows.toLocaleString()} rows loaded
        </span>
      </div>

      <div className="hidden md:flex items-center gap-4">
        {datasets.datasets.map((dataset) => (
          <div key={dataset.name} className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-gray-400">
              {dataset.name}: {(dataset.rows / 1000).toFixed(0)}K rows
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}