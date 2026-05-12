'use client';

import { useState } from 'react';

export default function MapGenerator() {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([
    { id: 1, title: 'Desert Fortress', description: 'A sprawling desert base with pyramid structures' },
    { id: 2, title: 'Neon Cyberpunk City', description: 'Futuristic cityscape with holographic billboards' },
    { id: 3, title: 'Underwater Temple', description: 'Ancient ruins beneath the ocean waves' },
  ]);

  const handleApply = (suggestion: any) => {
    setInput(suggestion.title);
  };

  const handleGenerate = () => {
    if (!input.trim()) return;
    alert(`🎮 Generating map: "${input}"\n\n⚡ This would generate an AI-powered map with your specifications!`);
  };

  return (
    <section className="w-full py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Section Title */}
        <div className="text-center mb-12">
          <h1 className="text-5xl sm:text-6xl font-black mb-4">
            <span className="text-neon-green" style={{textShadow: '0 0 30px rgba(0, 255, 0, 0.8)'}}>
              CREATE
            </span>
            <span className="text-white mx-2">MAPS.</span>
            <span className="text-neon-magenta" style={{textShadow: '0 0 30px rgba(255, 0, 110, 0.8)'}}>
              EARN
            </span>
            <span className="text-white mx-2">MONEY.</span>
            <span className="ml-2">🚀</span>
          </h1>
          <p className="text-neon-cyan text-xl mt-4" style={{textShadow: '0 0 15px rgba(0, 255, 255, 0.6)'}}>
            Power your gaming empire with AI-generated worlds
          </p>
        </div>

        {/* Input Section */}
        <div className="mb-12">
          <label className="block text-xl font-bold text-neon-green mb-4" style={{textShadow: '0 0 10px rgba(0, 255, 0, 0.8)'}}>
            What Map Do You Want?
          </label>
          <div className="flex gap-3 flex-col sm:flex-row">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
              placeholder="Describe your dream map... Cyberpunk city, fantasy dungeon, sci-fi base..."
              className="arcade-input flex-1"
            />
            <button
              onClick={handleGenerate}
              className="btn-primary whitespace-nowrap font-arcade"
            >
              ⚡ GENERATE
            </button>
          </div>
        </div>

        {/* Quick Suggestions */}
        <div className="mb-12">
          <p className="text-sm font-semibold text-neon-cyan mb-3" style={{textShadow: '0 0 8px rgba(0, 255, 255, 0.6)'}}>
            QUICK SUGGESTIONS
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {suggestions.map((suggestion) => (
              <div
                key={suggestion.id}
                className="arcade-card group cursor-pointer"
              >
                <h3 className="text-neon-cyan font-bold mb-2" style={{textShadow: '0 0 10px rgba(0, 255, 255, 0.8)'}}>
                  {suggestion.title}
                </h3>
                <p className="text-sm text-gray-300 mb-4">{suggestion.description}</p>
                <button
                  onClick={() => handleApply(suggestion)}
                  className="btn-secondary w-full text-sm py-2"
                >
                  APPLY
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* AI Suggestions Cards */}
        <div className="mb-12">
          <p className="text-sm font-semibold text-neon-cyan mb-4" style={{textShadow: '0 0 8px rgba(0, 255, 255, 0.6)'}}>
            AI SUGGESTIONS FOR YOU
          </p>
          <div className="space-y-4">
            <div className="arcade-card border-2 border-neon-cyan/50">
              <h3 className="text-neon-cyan font-bold text-lg mb-2" style={{textShadow: '0 0 10px rgba(0, 255, 255, 0.8)'}}>
                💎 Premium Challenge: "Infinite Labyrinth"
              </h3>
              <p className="text-gray-300 text-sm mb-3">
                Based on your playstyle, you'd love an intricate maze map with hidden treasures and procedural generation. High difficulty = high rewards!
              </p>
              <div className="flex gap-3">
                <button className="btn-secondary text-sm py-2 px-4">
                  APPLY
                </button>
                <button className="px-4 py-2 rounded-lg border-2 border-gray-600 text-gray-300 font-semibold hover:border-neon-green hover:text-neon-green transition-all">
                  VIEW DETAILS
                </button>
              </div>
            </div>

            <div className="arcade-card border-2 border-neon-cyan/50">
              <h3 className="text-neon-cyan font-bold text-lg mb-2" style={{textShadow: '0 0 10px rgba(0, 255, 255, 0.8)'}}>
                🏆 Trending: "Retro Arcade Battle Arena"
              </h3>
              <p className="text-gray-300 text-sm mb-3">
                2,847 players are generating this map this week. Classic arcade style with modern multiplayer elements. Perfect for streaming!
              </p>
              <div className="flex gap-3">
                <button className="btn-secondary text-sm py-2 px-4">
                  APPLY
                </button>
                <button className="px-4 py-2 rounded-lg border-2 border-gray-600 text-gray-300 font-semibold hover:border-neon-green hover:text-neon-green transition-all">
                  VIEW DETAILS
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main CTA */}
        <div className="text-center py-8 px-6 rounded-xl border-2 border-neon-magenta/50 bg-gradient-to-b from-neon-magenta/10 to-transparent">
          <p className="text-sm font-semibold text-neon-green mb-4" style={{textShadow: '0 0 8px rgba(0, 255, 0, 0.8)'}}>
            READY TO EARN?
          </p>
          <button
            onClick={handleGenerate}
            className="btn-primary font-arcade text-lg py-4 px-12 mx-auto block"
          >
            ⚡ GENERATE MAP WITH AI ⚡
          </button>
          <p className="text-xs text-gray-400 mt-4">
            Each map generation costs 10 credits. You have 5,000 credits. 🎮
          </p>
        </div>
      </div>
    </section>
  );
}
