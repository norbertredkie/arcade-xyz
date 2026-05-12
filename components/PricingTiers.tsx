'use client';

export default function PricingTiers() {
  const tiers = [
    {
      name: 'FREE',
      price: '$0',
      period: 'forever',
      features: [
        '100 credits/month',
        '10 maps/month',
        'Basic map styles',
        'Community support',
        'Standard resolution',
      ],
      cta: 'GET STARTED',
      featured: false,
    },
    {
      name: 'PRO',
      price: '$9.99',
      period: 'per month',
      features: [
        '1,000 credits/month',
        'Unlimited maps',
        'Premium map styles',
        '24/7 Priority support',
        '4K resolution',
        'Custom themes',
        'Advanced AI suggestions',
      ],
      cta: 'START PRO',
      featured: true,
    },
    {
      name: 'STUDIO',
      price: '$49.99',
      period: 'per month',
      features: [
        '10,000 credits/month',
        'Unlimited maps',
        'All premium styles',
        'Dedicated account manager',
        '8K resolution',
        'White-label options',
        'API access',
        'Team collaboration',
        'Revenue sharing (up to 50%)',
      ],
      cta: 'GO STUDIO',
      featured: false,
    },
  ];

  return (
    <section className="w-full py-20 px-4 sm:px-6 lg:px-8 bg-dark-card/30">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-black mb-4">
            <span className="text-neon-magenta" style={{textShadow: '0 0 25px rgba(255, 0, 110, 0.8)'}}>
              CHOOSE
            </span>
            <span className="text-white mx-2">YOUR</span>
            <span className="text-neon-green" style={{textShadow: '0 0 25px rgba(0, 255, 0, 0.8)'}}>
              TIER
            </span>
          </h2>
          <p className="text-neon-cyan text-lg mt-4" style={{textShadow: '0 0 12px rgba(0, 255, 255, 0.6)'}}>
            Scale your gaming empire from free to enterprise
          </p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {tiers.map((tier, idx) => (
            <div
              key={idx}
              className={`pricing-card ${tier.featured ? 'featured' : ''}`}
            >
              {tier.featured && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-neon-magenta text-dark-bg px-4 py-1 rounded-full text-sm font-black" style={{textShadow: 'none'}}>
                    ⭐ MOST POPULAR
                  </span>
                </div>
              )}

              <h3 className="text-2xl font-black text-neon-green mb-2" style={{textShadow: '0 0 15px rgba(0, 255, 0, 0.8)'}}>
                {tier.name}
              </h3>

              <div className="mb-6">
                <div className="text-4xl font-black text-neon-cyan" style={{textShadow: '0 0 15px rgba(0, 255, 255, 0.8)'}}>
                  {tier.price}
                </div>
                <div className="text-sm text-gray-400 mt-1">{tier.period}</div>
              </div>

              <button
                className={tier.featured ? 'btn-primary w-full font-bold mb-6' : 'btn-secondary w-full font-bold mb-6'}
              >
                {tier.cta}
              </button>

              <div className="space-y-3">
                {tier.features.map((feature, fidx) => (
                  <div key={fidx} className="flex items-start gap-3">
                    <span className="text-neon-green font-bold mt-1">✓</span>
                    <span className="text-sm text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Comparison Note */}
        <div className="text-center">
          <p className="text-gray-400 text-sm">
            All plans include 30-day money-back guarantee. No credit card required for FREE tier.
          </p>
        </div>
      </div>
    </section>
  );
}
