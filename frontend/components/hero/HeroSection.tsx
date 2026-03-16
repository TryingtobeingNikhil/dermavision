"use client";

import { motion } from "framer-motion";
import { Sparkles, Brain, Shield, Zap } from "lucide-react";
import NeuralBackground from "./NeuralBackground";

export default function HeroSection() {
  const scrollToScanner = () => {
    document.getElementById('scanner')?.scrollIntoView({ 
      behavior: 'smooth' 
    });
  };

  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden">
      {/* 3D Neural Network Background */}
      <div className="absolute inset-0 opacity-30">
        <NeuralBackground />
      </div>

      {/* Animated Gradient Orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-20 left-20 w-96 h-96 bg-primary/30 rounded-full blur-3xl"
      />
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute bottom-20 right-20 w-96 h-96 bg-secondary/30 rounded-full blur-3xl"
      />

      {/* Content */}
      <div className="relative z-20 text-center px-4 max-w-6xl">
        {/* Logo/Icon */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-8"
        >
          <motion.div
            animate={{
              rotateY: [0, 360],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="inline-block"
          >
            <div className="relative">
              <Brain className="w-32 h-32 text-primary mx-auto glow-primary" />
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 border-2 border-primary/30 rounded-full"
              />
            </div>
          </motion.div>
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <h1 className="text-7xl md:text-9xl font-bold mb-6">
            <span className="text-white">Derma</span>
            <span className="text-primary text-glow">Vision</span>
            <span className="text-white"> AI</span>
          </h1>
        </motion.div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="text-xl md:text-2xl text-gray-300 mb-4 max-w-4xl mx-auto leading-relaxed"
        >
          Next-generation <span className="text-primary font-semibold">AI-powered</span> skin lesion analysis
          with <span className="text-secondary font-semibold">clinical-grade</span> uncertainty detection
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="text-gray-500 mb-12"
        >
          Powered by EfficientNet-B3 • Trained on 10,000+ dermoscopic images
        </motion.p>

        {/* Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1 }}
          className="flex flex-wrap justify-center gap-6 mb-16"
        >
          <FeatureCard
            icon={<Zap className="w-6 h-6" />}
            title="85.7%"
            subtitle="Melanoma Sensitivity"
            color="primary"
          />
          <FeatureCard
            icon={<Brain className="w-6 h-6" />}
            title="7 Classes"
            subtitle="Skin Lesion Types"
            color="secondary"
          />
          <FeatureCard
            icon={<Shield className="w-6 h-6" />}
            title="0.96 AUC"
            subtitle="Model Performance"
            color="accent"
          />
          <FeatureCard
            icon={<Sparkles className="w-6 h-6" />}
            title="60%"
            subtitle="Uncertainty Threshold"
            color="primary"
          />
        </motion.div>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.2 }}
        >
          <motion.button
            whileHover={{ scale: 1.05, boxShadow: "0 0 40px rgba(0, 217, 255, 0.6)" }}
            whileTap={{ scale: 0.95 }}
            onClick={scrollToScanner}
            className="glass-strong px-12 py-4 rounded-full text-lg font-semibold glow-primary 
                     hover:bg-primary/20 transition-all duration-300 group"
          >
            <span className="flex items-center gap-3">
              Start Analysis
              <motion.span
                animate={{ x: [0, 5, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                →
              </motion.span>
            </span>
          </motion.button>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.5 }}
          className="mt-20"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="text-primary/50 cursor-pointer"
            onClick={scrollToScanner}
          >
            <p className="text-sm uppercase tracking-wider mb-4">Scroll to Analyze</p>
            <div className="w-6 h-10 border-2 border-primary/30 rounded-full mx-auto flex justify-center">
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-1 h-3 bg-primary rounded-full mt-2"
              />
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  color: "primary" | "secondary" | "accent";
}

function FeatureCard({ icon, title, subtitle, color }: FeatureCardProps) {
  const colorClasses = {
    primary: "text-primary glow-primary border-primary/30",
    secondary: "text-secondary glow-secondary border-secondary/30",
    accent: "text-accent glow-danger border-accent/30",
  };

  return (
    <motion.div
      whileHover={{ 
        scale: 1.05, 
        y: -5,
        boxShadow: color === "primary" 
          ? "0 0 40px rgba(0, 217, 255, 0.6)"
          : color === "secondary"
          ? "0 0 40px rgba(184, 48, 255, 0.6)"
          : "0 0 40px rgba(255, 0, 110, 0.6)"
      }}
      className={`glass px-8 py-5 rounded-2xl cursor-pointer border-2 ${colorClasses[color]}`}
    >
      <div className="flex items-center gap-4">
        <div className={colorClasses[color]}>{icon}</div>
        <div className="text-left">
          <p className="text-3xl font-bold text-white">{title}</p>
          <p className="text-sm text-gray-400">{subtitle}</p>
        </div>
      </div>
    </motion.div>
  );
}