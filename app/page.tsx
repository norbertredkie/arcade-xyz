import Header from '@/components/Header';
import MapGenerator from '@/components/MapGenerator';
import PricingTiers from '@/components/PricingTiers';
import CreditShop from '@/components/CreditShop';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-dark-bg overflow-x-hidden">
      {/* Navigation */}
      <Header />

      {/* Hero & Map Generator */}
      <div className="pt-24">
        <MapGenerator />
      </div>

      {/* Divider */}
      <div className="w-full h-px bg-gradient-to-r from-transparent via-neon-green to-transparent opacity-30"></div>

      {/* Pricing Tiers */}
      <PricingTiers />

      {/* Divider */}
      <div className="w-full h-px bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-30"></div>

      {/* Credit Shop */}
      <CreditShop />

      {/* Divider */}
      <div className="w-full h-px bg-gradient-to-r from-transparent via-neon-magenta to-transparent opacity-30"></div>

      {/* Footer */}
      <Footer />
    </main>
  );
}
