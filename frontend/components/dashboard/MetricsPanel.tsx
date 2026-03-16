"use client";

import { motion } from "framer-motion";
import { Brain, Target, TrendingUp, Shield, Zap, Activity } from "lucide-react";
import PerformanceChart from "./PerformanceChart";
import StatsWidget from "./StatsWidget";

export default function MetricsPanel() {
  // Real metrics from your trained model
  const modelMetrics = {
    accuracy: 0.6647,
    macroF1: 0.6892,
    melanomaSensitivity: 0.8571,
    macroAUC: 0.9577,
    weightedAUC: 0.9440,
    uncertaintyThreshold: 0.60,
  };

  const classMetrics = [
    { name: "Actinic Keratoses", precision: 0.600, recall: 0.750, f1: 0.667 },
    { name: "Basal Cell Carcinoma", precision: 0.682, recall: 0.865, f1: 0.763 },
    { name: "Benign Keratosis", precision: 0.582, recall: 0.709, f1: 0.639 },
    { name: "Dermatofibroma", precision: 0.688, recall: 1.000, f1: 0.815 },
    { name: "Melanoma", precision: 0.296, recall: 0.857, f1: 0.440 },
    { name: "Melanocytic Nevi", precision: 0.997, recall: 0.593, f1: 0.744 },
    { name: "Vascular Lesions", precision: 0.609, recall: 1.000, f1: 0.757 },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Section Header */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
        className="text-center mb-16"
      >
        <h2 className="text-5xl font-bold mb-4">
          Model <span className="text-primary text-glow">Performance</span>
        </h2>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Real-time metrics from production model trained on 10,015 dermoscopic images
        </p>
      </motion.div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
        <StatsWidget
          icon={<Target className="w-6 h-6" />}
          label="Accuracy"
          value={modelMetrics.accuracy}
          format="percentage"
          delay={0}
          color="primary"
        />
        <StatsWidget
          icon={<TrendingUp className="w-6 h-6" />}
          label="Macro F1"
          value={modelMetrics.macroF1}
          format="percentage"
          delay={0.1}
          color="secondary"
        />
        <StatsWidget
          icon={<Zap className="w-6 h-6" />}
          label="Melanoma Sensitivity"
          value={modelMetrics.melanomaSensitivity}
          format="percentage"
          delay={0.2}
          color="accent"
          highlight
        />
        <StatsWidget
          icon={<Activity className="w-6 h-6" />}
          label="Macro AUC"
          value={modelMetrics.macroAUC}
          format="percentage"
          delay={0.3}
          color="primary"
        />
        <StatsWidget
          icon={<Brain className="w-6 h-6" />}
          label="Weighted AUC"
          value={modelMetrics.weightedAUC}
          format="percentage"
          delay={0.4}
          color="secondary"
        />
        <StatsWidget
          icon={<Shield className="w-6 h-6" />}
          label="Threshold"
          value={modelMetrics.uncertaintyThreshold}
          format="percentage"
          delay={0.5}
          color="accent"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid lg:grid-cols-2 gap-8 mb-12">
        {/* Performance Chart */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <PerformanceChart data={classMetrics} type="bar" />
        </motion.div>

        {/* Radar Chart */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
        >
          <PerformanceChart data={classMetrics} type="radar" />
        </motion.div>
      </div>

      {/* Model Architecture Info */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        viewport={{ once: true }}
        className="glass-strong rounded-3xl p-8"
      >
        <h3 className="text-3xl font-bold mb-8 text-center">
          <span className="text-glow">Architecture</span> Overview
        </h3>

        <div className="grid md:grid-cols-3 gap-6">
          <ArchitectureCard
            title="Base Model"
            items={[
              "EfficientNet-B3",
              "ImageNet Pretrained",
              "10.7M Parameters",
              "224x224 Input Size",
            ]}
            delay={0.8}
          />
          <ArchitectureCard
            title="Training"
            items={[
              "Focal Loss (γ=2.0)",
              "AdamW Optimizer",
              "Cosine Annealing LR",
              "Weighted Sampling",
            ]}
            delay={1}
          />
          <ArchitectureCard
            title="Dataset"
            items={[
              "HAM10000 (10,015)",
              "7 Lesion Classes",
              "80/10/10 Split",
              "Data Augmentation",
            ]}
            delay={1.2}
          />
        </div>
      </motion.div>
    </div>
  );
}

function ArchitectureCard({ 
  title, 
  items, 
  delay 
}: { 
  title: string; 
  items: string[]; 
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      viewport={{ once: true }}
      className="glass p-6 rounded-2xl hover:bg-white/10 transition-all"
    >
      <h4 className="text-xl font-bold mb-4 text-primary">{title}</h4>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -10 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: delay + i * 0.1 }}
            viewport={{ once: true }}
            className="flex items-center gap-2 text-gray-300"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-primary" />
            <span className="text-sm">{item}</span>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
}