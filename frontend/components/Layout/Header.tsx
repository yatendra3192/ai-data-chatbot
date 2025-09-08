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
          <div className="flex items-center gap-2">
            <Shield className="w-8 h-8 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-900">
              AI Data Analyst Dashboard
            </h1>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Package className="w-4 h-4 text-orange-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Quotes</p>
                <p className="font-semibold text-gray-900">{stats.quotes}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="p-2 bg-green-100 rounded-lg">
                <DollarSign className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Revenue</p>
                <p className="font-semibold text-gray-900">
                  ${stats.revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Package className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Products</p>
                <p className="font-semibold text-gray-900">{stats.products}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Dataset Status Bar */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <DatasetStatus />
        </div>
      </div>
    </header>
  );
}