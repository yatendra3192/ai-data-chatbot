import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorMessageProps {
  error: string;
  recommendations?: string[];
  onRetry?: () => void;
}

export function ErrorMessage({ error, recommendations, onRetry }: ErrorMessageProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 my-4">
      <div className="flex items-start space-x-3">
        <AlertCircle className="text-red-500 mt-0.5" size={20} />
        <div className="flex-1">
          <h3 className="text-red-800 font-semibold">Error Processing Query</h3>
          <p className="text-red-700 mt-1 text-sm">{error}</p>
          
          {recommendations && recommendations.length > 0 && (
            <div className="mt-3">
              <p className="text-red-800 text-sm font-medium">Suggestions:</p>
              <ul className="mt-1 list-disc list-inside text-red-700 text-sm">
                {recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
          
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 flex items-center space-x-2 text-red-700 hover:text-red-800 text-sm font-medium"
            >
              <RefreshCw size={16} />
              <span>Try Again</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}