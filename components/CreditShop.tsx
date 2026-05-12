'use client';

import { useState } from 'react';

export default function CreditShop() {
  const [selectedPackage, setSelectedPackage] = useState<number | null>(null);

  const packages = [
    {
      id: 1,
      credits: 50,
      price: 0.99,
      bonus: '0% bonus',
      popular: false,
    },
    {
      id: 2,
      credits: 500,
      price: 7.99,
      bonus: '25% bonus (625 total)',
      popular: true,
    },
    {
      id: 3,
      credits: 2500,
      price: 29.99,
      bonus: '50% bonus (3,750 total)',
      popular: false,
    },
  ];

  const handlePurchase = (pkg: any) => {
    setSelectedPackage(pkg.id);
    alert(`🎮 Purchase initiated!\n\n${pkg.credits} Credits + ${pkg.bonus}\nPrice: $${pkg.price.toFixed(2)}\n\nThis would process payment and add credits to your account!`);
    setSelectedPackage(null);
  };

  return (
    <section className="w-full py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-black mb-4">
            <span className="text-neon-cyan" style={{textShadow: '0 0 25px rgba(0, 255, 255, 0.8)'}}>
              BUY
            </span>
            <span className="text-white mx-2">CREDITS</span>
            <span className="text-neon-magenta" style={{textShadow: '0 0 25px rgba(255, 0, 110, 0.8)'}}>
              NOW
            </span>
          </h2>
          <p className="text-neon-green text-lg mt-4" style={{textShadow: '0 0 12px rgba(0, 255, 0, 0.8)'}}>
            Earn more maps, earn more money. One credit = 1 map generation.
          </p>
        </div>

        {/* Credit Packages */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {packages.map((pkg) => (
            <div
              key={pkg.id}
              className={`arcade-card border-2 transform transition-all duration-300 hover:scale-105 ${
                pkg.popular
                  ? 'border-neon-magenta md:scale-105 shadow-lg'
                  : 'border-neon-cyan/30 hover:border-neon-cyan'
              } ${selectedPackage === pkg.id ? 'ring-2 ring-neon-green' : ''}`}
            >
              {pkg.popular && (
                <div className="absolute -top-3 right-4">
                  <span className="bg-neon-magenta text-dark-bg px-3 py-1 rounded-full text-xs font-black">
                    BEST VALUE
                  </span>
                </div>
              )}

              <div className="text-center">
                <div className="text-5xl font-black text-neon-green mb-2" style={{textShadow: '0 0 20px rgba(0, 255, 0, 0.8)'}}>
                  {pkg.credits}
                </div>
                <div className="text-sm text-gray-400 mb-4">CREDITS</div>

                <div className="text-2xl font-black text-neon-magenta mb-2" style={{textShadow: '0 0 15px rgba(255, 0, 110, 0.8)'}}>
                  ${pkg.price.toFixed(2)}
                </div>

                <div className="text-neon-cyan text-sm mb-6" style={{textShadow: '0 0 8px rgba(0, 255, 255, 0.6)'}}>
                  {pkg.bonus}
                </div>

                <button
                  onClick={() => handlePurchase(pkg)}
                  className={pkg.popular ? 'btn-primary w-full font-bold' : 'btn-secondary w-full font-bold'}
                >
                  BUY NOW
                </button>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700">
                <p className="text-xs text-gray-400 text-center">
                  {(pkg.credits / pkg.price).toFixed(0)} credits per dollar
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Trust Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 rounded-lg border border-gray-700">
            <div className="text-2xl mb-2">🔒</div>
            <p className="text-xs text-gray-400">Secure Payment</p>
          </div>
          <div className="p-4 rounded-lg border border-gray-700">
            <div className="text-2xl mb-2">⚡</div>
            <p className="text-xs text-gray-400">Instant Delivery</p>
          </div>
          <div className="p-4 rounded-lg border border-gray-700">
            <div className="text-2xl mb-2">💯</div>
            <p className="text-xs text-gray-400">No Hidden Fees</p>
          </div>
          <div className="p-4 rounded-lg border border-gray-700">
            <div className="text-2xl mb-2">🔄</div>
            <p className="text-xs text-gray-400">30-Day Guarantee</p>
          </div>
        </div>
      </div>
    </section>
  );
}
