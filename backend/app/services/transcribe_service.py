import os
import logging

logger = logging.getLogger(__name__)

class TranscribeService:
    def format_timestamp(self, seconds: float) -> str:
        """
        Converts seconds to SRT timestamp format: HH:MM:SS,mmm
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def generate_srt(self, captions: list, output_path: str):
        """
        Writes a list of captions to an SRT file.
        captions: list of dicts like [{"start": 0.0, "end": 4.5, "text": "Hello world"}]
        """
        logger.info(f"Writing subtitles to SRT: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, caption in enumerate(captions):
                start_str = self.format_timestamp(caption["start"])
                end_str = self.format_timestamp(caption["end"])
                
                f.write(f"{idx + 1}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{caption['text']}\n\n")

    def split_into_shorter_captions(self, text: str, start_time: float, duration: float) -> list:
        """
        Splits a long sentence into shorter caption chunks (around 5-8 words each)
        and distributes the duration proportionally.
        """
        words = text.split()
        if not words:
            return []
            
        words_per_caption = 6
        chunks = [words[i:i + words_per_caption] for i in range(0, len(words), words_per_caption)]
        
        captions = []
        accumulated_time = start_time
        time_per_word = duration / len(words)
        
        for chunk in chunks:
            chunk_text = " ".join(chunk)
            chunk_duration = time_per_word * len(chunk)
            
            captions.append({
                "start": accumulated_time,
                "end": accumulated_time + chunk_duration,
                "text": chunk_text
            })
            accumulated_time += chunk_duration
            
        return captions

transcribe_service = TranscribeService()
