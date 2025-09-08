import { Lightbulb, ChevronDown } from "lucide-react";
import { useState } from "react";

interface QueryExamplesProps {
  onSelectExample: (query: string) => void;
}

const EXAMPLE_QUERIES = [
  {
    category: "Sales Analysis",
    queries: [
      "What are the top 5 customers by revenue?",
      "Show monthly sales trends for this year",
      "What is the average order value by status?",
      "Show sales distribution by city"
    ]
  },
  {
    category: "Product Analysis",
    queries: [
      "Which products generate the most revenue?",
      "Show top 10 products by quantity sold",
      "What is the product distribution by type?",
      "Show product sales trends over time"
    ]
  },
  {
    category: "Customer Insights",
    queries: [
      "Show customer distribution by country",
      "Who are the most active customers?",
      "What is the customer retention rate?",
      "Show new customers by month"
    ]
  },
  {
    category: "Quote Analysis",
    queries: [
      "How many quotes convert to orders?",
      "What is the average quote value?",
      "Show quote status distribution",
      "Compare quotes vs orders by month"
    ]
  }
];

export function QueryExamples({ onSelectExample }: QueryExamplesProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
      >
        <Lightbulb size={18} />
        <span className="text-sm font-medium">Example Queries</span>
        <ChevronDown 
          size={16} 
          className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          <div className="p-2">
            {EXAMPLE_QUERIES.map((category) => (
              <div key={category.category} className="mb-2">
                <button
                  onClick={() => setSelectedCategory(
                    selectedCategory === category.category ? null : category.category
                  )}
                  className="w-full text-left px-3 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 rounded-md flex items-center justify-between"
                >
                  <span>{category.category}</span>
                  <ChevronDown 
                    size={14} 
                    className={`transform transition-transform ${
                      selectedCategory === category.category ? 'rotate-180' : ''
                    }`} 
                  />
                </button>
                
                {selectedCategory === category.category && (
                  <div className="mt-1 ml-2">
                    {category.queries.map((query, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          onSelectExample(query);
                          setIsOpen(false);
                          setSelectedCategory(null);
                        }}
                        className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-purple-50 hover:text-purple-700 rounded-md transition-colors"
                      >
                        {query}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}