"""
Gen Z UI Design System for Arcade.XYZ

Colors, typography, and component guidelines for TikTok-meets-Fortnite aesthetic
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

COLORS = {
    # Primary (Hot Pink) - Call-to-action, buttons, highlights
    "primary": "#FF006E",
    "primary_light": "#FF1493",
    "primary_dark": "#C4004F",
    # Secondary (Electric Cyan) - Accents, hovers, energy
    "secondary": "#00D9FF",
    "secondary_light": "#00FFFF",
    "secondary_dark": "#0099BB",
    # Accent (Lime) - Success, credits earned, achievements
    "accent": "#39FF14",
    "accent_light": "#76FF03",
    "accent_dark": "#2FA300",
    # Backgrounds
    "bg_dark": "#0a0e27",  # Deep purple/black
    "bg_surface": "rgba(255,255,255,0.05)",  # Glassmorphism surface
    "bg_hover": "rgba(255,255,255,0.08)",  # Hover state
    # Text
    "text_primary": "#FFFFFF",
    "text_secondary": "rgba(255,255,255,0.7)",
    "text_muted": "rgba(255,255,255,0.5)",
    # Utilities
    "error": "#FF4444",
    "warning": "#FFAA00",
    "success": "#39FF14",
    "info": "#00D9FF",
}

# ============================================================================
# TYPOGRAPHY
# ============================================================================

TYPOGRAPHY = {
    "fonts": {
        "display": "'Poppins', sans-serif",  # Bold, playful headings
        "body": "'Outfit', sans-serif",  # Modern, clean body text
        "mono": "'Courier New', monospace",  # Code
    },
    "sizes": {
        "xs": "12px",
        "sm": "14px",
        "base": "16px",
        "lg": "18px",
        "xl": "20px",
        "2xl": "24px",
        "3xl": "30px",
        "4xl": "36px",
        "5xl": "48px",
    },
    "weights": {
        "light": 300,
        "normal": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700,
        "extrabold": 800,
    },
    "line_heights": {
        "tight": 1.2,
        "normal": 1.5,
        "relaxed": 1.75,
        "loose": 2,
    },
}

# ============================================================================
# COMPONENT STYLES (CSS-in-JS ready)
# ============================================================================

COMPONENTS = {
    "button_primary": {
        "padding": "12px 24px",
        "border_radius": "16px",
        "font_weight": 700,
        "font_size": "16px",
        "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']})",
        "color": COLORS["text_primary"],
        "border": "none",
        "cursor": "pointer",
        "transition": "all 0.2s ease",
        "box_shadow": f"0 0 20px rgba(255, 0, 110, 0.4)",
        "hover": {
            "transform": "scale(1.05)",
            "box_shadow": f"0 0 30px rgba(255, 0, 110, 0.6)",
        },
        "active": {
            "transform": "scale(0.95)",
        },
    },
    "button_secondary": {
        "padding": "12px 24px",
        "border_radius": "16px",
        "font_weight": 600,
        "font_size": "16px",
        "background": f"linear-gradient(135deg, {COLORS['secondary']}, {COLORS['secondary_light']})",
        "color": COLORS["bg_dark"],
        "border": "none",
        "cursor": "pointer",
        "transition": "all 0.2s ease",
        "box_shadow": f"0 0 20px rgba(0, 217, 255, 0.3)",
        "hover": {
            "transform": "scale(1.05)",
            "box_shadow": f"0 0 30px rgba(0, 217, 255, 0.5)",
        },
    },
    "button_outline": {
        "padding": "12px 24px",
        "border_radius": "16px",
        "font_weight": 600,
        "font_size": "16px",
        "background": "transparent",
        "color": COLORS["secondary"],
        "border": f"2px solid {COLORS['secondary']}",
        "cursor": "pointer",
        "transition": "all 0.2s ease",
        "hover": {
            "background": f"rgba(0, 217, 255, 0.1)",
            "box_shadow": f"0 0 20px rgba(0, 217, 255, 0.3)",
        },
    },
    "card": {
        "background": COLORS["bg_surface"],
        "backdrop_filter": "blur(10px)",
        "border": f"1px solid rgba(255, 255, 255, 0.1)",
        "border_radius": "16px",
        "padding": "20px",
        "transition": "all 0.2s ease",
        "hover": {
            "background": COLORS["bg_hover"],
            "border_color": f"rgba(0, 217, 255, 0.3)",
            "box_shadow": f"0 0 20px rgba(0, 217, 255, 0.2)",
        },
    },
    "input": {
        "background": f"rgba(255, 255, 255, 0.05)",
        "border": f"1px solid rgba(255, 255, 255, 0.1)",
        "border_radius": "12px",
        "padding": "12px 16px",
        "color": COLORS["text_primary"],
        "font_size": "16px",
        "font_family": TYPOGRAPHY["fonts"]["body"],
        "transition": "all 0.2s ease",
        "placeholder_color": COLORS["text_muted"],
        "focus": {
            "background": f"rgba(255, 255, 255, 0.08)",
            "border_color": COLORS["secondary"],
            "box_shadow": f"0 0 10px rgba(0, 217, 255, 0.3)",
            "outline": "none",
        },
    },
    "badge": {
        "display": "inline_block",
        "padding": "6px 12px",
        "border_radius": "20px",
        "font_size": "12px",
        "font_weight": 600,
        "background": f"rgba(0, 217, 255, 0.1)",
        "color": COLORS["secondary"],
        "border": f"1px solid {COLORS['secondary']}",
    },
    "dialog": {
        "background": COLORS["bg_dark"],
        "border_radius": "20px",
        "padding": "24px",
        "box_shadow": f"0 20px 60px rgba(255, 0, 110, 0.2)",
        "border": f"1px solid rgba(255, 0, 110, 0.2)",
    },
}

# ============================================================================
# ANIMATIONS
# ============================================================================

ANIMATIONS = {
    "fade_in": {
        "duration": "0.3s",
        "timing": "ease-in",
        "keyframes": {
            "0%": {"opacity": "0"},
            "100%": {"opacity": "1"},
        },
    },
    "slide_up": {
        "duration": "0.3s",
        "timing": "ease-out",
        "keyframes": {
            "0%": {"opacity": "0", "transform": "translateY(10px)"},
            "100%": {"opacity": "1", "transform": "translateY(0)"},
        },
    },
    "bounce": {
        "duration": "0.5s",
        "timing": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        "keyframes": {
            "0%": {"transform": "scale(0.95)"},
            "50%": {"transform": "scale(1.05)"},
            "100%": {"transform": "scale(1)"},
        },
    },
    "pulse": {
        "duration": "2s",
        "timing": "ease-in-out",
        "timing_function": "infinite",
        "keyframes": {
            "0%": {"opacity": "1"},
            "50%": {"opacity": "0.7"},
            "100%": {"opacity": "1"},
        },
    },
    "glow": {
        "duration": "0.3s",
        "timing": "ease-out",
        "keyframes": {
            "0%": {"box_shadow": f"0 0 0px rgba(255, 0, 110, 0)"},
            "100%": {
                "box_shadow": f"0 0 20px rgba(255, 0, 110, 0.6)"
            },
        },
    },
}

# ============================================================================
# SPACING SCALE
# ============================================================================

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "20px",
    "2xl": "24px",
    "3xl": "32px",
    "4xl": "40px",
    "5xl": "48px",
    "6xl": "60px",
}

# ============================================================================
# SHADOWS
# ============================================================================

SHADOWS = {
    "sm": "0 2px 4px rgba(0, 0, 0, 0.1)",
    "md": "0 4px 12px rgba(0, 0, 0, 0.15)",
    "lg": "0 8px 24px rgba(0, 0, 0, 0.2)",
    "xl": "0 12px 32px rgba(0, 0, 0, 0.25)",
    "neon_pink": f"0 0 20px rgba(255, 0, 110, 0.4)",
    "neon_cyan": f"0 0 20px rgba(0, 217, 255, 0.3)",
    "neon_lime": f"0 0 20px rgba(57, 255, 20, 0.3)",
}

# ============================================================================
# ZINDEX SCALE
# ============================================================================

ZINDEX = {
    "base": 0,
    "dropdown": 100,
    "sticky": 200,
    "fixed": 300,
    "modal": 400,
    "popover": 500,
    "tooltip": 600,
}

# ============================================================================
# VIEWPORT BREAKPOINTS
# ============================================================================

BREAKPOINTS = {
    "xs": "0px",
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}

# ============================================================================
# DESIGN TOKENS (Export as Python dict for easy access)
# ============================================================================

DESIGN_TOKENS = {
    "colors": COLORS,
    "typography": TYPOGRAPHY,
    "components": COMPONENTS,
    "animations": ANIMATIONS,
    "spacing": SPACING,
    "shadows": SHADOWS,
    "zindex": ZINDEX,
    "breakpoints": BREAKPOINTS,
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_gradient(start_color: str, end_color: str, angle: int = 135) -> str:
    """Generate CSS gradient string."""
    return f"linear-gradient({angle}deg, {start_color}, {end_color})"


def get_glow_shadow(color: str, intensity: float = 0.4) -> str:
    """Generate neon glow shadow."""
    # Extract RGB from hex
    rgb = tuple(int(color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    return f"0 0 20px rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {intensity})"


def get_responsive_padding(base: str, sm: str = None, lg: str = None) -> dict:
    """Generate responsive padding object."""
    return {
        "default": SPACING.get(base, base),
        "md": SPACING.get(sm or base, sm or base),
        "lg": SPACING.get(lg or base, lg or base),
    }


if __name__ == "__main__":
    # Print design system for reference
    print("🎨 Arcade.XYZ Gen Z Design System")
    print("=" * 50)
    print("\nColors:")
    for name, value in COLORS.items():
        print(f"  {name}: {value}")
    print("\nComponents:")
    for name in COMPONENTS.keys():
        print(f"  ✓ {name}")
    print("\nAnimations:")
    for name in ANIMATIONS.keys():
        print(f"  ✓ {name}")
