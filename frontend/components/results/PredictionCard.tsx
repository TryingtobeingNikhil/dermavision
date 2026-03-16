"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle, Info, Zap, Eye } from "lucide-react";
import ConfidenceCounter from "./ConfidenceCounter";
import ProbabilityBars from "./ProbabilityBars";
import GradCAMViewer from "./GradCAMViewer";

interface PredictionCardProps {
  prediction: {
    prediction: string | null;
    predicted_class_code: string;
    confidence: number;
    uncertain: boolean;
    message: string;
    all_probabilities: Record<string, number>;
    gradcam_base64?: string;
  };
  image: string | null;
  onReset: () => void;
}

export default function PredictionCard({ prediction, image, onReset }: PredictionCardProps) {
  const [showGradCAM, setShowGradCAM] = useState(false);

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h2 className="text-5xl font-bold mb-4">
          Analysis <span className="text-primary text-glow">Results</span>
        </h2>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column: Image & Grad-CAM */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <GradCAMViewer
            image={image}
            gradcamBase64={prediction.gradcam_base64}
            showGradCAM={showGradCAM}
            onToggle={() => setShowGradCAM(!showGradCAM)}
          />
        </motion.div>

        {/* Right Column: Prediction Details */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          {/* Main Prediction Card */}
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className={`
              glass-strong rounded-3xl p-8 relative overflow-hidden
              ${prediction.uncertain ? "border-2 border-yellow-500/50" : "border-2 border-green-500/50"}
            `}
          >
            {/* Holographic Background Effect */}
            <div className="absolute inset-0 holographic opacity-20" />
            
            <div className="relative z-10">
              {/* Status Icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.6 }}
                className="mb-6"
              >
                {prediction.uncertain ? (
                  <div className="w-20 h-20 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto glow-danger">
                    <AlertTriangle className="w-10 h-10 text-yellow-500" />
                  </div>
                ) : (
                  <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto glow-primary">
                    <CheckCircle className="w-10 h-10 text-green-500" />
                  </div>
                )}
              </motion.div>

              {/* Prediction Label */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="text-center mb-6"
              >
                {prediction.uncertain ? (
                  <>
                    <h3 className="text-3xl font-bold mb-2 text-yellow-500">
                      ⚠️ UNCERTAIN
                    </h3>
                    <p className="text-lg text-gray-300 mb-4">
                      Dermatologist Review Recommended
                    </p>
                    <div className="glass px-4 py-2 rounded-full inline-block">
                      <p className="text-sm text-gray-400">
                        Top prediction: <span className="text-white font-semibold">
                          {prediction.predicted_class_code.toUpperCase()}
                        </span>
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <h3 className="text-4xl font-bold mb-2 text-glow">
                      {prediction.prediction}
                    </h3>
                    <p className="text-gray-400">Predicted Class</p>
                  </>
                )}
              </motion.div>

              {/* Confidence Counter */}
              <ConfidenceCounter 
                confidence={prediction.confidence} 
                uncertain={prediction.uncertain}
              />

              {/* Message */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.2 }}
                className="mt-6 glass px-6 py-4 rounded-2xl"
              >
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-300">{prediction.message}</p>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Probability Bars */}
          <ProbabilityBars probabilities={prediction.all_probabilities} />

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.4 }}
            className="flex gap-4"
          >
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowGradCAM(!showGradCAM)}
              className="flex-1 glass-strong px-6 py-4 rounded-2xl font-semibold 
                       hover:bg-primary/20 transition-all flex items-center justify-center gap-2"
            >
              <Eye className="w-5 h-5" />
              {showGradCAM ? "Hide" : "Show"} Heatmap
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onReset}
              className="flex-1 glass-strong px-6 py-4 rounded-2xl font-semibold 
                       hover:bg-secondary/20 transition-all flex items-center justify-center gap-2"
            >
              <Zap className="w-5 h-5" />
              New Analysis
            </motion.button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}