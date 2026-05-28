import os
import math
import random
import logging
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from backend.app.config import settings

logger = logging.getLogger(__name__)

class VideoEngine:
    def __init__(self):
        self.fps = 24
        self.loop_duration = 10  # 10 seconds loop
        self.total_frames = self.fps * self.loop_duration  # 240 frames

    def draw_radial_gradient(self, width: int, height: int, center_x: float, center_y: float, color1: tuple, color2: tuple) -> Image.Image:
        """
        Generates a smooth radial color gradient.
        """
        x = np.arange(width)
        y = np.arange(height)
        xx, yy = np.meshgrid(x, y)
        
        dist = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        factor = np.clip(dist / (max_dist * 0.75), 0.0, 1.0)
        
        r = (color1[0] * (1.0 - factor) + color2[0] * factor).astype(np.uint8)
        g = (color1[1] * (1.0 - factor) + color2[1] * factor).astype(np.uint8)
        b = (color1[2] * (1.0 - factor) + color2[2] * factor).astype(np.uint8)
        
        rgb = np.stack((r, g, b), axis=2)
        return Image.fromarray(rgb)

    def generate_loop_video(self, output_path: str, theme: str = "sacred_geometry", video_format: str = "long_form"):
        """
        Generates the 10-second looping abstract visual video based on a selected theme.
        Pipes raw PNG frames into FFmpeg to encode the video.
        """
        logger.info(f"Generating 10-second loop ({video_format}) with theme '{theme}' at: {output_path}")
        
        # Determine canvas size
        if video_format == "short_form":
            width, height = 720, 1280
        else:
            width, height = 1280, 720
            
        # Launch FFmpeg process to write video from raw frame pipe
        cmd = [
            "ffmpeg", "-y",
            "-f", "image2pipe",
            "-vcodec", "png",
            "-r", str(self.fps),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            output_path
        ]
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        cx, cy = width / 2.0, height / 2.0
        max_dist = math.sqrt(cx**2 + cy**2)
        
        # Pre-seed deterministic random parameters for particles/movement per theme
        random.seed(42)
        np.random.seed(42)
        
        # Pre-generate particles based on theme
        particles = []
        if theme in ["sacred_geometry", "cosmic_nebula", "starlight_vortex", "ocean_depths", "aura_glow"]:
            num_parts = 60 if theme in ["cosmic_nebula", "starlight_vortex"] else 35
            for i in range(num_parts):
                particles.append({
                    "radius": random.uniform(2, 6),
                    "base_r": random.uniform(20, width * 0.45),
                    "base_angle": random.uniform(0, 2 * math.pi),
                    "speed_multiplier": random.choice([-2, -1, 1, 2]),
                    "pulse_freq": random.choice([1, 2, 3]),
                    "w_freq": random.uniform(1.5, 4.0),
                    "base_x": random.uniform(50, width - 50),
                    "base_y": random.uniform(50, height - 50),
                    "color": random.choice([
                        (100, 180, 255, 120),  # Blue
                        (180, 100, 255, 120),  # Purple
                        (100, 255, 220, 120),  # Teal
                        (255, 120, 200, 120)   # Pink
                    ])
                })
        elif theme == "dreamscape":
            # 10 large drifting blobs
            for i in range(10):
                particles.append({
                    "drift_r": random.uniform(30, 90),
                    "base_r": random.uniform(80, 160),
                    "phase": random.uniform(0, 2 * math.pi),
                    "speed": random.choice([-1, 1]) * random.uniform(0.5, 1.5),
                    "color": (
                        random.randint(120, 255),
                        random.randint(80, 200),
                        random.randint(180, 255),
                        35
                    )
                })

        # Frame loop
        for frame_idx in range(self.total_frames):
            # t goes smoothly from 0 to 2*pi
            t = (frame_idx / self.total_frames) * 2 * math.pi
            
            # 1. Generate gradient background based on theme
            color_c, color_edge = self.get_theme_colors(theme, t)
            
            # Oscillate gradient center slightly for dynamic feeling
            bg_cx = cx + (width * 0.05) * math.sin(t)
            bg_cy = cy + (height * 0.05) * math.cos(t)
            
            frame_img = self.draw_radial_gradient(width, height, bg_cx, bg_cy, color_c, color_edge)
            
            # 2. Setup translucent overlay for drawing elements
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # 3. Draw theme-specific visual layers
            self.draw_theme_layer(draw, overlay, theme, t, width, height, cx, cy, max_dist, particles)
            
            # 4. Composite drawing layers onto base background
            frame_img.paste(overlay, (0, 0), overlay)
            
            # 5. Apply dreamlike softening blur
            frame_img = frame_img.filter(ImageFilter.GaussianBlur(1.0))
            
            # 6. Pipe frame to FFmpeg
            frame_img.save(process.stdin, "PNG")
            
        process.stdin.close()
        stderr = process.stderr.read()
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg loop video generation failed: {stderr.decode('utf-8')}")
            raise Exception("FFmpeg failed to create looping video.")

    def get_theme_colors(self, theme: str, t: float) -> tuple:
        """
        Defines beautiful color palette pairs (center, edge) for each of the 19 themes.
        All colors loop perfectly since they depend on sin/cos of t.
        """
        # Default fallback (Deep space violet-blue)
        color_c = (int(25 + 10 * math.sin(t)), int(15 + 5 * math.cos(t)), int(45 + 15 * math.sin(t)))
        color_edge = (5, 5, 12)
        
        if theme == "cosmic_nebula":
            color_c = (int(15 + 5 * math.sin(t)), int(8 + 3 * math.cos(t)), int(30 + 10 * math.sin(t)))
            color_edge = (2, 2, 6)
        elif theme == "aura_glow":
            # Shifts between deep teal-blue and violet
            color_c = (int(20 + 15 * math.sin(t)), int(30 + 10 * math.cos(t)), int(45 + 15 * math.sin(t)))
            color_edge = (4, 6, 15)
        elif theme == "quantum_tunnel":
            color_c = (int(10 + 5 * math.sin(t)), int(10 + 5 * math.cos(t)), int(35 + 10 * math.sin(t)))
            color_edge = (0, 0, 2)
        elif theme == "chakra_alignment":
            color_c = (int(30 + 15 * math.sin(t)), int(10 + 5 * math.cos(t)), int(40 + 10 * math.sin(t)))
            color_edge = (5, 3, 10)
        elif theme == "zen_waves":
            # Calming charcoal/slate tones
            color_c = (int(28 + 4 * math.sin(t)), int(28 + 4 * math.sin(t)), int(32 + 4 * math.cos(t)))
            color_edge = (10, 10, 12)
        elif theme == "dna_helix":
            color_c = (int(8 + 4 * math.sin(t)), int(26 + 8 * math.cos(t)), int(32 + 8 * math.sin(t)))
            color_edge = (5, 8, 12)
        elif theme == "fibonacci_spiral":
            # Deep golden copper shades
            color_c = (int(35 + 10 * math.sin(t)), int(22 + 6 * math.cos(t)), int(12 + 4 * math.sin(t)))
            color_edge = (6, 4, 3)
        elif theme == "subconscious_eye":
            color_c = (int(25 + 10 * math.sin(t)), int(10 + 5 * math.cos(t)), int(50 + 15 * math.sin(t)))
            color_edge = (3, 2, 8)
        elif theme == "astral_projection":
            color_c = (int(10 + 5 * math.sin(t)), int(15 + 5 * math.cos(t)), int(35 + 10 * math.sin(t)))
            color_edge = (2, 3, 8)
        elif theme == "fractal_canopy":
            color_c = (int(8 + 4 * math.sin(t)), int(30 + 8 * math.cos(t)), int(16 + 6 * math.sin(t)))
            color_edge = (3, 6, 4)
        elif theme == "ocean_depths":
            color_c = (int(6 + 3 * math.sin(t)), int(20 + 6 * math.cos(t)), int(38 + 10 * math.sin(t)))
            color_edge = (2, 4, 10)
        elif theme == "starlight_vortex":
            color_c = (int(32 + 12 * math.sin(t)), int(18 + 6 * math.cos(t)), int(48 + 12 * math.sin(t)))
            color_edge = (3, 2, 8)
        elif theme == "crystal_grid":
            color_c = (int(12 + 6 * math.sin(t)), int(32 + 8 * math.cos(t)), int(48 + 10 * math.sin(t)))
            color_edge = (4, 6, 12)
        elif theme == "buddha_halo":
            color_c = (int(42 + 12 * math.sin(t)), int(32 + 8 * math.cos(t)), int(12 + 4 * math.sin(t)))
            color_edge = (8, 6, 4)
        elif theme == "dreamscape":
            color_c = (int(45 + 10 * math.sin(t)), int(25 + 8 * math.cos(t)), int(42 + 10 * math.sin(t)))
            color_edge = (10, 8, 14)
        elif theme == "eternal_torus":
            color_c = (int(5 + 2 * math.sin(t)), int(32 + 8 * math.cos(t)), int(22 + 6 * math.sin(t)))
            color_edge = (2, 5, 3)
        elif theme == "chladni_patterns":
            color_c = (int(12 + 4 * math.sin(t)), int(35 + 8 * math.cos(t)), int(35 + 8 * math.sin(t)))
            color_edge = (6, 6, 8)
        elif theme == "hypnotic_spiral":
            color_c = (int(18 + 6 * math.sin(t)), int(10 + 4 * math.cos(t)), int(28 + 8 * math.sin(t)))
            color_edge = (0, 0, 0)
            
        return color_c, color_edge

    def draw_theme_layer(self, draw: ImageDraw.Draw, overlay: Image.Image, theme: str, t: float, width: int, height: int, cx: float, cy: float, max_dist: float, particles: list):
        """
        Draws the vector graphics layer for the selected theme.
        """
        if theme == "sacred_geometry":
            # Original theme: Rotating concentric mandalas with intersecting circles
            mandala_radius = (width * 0.15) + 10 * math.sin(t * 2)
            rotation = t * 0.25
            
            draw.ellipse([cx - mandala_radius, cy - mandala_radius, cx + mandala_radius, cy + mandala_radius], outline=(130, 100, 255, 35), width=2)
            draw.ellipse([cx - mandala_radius*0.6, cy - mandala_radius*0.6, cx + mandala_radius*0.6, cy + mandala_radius*0.6], outline=(100, 180, 255, 25), width=1)
            
            num_petals = 16
            for k in range(num_petals):
                theta = rotation + k * (2 * math.pi / num_petals)
                x1 = cx + mandala_radius * math.cos(theta)
                y1 = cy + mandala_radius * math.sin(theta)
                draw.line([(cx, cy), (x1, y1)], fill=(120, 120, 255, 20), width=1)
                
                # Outer petals
                petal_cx = cx + (mandala_radius * 0.55) * math.cos(theta)
                petal_cy = cy + (mandala_radius * 0.55) * math.sin(theta)
                petal_cr = width * 0.035
                draw.ellipse([petal_cx - petal_cr, petal_cy - petal_cr, petal_cx + petal_cr, petal_cy + petal_cr], outline=(150, 100, 255, 18), width=1)
                
            # Floating stars
            for p in particles:
                angle = p["base_angle"] + p["speed_multiplier"] * (t * 0.5)
                orbit_offset = p["base_r"] + 15 * math.sin(p["pulse_freq"] * t)
                px = cx + orbit_offset * math.cos(angle)
                py = cy + orbit_offset * math.sin(angle)
                r = p["radius"]
                opacity = int(100 + 60 * math.sin(t * p["pulse_freq"]))
                color = (p["color"][0], p["color"][1], p["color"][2], opacity)
                draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

        elif theme == "cosmic_nebula":
            # Soft blurs representing nebulae clouds
            nebula_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            nebula_draw = ImageDraw.Draw(nebula_layer)
            
            # Nebula blobs
            blob1_x = cx + (width * 0.12) * math.cos(t)
            blob1_y = cy + (height * 0.08) * math.sin(t)
            r1 = width * 0.18
            nebula_draw.ellipse([blob1_x - r1, blob1_y - r1, blob1_x + r1, blob1_y + r1], fill=(140, 50, 255, 40))
            
            blob2_x = cx - (width * 0.15) * math.sin(t * 0.8)
            blob2_y = cy + (height * 0.10) * math.cos(t * 0.8)
            r2 = width * 0.22
            nebula_draw.ellipse([blob2_x - r2, blob2_y - r2, blob2_x + r2, blob2_y + r2], fill=(0, 180, 220, 30))
            
            blob3_x = cx + (width * 0.05) * math.sin(t * 1.5)
            blob3_y = cy - (height * 0.12) * math.cos(t * 1.5)
            r3 = width * 0.15
            nebula_draw.ellipse([blob3_x - r3, blob3_y - r3, blob3_x + r3, blob3_y + r3], fill=(230, 80, 180, 25))
            
            # Blurring the nebula blobs heavily
            nebula_layer = nebula_layer.filter(ImageFilter.GaussianBlur(width * 0.08))
            overlay.paste(nebula_layer, (0,0), nebula_layer)
            
            # Draw moving stars
            for p in particles:
                r = (p["base_r"] + (t / (2*math.pi)) * (width * 0.45)) % (width * 0.45)
                opacity = int(220 * math.sin(math.pi * (r / (width * 0.45))))
                px = cx + r * math.cos(p["base_angle"])
                py = cy + r * math.sin(p["base_angle"])
                rad = p["radius"] * 0.8
                draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=(255, 255, 255, opacity))

        elif theme == "aura_glow":
            # Breathing light field rings
            for i in range(1, 6):
                r = (width * 0.07) * i * (1.0 + 0.08 * math.sin(t * 1.5 + i))
                opacity = int(75 - 10*i + 15 * math.sin(t * 2.0 + i))
                if opacity < 5: opacity = 5
                
                # Draw ring outline multiple times for simulated glow
                for glow_offset in range(4):
                    draw.ellipse([cx - r - glow_offset, cy - r - glow_offset, cx + r + glow_offset, cy + r + glow_offset], 
                                 outline=(120 + 20*i, 80 + 30*i, 255, opacity // (glow_offset + 1)), width=1)
            
            # Gentle pulsing aura particles
            for p in particles:
                px = p["base_x"] + 15 * math.cos(t + p["base_angle"])
                py = p["base_y"] + 15 * math.sin(t * p["pulse_freq"] * 0.5)
                r = p["radius"] * 1.5
                opacity = int(70 + 40 * math.sin(t * p["pulse_freq"]))
                color = (p["color"][0], p["color"][1], p["color"][2], opacity)
                draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

        elif theme == "quantum_tunnel":
            # Endless concentric geometric rings and polygons flowing towards screen
            num_walls = 10
            for i in range(num_walls):
                frac = ((t / (2*math.pi)) + i/num_walls) % 1.0
                r = frac * (width * 0.6)
                opacity = int(255 * (1.0 - frac) * frac * 3.8)
                if opacity < 0: opacity = 0
                
                # Alternating shapes: Hexagons and Circles
                color = (130, 100, 255, opacity) if i % 2 == 0 else (100, 220, 255, opacity)
                
                if i % 2 == 0:
                    # Draw Hexagon
                    points = []
                    for k in range(6):
                        angle = k * (math.pi / 3) + t * 0.12
                        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                    draw.polygon(points, outline=color, width=2)
                else:
                    # Draw Circle
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)

        elif theme == "chakra_alignment":
            # Draw vertical central spine channel (Sushumna Nadi)
            draw.line([(cx, 0), (cx, height)], fill=(255, 255, 255, 12), width=2)
            
            # Define 7 Chakras
            chakras = [
                {"name": "Crown", "color": (180, 80, 255), "y_pct": 0.15},      # Violet
                {"name": "Third Eye", "color": (100, 80, 255), "y_pct": 0.265},   # Indigo
                {"name": "Throat", "color": (80, 180, 255), "y_pct": 0.38},     # Blue
                {"name": "Heart", "color": (100, 220, 100), "y_pct": 0.495},    # Green
                {"name": "Solar Plexus", "color": (255, 220, 60), "y_pct": 0.61}, # Yellow
                {"name": "Sacral", "color": (255, 140, 50), "y_pct": 0.725},    # Orange
                {"name": "Root", "color": (255, 60, 60), "y_pct": 0.84}         # Red
            ]
            
            for idx, ch in enumerate(chakras):
                ch_y = height * ch["y_pct"]
                ch_color = ch["color"]
                
                # Active pulsing size
                r_base = width * 0.02 + 3 * math.sin(t * 2 + idx)
                r_glow = r_base * (1.3 + 0.15 * math.sin(t * 3 - idx))
                
                # Glow ring
                draw.ellipse([cx - r_glow, ch_y - r_glow, cx + r_glow, ch_y + r_glow], outline=(ch_color[0], ch_color[1], ch_color[2], 30), width=1)
                # Core sphere
                draw.ellipse([cx - r_base, ch_y - r_base, cx + r_base, ch_y + r_base], fill=(ch_color[0], ch_color[1], ch_color[2], 180))
                
                # Concentric petals / geometric markers
                num_petals = 4 + 2 * idx
                petal_rot = t * (0.2 + 0.05 * idx)
                petal_length = r_glow * 1.2
                for p_idx in range(num_petals):
                    p_angle = petal_rot + p_idx * (2 * math.pi / num_petals)
                    px = cx + petal_length * math.cos(p_angle)
                    py = ch_y + petal_length * math.sin(p_angle)
                    draw.line([(cx, ch_y), (px, py)], fill=(ch_color[0], ch_color[1], ch_color[2], 25), width=1)

        elif theme == "zen_waves":
            # Ripple waves radiating from the center
            num_waves = 12
            for i in range(num_waves):
                r = ((t / (2 * math.pi)) * (width * 0.08) + i * (width * 0.05)) % (width * 0.5)
                opacity = int(120 * (1.0 - r / (width * 0.5)))
                if opacity < 0: opacity = 0
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(200, 200, 220, opacity), width=1)
            
            # Wavy raked lines (Zen garden concept)
            num_lines = 15
            for i in range(num_lines):
                y_pos = height * 0.05 + i * (height * 0.9 / num_lines)
                points = []
                for x_pos in range(0, width + 20, 20):
                    # Ripple oscillation factor
                    dy = 12 * math.sin(x_pos / 90.0 + t + i * 0.5)
                    points.append((x_pos, y_pos + dy))
                draw.line(points, fill=(180, 180, 200, 15), width=1)

        elif theme == "dna_helix":
            # Spinning glowing DNA double helix structure
            num_nodes = 22
            helix_width = width * 0.12
            rotation_speed = 1.3
            
            for i in range(num_nodes):
                node_y = height * 0.08 + i * (height * 0.84 / num_nodes)
                # Shifting phase along helix length
                phase = (node_y / 90.0) * math.pi + t * rotation_speed
                
                x1 = cx + helix_width * math.cos(phase)
                x2 = cx - helix_width * math.cos(phase)
                
                # Base pair bridge
                opacity = int(60 + 40 * math.sin(phase))
                draw.line([(x1, node_y), (x2, node_y)], fill=(120, 160, 255, opacity), width=1)
                
                # Glowing nodes
                r_node = 6 + 1.5 * math.sin(phase)
                draw.ellipse([x1 - r_node, node_y - r_node, x1 + r_node, node_y + r_node], fill=(80, 180, 255, 210))
                draw.ellipse([x2 - r_node, node_y - r_node, x2 + r_node, node_y + r_node], fill=(255, 100, 160, 210))

        elif theme == "fibonacci_spiral":
            # Fibonacci sunflower seed spiral expanding outwards
            # Loop details
            num_seeds = 320
            spiral_rot = t * 0.4
            
            for idx in range(num_seeds):
                # Polar equations for Fermat's spiral
                r = 6.0 * math.sqrt(idx) * (width / 1280.0)
                if r > width * 0.5:
                    continue
                # Golden angle rotation
                angle = idx * 2.39996 + spiral_rot
                
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                
                opacity = int(220 * (1.0 - r / (width * 0.5)))
                if opacity < 5: opacity = 5
                
                seed_r = max(1.5, 3.5 * (1.0 - r / (width * 0.5)))
                draw.ellipse([px - seed_r, py - seed_r, px + seed_r, py + seed_r], fill=(245, 195, 80, opacity))

        elif theme == "subconscious_eye":
            # The central hypnotic Third Eye
            eye_w = width * 0.18
            eye_h = height * 0.10 * (1.0 + 0.05 * math.sin(t * 2))
            
            # Draw eye contour lines (upper/lower eyelids)
            pts_upper = []
            pts_lower = []
            steps = 40
            for k in range(steps + 1):
                dx = -eye_w + (2 * eye_w * k / steps)
                # Parabolic curve factor
                factor = (eye_w**2 - dx**2) / (eye_w**2)
                pts_upper.append((cx + dx, cy - eye_h * factor))
                pts_lower.append((cx + dx, cy + eye_h * factor))
                
            draw.line(pts_upper, fill=(180, 140, 255, 120), width=2)
            draw.line(pts_lower, fill=(180, 140, 255, 120), width=2)
            
            # Iris
            iris_r = width * 0.055
            draw.ellipse([cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r], outline=(100, 200, 255, 100), width=1)
            
            # Pupil (Pulsing in size with breath frequency)
            pupil_r = width * 0.024 + 4.5 * math.sin(t * 2.0)
            draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r], fill=(12, 10, 28, 255))
            
            # Concentric halos behind the eye
            halo_r = width * 0.13 + 10 * math.sin(t)
            draw.ellipse([cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r], outline=(150, 100, 255, 20), width=1)
            
            # Light rays radiating from pupil
            num_rays = 16
            ray_length = width * 0.32
            ray_rot = t * 0.08
            for r_idx in range(num_rays):
                r_angle = ray_rot + r_idx * (2 * math.pi / num_rays)
                rx1 = cx + pupil_r * math.cos(r_angle)
                ry1 = cy + pupil_r * math.sin(r_angle)
                rx2 = cx + ray_length * math.cos(r_angle)
                ry2 = cy + ray_length * math.sin(r_angle)
                draw.line([(rx1, ry1), (rx2, ry2)], fill=(200, 150, 255, 10), width=1)

        elif theme == "astral_projection":
            # Converging perspective grid lines
            num_rays = 16
            for r_idx in range(num_rays):
                angle = r_idx * (2 * math.pi / num_rays)
                rx = cx + width * math.cos(angle)
                ry = cy + height * math.sin(angle)
                draw.line([(cx, cy), (rx, ry)], fill=(100, 150, 255, 20), width=1)
                
            # Floating boxes or horizon panels expanding outwards
            num_gates = 8
            for i in range(num_gates):
                frac = ((t / (2*math.pi)) + i/num_gates) % 1.0
                r_w = frac * (width * 0.5)
                r_h = frac * (height * 0.5)
                
                opacity = int(140 * (1.0 - frac) * frac * 4.0)
                if opacity < 0: opacity = 0
                draw.rectangle([cx - r_w, cy - r_h, cx + r_w, cy + r_h], outline=(100, 200, 255, opacity), width=1)

        elif theme == "fractal_canopy":
            # Symmetrical breathing fractal tree (max_depth restricted to 6 for speed)
            def draw_branch(draw_obj, x1, y1, angle, depth, max_depth, t_val):
                if depth > max_depth:
                    return
                # Length contracts with depth
                length = (height * 0.16) * (0.75 ** depth) * (1.0 + 0.04 * math.sin(t_val + depth))
                x2 = x1 + length * math.cos(angle)
                y2 = y1 + length * math.sin(angle)
                
                opacity = int(220 * (1.0 - depth/max_depth))
                # Forest colors shifting
                color = (int(100 + depth*20), int(255 - depth*20), int(140 + depth*10), opacity)
                draw_obj.line([(x1, y1), (x2, y2)], fill=color, width=max(1, max_depth - depth))
                
                # Branch division angle oscillation
                angle_spread = 0.42 + 0.08 * math.sin(t_val * 1.5 + depth)
                draw_branch(draw_obj, x2, y2, angle - angle_spread, depth + 1, max_depth, t_val)
                draw_branch(draw_obj, x2, y2, angle + angle_spread, depth + 1, max_depth, t_val)
                
            draw_branch(draw, cx, height * 0.95, -math.pi / 2, 0, 6, t)

        elif theme == "ocean_depths":
            # Ocean waves shifting at top/bottom, bioluminescent bubble particles rising
            # Bottom Layer waves
            y_base = height * 0.88
            points1 = [(0, height), (0, y_base)]
            points2 = [(0, height), (0, y_base + height * 0.03)]
            
            for x_pos in range(0, width + 30, 30):
                dy1 = 15 * math.sin(x_pos / 110.0 + t * 1.2)
                dy2 = 10 * math.sin(x_pos / 80.0 - t * 1.5)
                points1.append((x_pos, y_base + dy1))
                points2.append((x_pos, y_base + height * 0.03 + dy2))
                
            points1.append((width, height))
            points2.append((width, height))
            
            draw.polygon(points1, fill=(20, 80, 160, 20))
            draw.polygon(points2, fill=(10, 50, 110, 25))
            
            # Rising bubble particles
            for p in particles:
                by = (p["base_y"] - (t / (2*math.pi)) * height) % height
                bx = p["base_x"] + 15 * math.sin(t * p["w_freq"])
                rad = p["radius"] * 0.9
                opacity = int(180 * math.sin(math.pi * (by / height)))
                if opacity < 5: opacity = 5
                draw.ellipse([bx - rad, by - rad, bx + rad, by + rad], outline=(130, 255, 230, opacity), width=1)

        elif theme == "starlight_vortex":
            # Particles spiraling inwards into a void center
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(0, 0, 0, 255))
            
            for p in particles:
                r = (p["base_r"] - (t / (2*math.pi)) * (width * 0.5)) % (width * 0.5)
                # Add swirling angle offsets
                angle = p["base_angle"] + 4.8 * (1.0 - r / (width * 0.5)) + t * 0.7
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                
                opacity = int(240 * math.sin(math.pi * (r / (width * 0.5))))
                if opacity < 5: opacity = 5
                rad = max(1.0, p["radius"] * (r / (width * 0.5)))
                
                draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=(190, 150, 255, opacity))

        elif theme == "crystal_grid":
            # Rotating crystal facets structure
            grid_r = width * 0.16
            inner_r = width * 0.075
            rot_t = t * 0.18
            
            # 6 Vertices on Outer Hexagon
            outer_v = []
            for k in range(6):
                ang = rot_t + k * (math.pi / 3.0)
                outer_v.append((cx + grid_r * math.cos(ang), cy + grid_r * math.sin(ang)))
                
            # 6 Vertices on Inner Hexagon
            inner_v = []
            for k in range(6):
                ang = -rot_t + k * (math.pi / 3.0)
                inner_v.append((cx + inner_r * math.cos(ang), cy + inner_r * math.sin(ang)))
                
            # Draw translucent lines connecting crystal nodes
            for o_idx in range(6):
                # Outer border
                draw.line([outer_v[o_idx], outer_v[(o_idx + 1) % 6]], fill=(140, 220, 255, 60), width=1)
                # Outer to inner connections
                draw.line([outer_v[o_idx], inner_v[o_idx]], fill=(140, 220, 255, 30), width=1)
                draw.line([outer_v[o_idx], inner_v[(o_idx + 1) % 6]], fill=(140, 220, 255, 20), width=1)
                # Inner connections
                draw.line([inner_v[o_idx], inner_v[(o_idx + 1) % 6]], fill=(100, 180, 255, 45), width=1)
                # Inner to center
                draw.line([inner_v[o_idx], (cx, cy)], fill=(100, 180, 255, 35), width=1)
                
            # Draw semi-transparent facets for crystalline reflections
            for o_idx in range(6):
                draw.polygon([outer_v[o_idx], inner_v[o_idx], inner_v[(o_idx+1)%6]], fill=(100, 180, 255, 12))
                
            # Draw vertices spheres
            for v in outer_v + inner_v + [(cx, cy)]:
                draw.ellipse([v[0]-3, v[1]-3, v[0]+3, v[1]+3], fill=(225, 245, 255, 160))

        elif theme == "buddha_halo":
            # Intricate overlapping Buddhist concentric halos
            # Ring 1
            r1 = width * 0.08
            draw.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], outline=(245, 200, 80, 45), width=1)
            
            # Ring 2: Rotating spokes
            r2 = width * 0.12
            num_spokes = 24
            spoke_rot = t * 0.28
            for k in range(num_spokes):
                ang = spoke_rot + k * (2 * math.pi / num_spokes)
                x1 = cx + (r2 - 4) * math.cos(ang)
                y1 = cy + (r2 - 4) * math.sin(ang)
                x2 = cx + (r2 + 4) * math.cos(ang)
                y2 = cy + (r2 + 4) * math.sin(ang)
                draw.line([(x1, y1), (x2, y2)], fill=(245, 195, 80, 50), width=1)
                
            # Ring 3: Concentric dotted wheel
            r3 = width * 0.16 + 5 * math.sin(t * 2)
            num_dots = 40
            dot_rot = -t * 0.15
            for k in range(num_dots):
                ang = dot_rot + k * (2 * math.pi / num_dots)
                dx = cx + r3 * math.cos(ang)
                dy = cy + r3 * math.sin(ang)
                draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 215, 120, 90))
                
            # Outer Ring 4
            r4 = width * 0.20
            draw.ellipse([cx - r4, cy - r4, cx + r4, cy + r4], outline=(245, 180, 80, 30), width=2)

        elif theme == "dreamscape":
            # Soft blurs of light moving and overlapping
            blob_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            blob_draw = ImageDraw.Draw(blob_layer)
            
            for idx, p in enumerate(particles):
                drift_dist = p["drift_r"]
                angle = p["phase"] + p["speed"] * (t * 0.5)
                # Compute coordinates
                bx = cx + drift_dist * math.cos(angle)
                by = cy + drift_dist * math.sin(angle * 1.3)
                # Pulsing radius
                rad = p["base_r"] * (1.0 + 0.12 * math.sin(t * 1.8 + idx))
                blob_draw.ellipse([bx - rad, by - rad, bx + rad, by + rad], fill=p["color"])
                
            # Blurring heavily
            blob_layer = blob_layer.filter(ImageFilter.GaussianBlur(width * 0.08))
            overlay.paste(blob_layer, (0,0), blob_layer)

        elif theme == "eternal_torus":
            # 3D Torus projection wireframe structure
            num_u, num_v = 10, 16
            R = width * 0.16
            r = width * 0.05
            
            rot_y = t * 0.15
            rot_x = 0.6 + 0.15 * math.sin(t)
            
            grid_points = {}
            for u in range(num_u):
                ang_u = u * (2.0 * math.pi / num_u)
                for v in range(num_v):
                    ang_v = v * (2.0 * math.pi / num_v)
                    
                    # 3D Coordinates
                    tx = (R + r * math.cos(ang_v)) * math.cos(ang_u)
                    ty = (R + r * math.cos(ang_v)) * math.sin(ang_u)
                    tz = r * math.sin(ang_v)
                    
                    # Rotate around Y axis
                    x_r = tx * math.cos(rot_y) - tz * math.sin(rot_y)
                    z_r = tx * math.sin(rot_y) + tz * math.cos(rot_y)
                    # Rotate around X axis
                    y_r = ty * math.cos(rot_x) - z_r * math.sin(rot_x)
                    
                    # Store 2D projection
                    grid_points[(u, v)] = (cx + x_r, cy + y_r)
                    
            # Draw wireframe lines
            for u in range(num_u):
                for v in range(num_v):
                    curr = grid_points[(u, v)]
                    nxt_u = grid_points[((u + 1) % num_u, v)]
                    nxt_v = grid_points[(u, (v + 1) % num_v)]
                    
                    draw.line([curr, nxt_u], fill=(100, 255, 180, 35), width=1)
                    draw.line([curr, nxt_v], fill=(100, 255, 180, 25), width=1)

        elif theme == "chladni_patterns":
            # 2D vibration nodal plate grid pattern simulation
            grid_sz = 28
            w_span = width * 0.45
            h_span = height * 0.45
            
            for gx in range(-grid_sz // 2, grid_sz // 2 + 1):
                px = cx + (gx / (grid_sz / 2)) * w_span
                for gy in range(-grid_sz // 2, grid_sz // 2 + 1):
                    py = cy + (gy / (grid_sz / 2)) * h_span
                    
                    # Chladni frequency plate equation
                    n, m = 3, 2
                    val = math.cos(n * math.pi * gx/(grid_sz/2)) * math.cos(m * math.pi * gy/(grid_sz/2)) - \
                          math.cos(m * math.pi * gx/(grid_sz/2)) * math.cos(n * math.pi * gy/(grid_sz/2))
                          
                    # Pulse oscillation over time
                    intensity = val * math.sin(t)
                    dot_radius = abs(intensity) * 5.5
                    
                    if dot_radius > 0.8:
                        opacity = int(180 * abs(intensity))
                        if opacity < 5: opacity = 5
                        draw.ellipse([px - dot_radius, py - dot_radius, px + dot_radius, py + dot_radius], 
                                     fill=(90, 210, 210, opacity))

        elif theme == "hypnotic_spiral":
            # High contrast classic hypnotic spiral rotating inwards
            spiral_pts = []
            num_pts = 420
            spiral_rot = -t * 2.2 # Direction of spin
            
            for i in range(num_pts):
                theta = i * 0.12
                r = theta * (width * 0.48 / 50.0)
                if r > width * 0.65:
                    continue
                angle = theta + spiral_rot
                spiral_pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                
            # Draw spiral path
            if len(spiral_pts) > 1:
                draw.line(spiral_pts, fill=(170, 130, 255, 180), width=3)
                
            # Add secondary outer spiral
            spiral_pts_2 = []
            for i in range(num_pts):
                theta = i * 0.12
                r = theta * (width * 0.48 / 50.0)
                if r > width * 0.65:
                    continue
                angle = theta + spiral_rot + math.pi # Opposite arm
                spiral_pts_2.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                
            if len(spiral_pts_2) > 1:
                draw.line(spiral_pts_2, fill=(100, 210, 255, 100), width=2)

    def render_final_video(self, loop_video_path: str, audio_path: str, output_path: str) -> str:
        """
        Combines the 10-second looping video with the final audio.
        Uses stream-looping and stream copying (-c:v copy) to render almost instantaneously.
        """
        logger.info(f"Muxing loop video with final audio...")
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", loop_video_path,
            "-i", audio_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"FFmpeg final video render failed: {result.stderr.decode('utf-8')}")
            raise Exception("FFmpeg failed to render final video.")
            
        return output_path

video_engine = VideoEngine()
