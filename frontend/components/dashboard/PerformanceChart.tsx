"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";

interface PerformanceChartProps {
  data: Array<{
    name: string;
    precision: number;
    recall: number;
    f1: number;
  }>;
  type: "bar" | "radar";
}

export default function PerformanceChart({ data, type }: PerformanceChartProps) {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-strong p-4 rounded-xl border border-white/20">
          <p className="text-white font-semibold mb-2">{payload[0].payload.name}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {(entry.value * 100).toFixed(1)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      viewport={{ once: true }}
      className="glass-strong rounded-3xl p-8 h-full"
    >
      <h3 className="text-2xl font-bold mb-6">
        <span className="text-glow">
          {type === "bar" ? "Per-Class Metrics" : "Performance Radar"}
        </span>
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        {type === "bar" ? (
          <BarChart data={data}>
            <defs>
              <linearGradient id="colorPrecision" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d9ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#00d9ff" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="colorRecall" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#b830ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#b830ff" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="colorF1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff006e" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ff006e" stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis 
              dataKey="name" 
              stroke="#888" 
              tick={{ fill: "#888", fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis 
              stroke="#888" 
              tick={{ fill: "#888" }}
              domain={[0, 1]}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ color: "#fff" }}
              iconType="circle"
            />
            <Bar 
              dataKey="precision" 
              fill="url(#colorPrecision)" 
              radius={[8, 8, 0, 0]}
              animationDuration={1500}
            />
            <Bar 
              dataKey="recall" 
              fill="url(#colorRecall)" 
              radius={[8, 8, 0, 0]}
              animationDuration={1500}
              animationBegin={200}
            />
            <Bar 
              dataKey="f1" 
              fill="url(#colorF1)" 
              radius={[8, 8, 0, 0]}
              animationDuration={1500}
              animationBegin={400}
            />
          </BarChart>
        ) : (
          <RadarChart data={data}>
            <PolarGrid stroke="rgba(255,255,255,0.2)" />
            <PolarAngleAxis 
              dataKey="name" 
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 1]}
              tick={{ fill: "#888" }}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Radar
              name="Precision"
              dataKey="precision"
              stroke="#00d9ff"
              fill="#00d9ff"
              fillOpacity={0.3}
              animationDuration={1500}
            />
            <Radar
              name="Recall"
              dataKey="recall"
              stroke="#b830ff"
              fill="#b830ff"
              fillOpacity={0.3}
              animationDuration={1500}
              animationBegin={200}
            />
            <Radar
              name="F1 Score"
              dataKey="f1"
              stroke="#ff006e"
              fill="#ff006e"
              fillOpacity={0.3}
              animationDuration={1500}
              animationBegin={400}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: "#fff" }} />
          </RadarChart>
        )}
      </ResponsiveContainer>
    </motion.div>
  );
}