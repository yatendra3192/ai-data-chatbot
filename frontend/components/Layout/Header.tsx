import { Shield, DollarSign, Package } from "lucide-react";
import { DatasetStatus } from "./DatasetStatus";

interface HeaderProps {
  stats: {
    quotes: number;
    revenue: number;
    products: number;
  };
}

export function Header({ stats }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Shield className="w-8 h-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                AI Data Analyst Dashboard
              </h1>
            </div>
            <div className="border-l border-gray-300 pl-4">
              <DatasetStatus />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}