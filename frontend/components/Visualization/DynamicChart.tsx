"use client";

import { 
  BarChart, Bar, 
  LineChart, Line,
  PieChart, Pie, Cell,
  AreaChart, Area,
  ScatterChart, Scatter,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from "recharts";

interface DynamicChartProps {
  visualization: {
    type: string;
    title: string;
    description?: string;
    data: any[];
    config?: {
      xAxis?: string;
      yAxis?: string;
      color?: string;
      colors?: string[];
      showLegend?: boolean;
      stacked?: boolean;
    };
  };
}

const COLORS = ['#818CF8', '#A78BFA', '#C084FC', '#E879F9', '#F472B6', '#FB7185', '#FCA5A5', '#FDBA74'];

export function DynamicChart({ visualization }: DynamicChartProps) {
  const { type, title, description, data, config = {} } = visualization;
  
  // Default config values
  const xAxis = config.xAxis || 'name';
  const yAxis = config.yAxis || 'value';
  const color = config.color || '#818CF8';
  const colors = config.colors || COLORS;
  
  const renderChart = () => {
    switch (type?.toLowerCase()) {
      case 'line':
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xAxis} angle={-45} textAnchor="end" height={80} tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            {config.showLegend && <Legend />}
            <Line type="monotone" dataKey={yAxis} stroke={color} strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        );
      
      case 'area':
        return (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xAxis} angle={-45} textAnchor="end" height={80} tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            {config.showLegend && <Legend />}
            <Area type="monotone" dataKey={yAxis} stroke={color} fill={color} fillOpacity={0.6} />
          </AreaChart>
        );
      
      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill={color}
              dataKey={yAxis}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        );
      
      case 'scatter':
        return (
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xAxis} tick={{ fontSize: 10 }} />
            <YAxis dataKey={yAxis} tick={{ fontSize: 10 }} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            {config.showLegend && <Legend />}
            <Scatter name={title} data={data} fill={color} />
          </ScatterChart>
        );
      
      case 'radar':
        return (
          <RadarChart data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey={xAxis} />
            <PolarRadiusAxis angle={90} domain={[0, 'auto']} />
            <Radar name={title} dataKey={yAxis} stroke={color} fill={color} fillOpacity={0.6} />
            <Tooltip />
          </RadarChart>
        );
      
      case 'stacked-bar':
        // For stacked bar, expect data to have multiple value keys
        const valueKeys = Object.keys(data[0] || {}).filter(k => k !== xAxis);
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={xAxis} angle={-45} textAnchor="end" height={80} tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Legend />
            {valueKeys.map((key, index) => (
              <Bar key={key} dataKey={key} stackId="a" fill={colors[index % colors.length]} />
            ))}
          </BarChart>
        );
      
      case 'bar':
      default:
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey={xAxis} 
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 10 }}
            />
            <YAxis 
              tick={{ fontSize: 10 }}
              tickFormatter={(value) => {
                if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
                return value;
              }}
            />
            <Tooltip 
              formatter={(value: number) => {
                if (typeof value === 'number') {
                  return value.toLocaleString();
                }
                return value;
              }}
            />
            {config.showLegend && <Legend />}
            <Bar dataKey={yAxis} fill={color} radius={[8, 8, 0, 0]} />
          </BarChart>
        );
    }
  };
  
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-gray-500 mb-4 italic">{description}</p>
      )}
      <ResponsiveContainer width="100%" height={250}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
}