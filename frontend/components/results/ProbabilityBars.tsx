"use client";

import { motion } from "framer-motion";

interface ProbabilityBarsProps {
  probabilities: Record<string, number>;
}

export default function ProbabilityBars({ probabilities }: ProbabilityBarsProps) {
  const sortedProbs = Object.entries(probabilities)
    .sort(([, a], [, b]) => b - a);

  const getBarColor = (value: number, index: number) => {
    if (index === 0) {
      return value >= 0.6 
        ? "from-green-500 to-green-400" 
        : "from-yellow-500 to-yellow-400";
    }
    return "from-primary to-secondary";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1 }}
      className="glass-strong rounded-3xl p-8"
    >
      <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <span className="text-glow">All Probabilities</span>
      </h3>

      <div className="space-y-4">
        {sortedProbs.map(([className, probability], index) => (
          <motion.div
            key={className}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 + index * 0.1 }}
          >
            <div className="flex justify-between items-center mb-2">
              <span className={`font-medium ${index === 0 ? "text-lg text-white" : "text-gray-400"}`}>
                {className}
              </span>
              <span className={`font-bold ${index === 0 ? "text-lg text-primary" : "text-gray-500"}`}>
                {(probability * 100).toFixed(1)}%
              </span>
            </div>

            <div className="relative h-3 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${probability * 100}%` }}
                transition={{ duration: 1, ease: "easeOut", delay: 1.4 + index * 0.1 }}
                className={`
                  absolute inset-y-0 left-0 rounded-full
                  bg-gradient-to-r ${getBarColor(probability, index)}
                `}
                style={{
                  boxShadow: index === 0
                    ? probability >= 0.6
                      ? "0 0 15px rgba(34, 197, 94, 0.6)"
                      : "0 0 15px rgba(234, 179, 8, 0.6)"
                    : "0 0 10px rgba(0, 217, 255, 0.4)",
                }}
              />

              {/* Animated shimmer effect on top bar */}
              {index === 0 && (
                <motion.div
                  animate={{
                    x: ["-100%", "100%"],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  style={{ width: `${probability * 100}%` }}
                />
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}