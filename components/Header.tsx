'use client';

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-dark-bg/95 backdrop-blur-sm border-b-2 border-neon-green/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="text-4xl font-black text-neon-magenta arcade-flicker" style={{textShadow: '0 0 20px rgba(255, 0, 110, 0.8)'}}>
            ARCADE
          </div>
          <div className="text-2xl font-bold text-neon-cyan" style={{textShadow: '0 0 15px rgba(0, 255, 255, 0.8)'}}>
            .XYZ
          </div>
        </div>

        {/* Credit Counter */}
        <div className="flex items-center gap-3 px-6 py-2 rounded-lg border-2 border-neon-green/50 neon-glow-green">
          <div className="text-sm font-semibold text-neon-green">CREDITS</div>
          <div className="text-2xl font-black text-neon-green">5,000</div>
        </div>
      </div>
    </header>
  );
}
