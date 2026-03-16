"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ZoomIn, ZoomOut } from "lucide-react";

interface GradCAMViewerProps {
  image: string | null;
  gradcamBase64?: string;
  showGradCAM: boolean;
  onToggle: () => void;
}

export default function GradCAMViewer({ 
  image, 
  gradcamBase64, 
  showGradCAM,
  onToggle 
}: GradCAMViewerProps) {
  const [opacity, setOpacity] = useState(0.6);
  const [zoom, setZoom] = useState(1);

  return (
    <div className="glass-strong rounded-3xl p-8">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold">
          <span className="text-glow">Visual Analysis</span>
        </h3>

        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setZoom(Math.max(1, zoom - 0.2))}
            disabled={zoom <= 1}
            className="glass p-2 rounded-lg hover:bg-white/10 transition-all disabled:opacity-30"
          >
            <ZoomOut className="w-4 h-4" />
          </motion.button>

          <span className="text-sm text-gray-400 w-12 text-center">
            {(zoom * 100).toFixed(0)}%
          </span>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setZoom(Math.min(2, zoom + 0.2))}
            disabled={zoom >= 2}
            className="glass p-2 rounded-lg hover:bg-white/10 transition-all disabled:opacity-30"
          >
            <ZoomIn className="w-4 h-4" />
          </motion.button>
        </div>
      </div>

      {/* Image Container */}
      <div className="relative aspect-square rounded-2xl overflow-hidden bg-black/20">
        {image && (
          <motion.div
            animate={{ scale: zoom }}
            transition={{ type: "spring", stiffness: 200 }}
            className="relative w-full h-full"
          >
            <img
              src={image}
              alt="Original lesion"
              className="w-full h-full object-contain"
            />

            {/* Grad-CAM Overlay */}
            <AnimatePresence>
              {showGradCAM && gradcamBase64 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: opacity }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="absolute inset-0"
                >
                  <img
                    src={`data:image/png;base64,${gradcamBase64}`}
                    alt="Grad-CAM heatmap"
                    className="w-full h-full object-contain"
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Border Effect */}
        <div className="absolute inset-0 border-2 border-primary/30 rounded-2xl pointer-events-none" />
      </div>

      {/* Opacity Slider (only shown when Grad-CAM is active) */}
      <AnimatePresence>
        {showGradCAM && gradcamBase64 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6"
          >
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400 w-20">Opacity:</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={opacity}
                onChange={(e) => setOpacity(parseFloat(e.target.value))}
                className="flex-1 h-2 bg-white/10 rounded-full appearance-none cursor-pointer
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 
                         [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full 
                         [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:cursor-pointer
                         [&::-webkit-slider-thumb]:shadow-[0_0_10px_rgba(0,217,255,0.8)]"
              />
              <span className="text-sm text-primary w-12 text-right">
                {(opacity * 100).toFixed(0)}%
              </span>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-4 glass px-4 py-3 rounded-xl"
            >
              <p className="text-xs text-gray-400 leading-relaxed">
                🔥 <span className="text-primary font-semibold">Heatmap</span> shows regions 
                the AI focused on. Red/yellow areas had the strongest influence on the prediction.
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}