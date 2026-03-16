"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, X, Loader2, Sparkles } from "lucide-react";
import { fileToBase64 } from "../../lib/utils";
import ScanningAnimation from "./ScanningAnimation";
import HolographicLoader from "./HolographicLoader";

interface ImageUploaderProps {
  onImageUpload: (imageData: string) => void;
  isAnalyzing: boolean;
  uploadedImage: string | null;
  onReset: () => void;
}

export default function ImageUploader({
  onImageUpload,
  isAnalyzing,
  uploadedImage,
  onReset,
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        const base64 = await fileToBase64(file);
        const reader = new FileReader();
        reader.onload = () => {
          onImageUpload(reader.result as string);
        };
        reader.readAsDataURL(file);
      }
    },
    [onImageUpload]
  );

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        onImageUpload(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <AnimatePresence mode="wait">
        {!uploadedImage ? (
          // Upload Area
          <motion.div
            key="uploader"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`
              glass-strong rounded-3xl p-12 border-2 border-dashed
              transition-all duration-300 cursor-pointer
              ${isDragging 
                ? "border-primary glow-primary bg-primary/10 scale-105" 
                : "border-white/20 hover:border-primary/50 hover:glow-primary"
              }
            `}
          >
            <div className="text-center">
              <motion.div
                animate={{
                  y: [0, -10, 0],
                  rotateZ: isDragging ? [0, 5, -5, 0] : 0,
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="mb-6"
              >
                <Upload className="w-20 h-20 mx-auto text-primary" />
              </motion.div>

              <h3 className="text-3xl font-bold mb-3 text-glow">
                Upload Dermoscopic Image
              </h3>
              
              <p className="text-gray-400 mb-8 text-lg">
                Drag and drop or click to select
              </p>

              <label className="inline-block">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="glass px-8 py-4 rounded-full font-semibold glow-primary 
                           hover:bg-primary/20 transition-all cursor-pointer inline-flex items-center gap-2"
                >
                  <Sparkles className="w-5 h-5" />
                  Select Image
                </motion.div>
              </label>

              <p className="text-sm text-gray-500 mt-6">
                Supported formats: JPG, PNG, JPEG
              </p>
            </div>
          </motion.div>
        ) : (
          // Preview & Analysis
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="glass-strong rounded-3xl p-8 relative overflow-hidden"
          >
            {/* Reset Button */}
            <motion.button
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.9 }}
              onClick={onReset}
              className="absolute top-6 right-6 z-20 glass p-3 rounded-full glow-primary 
                       hover:bg-red-500/20 transition-all"
            >
              <X className="w-6 h-6" />
            </motion.button>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Image Preview */}
              <div className="relative">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="relative rounded-2xl overflow-hidden aspect-square"
                >
                  <img
                    src={uploadedImage}
                    alt="Uploaded lesion"
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Scanning Animation Overlay */}
                  {isAnalyzing && <ScanningAnimation />}
                  
                  {/* Holographic Border */}
                  <div className="absolute inset-0 border-2 border-primary/50 rounded-2xl pointer-events-none" />
                </motion.div>
              </div>

              {/* Analysis Status */}
              <div className="flex flex-col justify-center">
                {isAnalyzing ? (
                  <div className="text-center">
                    <HolographicLoader />
                    
                    <motion.h3
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="text-3xl font-bold mb-4 text-glow"
                    >
                      AI Analyzing...
                    </motion.h3>
                    
                    <div className="space-y-3 text-left max-w-md mx-auto">
                      <AnalysisStep 
                        delay={0} 
                        text="Preprocessing image" 
                      />
                      <AnalysisStep 
                        delay={0.5} 
                        text="Extracting features" 
                      />
                      <AnalysisStep 
                        delay={1} 
                        text="Running neural network" 
                      />
                      <AnalysisStep 
                        delay={1.5} 
                        text="Calculating confidence" 
                      />
                      <AnalysisStep 
                        delay={2} 
                        text="Generating heatmap" 
                      />
                    </div>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                  >
                    <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4 glow-primary">
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", stiffness: 200 }}
                      >
                        ✓
                      </motion.div>
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Image Ready</h3>
                    <p className="text-gray-400">Scroll down to view results</p>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function AnalysisStep({ delay, text }: { delay: number; text: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-center gap-3 text-gray-300"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      >
        <Loader2 className="w-4 h-4 text-primary" />
      </motion.div>
      <span>{text}</span>
    </motion.div>
  );
}