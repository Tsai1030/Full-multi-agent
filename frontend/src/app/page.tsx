import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import DomainCards from "@/components/DomainCards";

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-x-hidden">
      <CosmicBackground />
      <Navbar />
      <HeroSection />
      <DomainCards />

      {/* Footer */}
      <footer className="relative z-10 text-center py-10 text-parchment-muted text-xs tracking-widest">
        <div className="divider-gold w-40 mx-auto mb-6" />
        <p>紫微星盤 AI · 以傳統命理遇見現代智慧</p>
      </footer>
    </main>
  );
}
