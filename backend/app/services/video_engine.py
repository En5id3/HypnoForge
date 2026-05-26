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
        self.width = 1280
        self.height = 720
        self.fps = 24
        self.loop_duration = 10  # 10 seconds loop
        self.total_frames = self.fps * self.loop_duration  # 240 frames

    def draw_radial_gradient(self, width: int, height: int, center_x: float, center_y: float, color1: tuple, color2: tuple) -> Image.Image:
        """
        Generates a smooth radial color gradient.
        """
        # Create a coordinate grid
        x = np.arange(width)
        y = np.arange(height)
        xx, yy = np.meshgrid(x, y)
        
        # Calculate distances from center
        dist = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        # Normalize distance
        factor = np.clip(dist / (max_dist * 0.7), 0.0, 1.0)
        
        # Blend colors
        r = (color1[0] * (1.0 - factor) + color2[0] * factor).astype(np.uint8)
        g = (color1[1] * (1.0 - factor) + color2[1] * factor).astype(np.uint8)
        b = (color1[2] * (1.0 - factor) + color2[2] * factor).astype(np.uint8)
        
        # Create RGB array
        rgb = np.stack((r, g, b), axis=2)
        return Image.fromarray(rgb)

    def generate_loop_video(self, output_path: str):
        """
        Generates the 10-second looping abstract cosmic video.
        Pipes raw PNG frames into FFmpeg to encode the video.
        """
        logger.info(f"Generating 10-second visual loop at: {output_path}")
        
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
        
        center_x, center_y = self.width // 2, self.height // 2
        
        # Define particles that move in looping mathematical paths
        num_particles = 35
        particles = []
        for i in range(num_particles):
            particles.append({
                "radius": np.random.uniform(2, 6),
                "orbit_r": np.random.uniform(50, 320),
                "base_angle": np.random.uniform(0, 2 * math.pi),
                "speed_multiplier": random.choice([-2, -1, 1, 2, 3]),
                "pulse_freq": random.choice([1, 2, 4]),
                "color": random.choice([
                    (100, 180, 255, 120),  # Blue
                    (180, 100, 255, 120),  # Purple
                    (100, 255, 220, 120),  # Teal
                    (255, 120, 200, 120)   # Pink
                ])
            })
            
        for frame_idx in range(self.total_frames):
            # 1. Background: slow shifting color gradient (deep space tones)
            t = (frame_idx / self.total_frames) * 2 * math.pi
            
            # Oscillate gradient center
            bg_cx = center_x + 100 * math.sin(t)
            bg_cy = center_y + 80 * math.cos(t)
            
            # Shifting deep blues and purples
            color_c = (int(25 + 10 * math.sin(t)), int(10 + 5 * math.cos(t)), int(45 + 15 * math.sin(t)))
            color_edge = (5, 5, 12)
            
            frame_img = self.draw_radial_gradient(self.width, self.height, bg_cx, bg_cy, color_c, color_edge)
            
            # 2. Overlay Layer for translucent vector graphics
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # 3. Draw Cosmic Particles
            for p in particles:
                # Calculate current position in orbit
                angle = p["base_angle"] + p["speed_multiplier"] * t
                orbit_offset = p["orbit_r"] + 15 * math.sin(p["pulse_freq"] * t)
                px = center_x + orbit_offset * math.cos(angle)
                py = center_y + orbit_offset * math.sin(angle)
                
                # Glowing circle
                r = p["radius"]
                opacity = int(100 + 50 * math.sin(t * p["pulse_freq"]))
                p_color = (p["color"][0], p["color"][1], p["color"][2], opacity)
                draw.ellipse([px - r, py - r, px + r, py + r], fill=p_color)
                
            # 4. Draw Rotating Sacred Geometry Mandala
            mandala_radius = 180 + 10 * math.sin(t * 2)
            rotation = t * 0.25 # Slow rotate
            
            # Draw concentric circular rings
            draw.ellipse([center_x - mandala_radius, center_y - mandala_radius, 
                          center_x + mandala_radius, center_y + mandala_radius], 
                          outline=(130, 100, 255, 30), width=2)
            draw.ellipse([center_x - mandala_radius*0.6, center_y - mandala_radius*0.6, 
                          center_x + mandala_radius*0.6, center_y + mandala_radius*0.6], 
                          outline=(100, 180, 255, 20), width=1)
            
            # Draw intersecting lines / petals
            num_petals = 16
            for k in range(num_petals):
                theta = rotation + k * (2 * math.pi / num_petals)
                
                # Petal loop
                x1 = center_x + mandala_radius * math.cos(theta)
                y1 = center_y + mandala_radius * math.sin(theta)
                
                # Draw elegant symmetry lines
                draw.line([(center_x, center_y), (x1, y1)], fill=(120, 120, 255, 20), width=1)
                
                # Intersecting circles
                cx = center_x + (mandala_radius * 0.55) * math.cos(theta)
                cy = center_y + (mandala_radius * 0.55) * math.sin(theta)
                cr = 40
                draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=(150, 100, 255, 15), width=1)
            
            # 5. Composite overlay onto gradient background
            frame_img.paste(overlay, (0, 0), overlay)
            
            # 6. Apply soft dreamlike filter to soften lines
            frame_img = frame_img.filter(ImageFilter.GaussianBlur(1.0))
            
            # 7. Write to stdin
            frame_img.save(process.stdin, "PNG")
            
        process.stdin.close()
        stderr = process.stderr.read()
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg loop video generation failed: {stderr.decode('utf-8')}")
            raise Exception("FFmpeg failed to create looping video.")

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
