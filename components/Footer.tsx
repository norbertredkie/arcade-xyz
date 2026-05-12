'use client';

export default function Footer() {
  return (
    <footer className="w-full bg-dark-card/50 border-t-2 border-neon-green/20 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <h3 className="text-2xl font-black text-neon-magenta mb-4" style={{textShadow: '0 0 15px rgba(255, 0, 110, 0.8)'}}>
              ARCADE.XYZ
            </h3>
            <p className="text-sm text-gray-400">
              Create maps. Earn money. Join the gaming revolution.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-neon-green font-bold mb-4" style={{textShadow: '0 0 10px rgba(0, 255, 0, 0.6)'}}>
              PRODUCT
            </h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-neon-cyan transition">Features</a></li>
              <li><a href="#" className="hover:text-neon-cyan transition">Pricing</a></li>
              <li><a href="#" className="hover:text-neon-cyan transition">API Docs</a></li>
              <li><a href="#" className="hover:text-neon-cyan transition">Status</a></li>
            </ul>
          </div>

          {/* Community */}
          <div>
            <h4 className="text-neon-cyan font-bold mb-4" style={{textShadow: '0 0 10px rgba(0, 255, 255, 0.6)'}}>
              COMMUNITY
            </h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-neon-green transition">Discord</a></li>
              <li><a href="#" className="hover:text-neon-green transition">Twitter</a></li>
              <li><a href="#" className="hover:text-neon-green transition">GitHub</a></li>
              <li><a href="#" className="hover:text-neon-green transition">Blog</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-neon-magenta font-bold mb-4" style={{textShadow: '0 0 10px rgba(255, 0, 110, 0.6)'}}>
              LEGAL
            </h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-neon-cyan transition">Privacy</a></li>
              <li><a href="#" className="hover:text-neon-cyan transition">Terms</a></li>
              <li><a href="#" className="hover:text-neon-cyan transition">Cookie Policy</a></li>
              <li><a href="#" className="hover:text-neon-cyan transition">Contact</a></li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-700 pt-8 mt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2024 Arcade.XYZ. All rights reserved. 🎮
            </p>
            <div className="flex gap-6 mt-4 md:mt-0 text-sm text-gray-400">
              <a href="#" className="hover:text-neon-green transition">Made with ⚡ for gamers</a>
              <a href="#" className="hover:text-neon-magenta transition">v1.0.0</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
