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
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-1.5">
        <Database className="w-4 h-4 text-purple-500" />
        <span className="text-gray-600">
          {datasetCount} Datasets
        </span>
      </div>
      
      <div className="flex items-center gap-1.5">
        <HardDrive className="w-4 h-4 text-green-500" />
        <span className="text-gray-600">
          {datasets.backend || 'SQLite Database'}
        </span>
      </div>
      
      <div className="flex items-center gap-1.5">
        <Activity className="w-4 h-4 text-blue-500" />
        <span className="text-gray-600">
          {totalRows.toLocaleString()} rows loaded
        </span>
      </div>

      <div className="hidden lg:flex items-center gap-3">
        {datasets.datasets.map((dataset) => (
          <div key={dataset.name} className="flex items-center gap-1.5 text-xs">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
            <span className="text-gray-500">
              {dataset.name}: {(dataset.rows / 1000).toFixed(0)}K rows
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}