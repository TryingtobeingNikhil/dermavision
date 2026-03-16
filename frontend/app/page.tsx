import { Navigation } from "@/components/layout/Navigation";
import { Hero } from "@/components/sections/Hero";
import { Stats } from "@/components/sections/Stats";
import { Scanner } from "@/components/sections/Scanner";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Features } from "@/components/sections/Features";
import { Footer } from "@/components/layout/Footer";
import { ToastProvider } from "@/components/ui/Toast";

export default function Home() {
  return (
    <ToastProvider>
      <Navigation />

      <main id="main-content">
        <Hero />
        <Stats />
        <Scanner />
        <HowItWorks />
        <Features />
      </main>

      <Footer />
    </ToastProvider>
  );
}