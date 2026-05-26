import logging
import re
from backend.app.config import settings

logger = logging.getLogger(__name__)

# Core Responsible AI Principles: Safety Filtering Keywords
SAFETY_BLOCKED_KEYWORDS = [
    r"harm", r"kill", r"suicide", r"depressed", r"abuse", r"force", r"control", 
    r"manipulate", r"obey", r"slave", r"submissive", r"addiction", r"cure", r"disease"
]

class HypnosisRewriter:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")

    def validate_safety(self, prompt: str) -> tuple[bool, str]:
        """
        Google AI Principle: Be built and tested for safety.
        Checks prompt for unsafe content or clinical claims.
        """
        prompt_lower = prompt.lower()
        for pattern in SAFETY_BLOCKED_KEYWORDS:
            if re.search(pattern, prompt_lower):
                return False, (
                    "This prompt contains terminology that conflicts with our Responsible AI Safety Guidelines. "
                    "HypnoForge does not generate scripts for medical diagnostics, addiction cures, "
                    "or non-consensual behavioral controls. Please rephrase your prompt focusing on general "
                    "well-being, relaxation, sleep, or confidence."
                )
        return True, ""

    def rewrite(self, prompt: str, style: str, session_length: int) -> str:
        """
        Uses Gemini API to rewrite raw prompts into hypnotic prose.
        If no API key is present, uses a highly structured local procedural template fallback.
        """
        # Safety Check
        is_safe, safety_msg = self.validate_safety(prompt)
        if not is_safe:
            return f"[ERROR: Safety Filter] {safety_msg}"

        if self.client:
            try:
                system_instruction = (
                    "You are a professional clinical hypnotherapist and scripting expert adhering to responsible, "
                    "permissive Ericksonian therapy principles. Your suggestions must respect user agency and consent, "
                    "using permissive phrasing (e.g., 'you can choose to', 'you might notice', 'if you wish') rather than "
                    "authoritarian commands.\n\n"
                    "Your task is to write a highly effective, professional, and safe hypnosis script based on the user's prompt.\n"
                    "You must write in the specified style: Ericksonian, Direct Suggestion, NLP-inspired, Conversational, "
                    "Guided Visualization, Sleep Induction, Confidence Boost, or Anxiety Relief.\n"
                    f"The script must be structured to match a {session_length}-minute session pacing.\n\n"
                    "CRITICAL REQUIREMENTS:\n"
                    "1. Insert speed tags: `[speed:0.85]` for deep trance/sleep, `[speed:0.90]` for standard suggestions, and `[speed:1.0]` for waking state/energy.\n"
                    "2. Insert pause tags: `[pause:N]` where N is the number of seconds (between 1 and 6) for silence.\n"
                    "3. Break the script into clear stages: Introduction/Induction, Deepener, Suggestion, and Awakening/Orientation.\n"
                    "4. Add a standard accountability warning at the very start: 'Safety Notice: Do not listen to this audio while driving or operating machinery.'\n"
                    "5. Countdowns and Count-ups: Whenever counting numbers (e.g., 'Ten... nine... eight...' or 'One... two... three...'), you MUST insert a 3-second pause tag `[pause:3]` immediately before saying each number. For example: '[pause:3] Ten... [pause:3] nine...' or '[pause:3] One... [pause:3] Two...'.\n\n"
                    "Ensure the tags are written exactly as `[speed:X.XX]` and `[pause:N]` inline with the text."
                )
                
                user_prompt = f"Rewrite this prompt into a safe, permissive hypnosis script: '{prompt}' in the style: '{style}'."
                
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                    config={
                        "system_instruction": system_instruction,
                        "temperature": 0.7,
                    }
                )
                
                if response.text:
                    script = response.text.strip()
                    return self.insert_countdown_pauses(script)
            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}. Falling back to template-based script generator.")
        
        fallback_script = self._generate_fallback_script(prompt, style, session_length)
        return self.insert_countdown_pauses(fallback_script)

    def insert_countdown_pauses(self, script: str) -> str:
        """
        Post-processes generated script to ensure a [pause:3] is inserted before any counting numbers
        (digits 0-10 or English words zero-ten) in countdown/countup sequences, replacing any other pause tag if present.
        """
        num_regex = re.compile(
            r"\b(ten|nine|eight|seven|six|five|four|three|two|one|zero|10|9|8|7|6|5|4|3|2|1|0)\b", 
            re.IGNORECASE
        )
        
        new_script = []
        last_idx = 0
        
        for match in num_regex.finditer(script):
            start, end = match.span()
            
            # Skip any matches that are inside bracket tags (like [pause:2] or [speed:1.0])
            open_bracket = script.rfind('[', 0, start)
            close_bracket = script.rfind(']', 0, start)
            if open_bracket > close_bracket:
                continue
            
            # Check context following the number
            following_slice = script[end:end+15].strip()
            
            # Count context detection:
            # 1. Directly followed by ellipsis (e.g. "Ten...")
            # 2. Preceded by sentence boundary/newline AND followed by punctuation (e.g. ". One. ")
            is_countdown = False
            if following_slice.startswith("..."):
                is_countdown = True
            elif following_slice.startswith((".", ",", "!")):
                preceding_slice = script[max(0, start-25):start].strip()
                if not preceding_slice or preceding_slice.endswith((".", "!", "?", "\n", ";", "]")):
                    is_countdown = True
            
            # Check if there is already an existing pause tag immediately preceding the number
            has_existing_pause = False
            pause_val = 0
            m_pause = None
            preceding_slice = script[max(0, start-25):start]
            m_pause = re.search(r"(\[pause:(\d+)\])\s*$", preceding_slice)
            if m_pause:
                has_existing_pause = True
                pause_val = int(m_pause.group(2))
            
            if is_countdown:
                if has_existing_pause:
                    if pause_val != 3:
                        p_start = m_pause.start(1)
                        new_script.append(script[last_idx:max(0, start-25) + p_start])
                        new_script.append("[pause:3] ")
                    else:
                        new_script.append(script[last_idx:start])
                else:
                    new_script.append(script[last_idx:start])
                    new_script.append("[pause:3] ")
            else:
                new_script.append(script[last_idx:start])
                
            new_script.append(script[start:end])
            last_idx = end
            
        new_script.append(script[last_idx:])
        return "".join(new_script)

    def _generate_fallback_script(self, prompt: str, style: str, session_length: int) -> str:
        """
        Generates a structured, rich procedural script when Gemini API is unavailable.
        Ensures permissive language, clear safety warnings, and sections.
        """
        # Safety Check
        is_safe, safety_msg = self.validate_safety(prompt)
        if not is_safe:
            return f"[ERROR: Safety Filter] {safety_msg}"

        logger.info(f"Generating procedural fallback script for style: {style}")
        
        safety_warning = "[speed:1.0] Safety Notice: Please ensure you are in a safe, quiet environment. Do not listen to this session while driving or operating machinery. [pause:3]"
        
        induction = (
            "[speed:0.95] Welcome to this HypnoForge session. Find a comfortable position. "
            "You can allow your eyes to close whenever you feel ready, and take a deep, slow breath in. [pause:3] "
            "Hold it for a moment... and let it go. [pause:2] "
            "With each breath out, you might choose to feel a gentle release of tension in your shoulders, "
            "in your neck, and behind your eyes. [pause:2] "
            "There is nothing else you need to do right now. "
            "Just allow my words to guide you, selecting only the suggestions that feel right for you."
        )
        
        if style == "Sleep Induction":
            deepener = (
                "[speed:0.85] Imagine you are standing at the top of a soft, carpeted staircase. "
                "There are ten steps leading down to a deep, peaceful sleep. [pause:3] "
                "Ten... letting go of today. [pause:2] "
                "Nine... drifting down. [pause:2] "
                "Eight... feeling your eyelids grow heavy, so heavy. [pause:2] "
                "Seven... six... relaxing deeper and deeper. [pause:3] "
                "Five... halfway down, moving closer to deep comfort. [pause:2] "
                "Four... three... peaceful, calm, still. [pause:2] "
                "Two... one... zero. Sleep. Deep, restful sleep."
            )
            suggestion = (
                "[speed:0.80] Your mind is completely calm. Your body is heavy and relaxed. [pause:4] "
                "You release all thoughts of the day, trusting that your mind knows how to rest. [pause:3] "
                "As you drift off, you know you are safe, you are protected, and you are deep in comfort. [pause:4] "
                "Every breath you take carries you deeper into a beautiful, healing sleep. [pause:4] "
                "When you wake up, you will feel completely refreshed, energized, and clear."
            )
            awakening = (
                "[speed:0.75] Letting go now. Drifting into quiet sleep. [pause:5] "
                "Sleep... sleep... sleep. [pause:6] Sleep."
            )
        elif style == "Anxiety Relief":
            deepener = (
                "[speed:0.85] Imagine a warm, glowing light at the top of your head. [pause:3] "
                "It is a protective, soothing light of calm. [pause:2] "
                "As it slowly flows down through your chest, your arms, and your legs, it melts away all worries, "
                "carrying them down into the ground. [pause:3] "
                "Deepening... letting go of tension. Deeper and calmer. [pause:3] "
                "You are entering a sanctuary of complete peace within yourself."
            )
            suggestion = (
                "[speed:0.85] In this peaceful state, you recognize that anxiety is just energy moving through. [pause:3] "
                "You can observe it without fear, letting it float by like clouds in a wide sky. [pause:3] "
                "You are grounded, safe, and fully in control of your response. [pause:4] "
                "You breathe in peace, and you breathe out tension. [pause:3] "
                "Every cell in your body now remembers how to feel calm, quiet, and balanced."
            )
            awakening = (
                "[speed:0.95] In a moment, I will count from one to five to bring you back to full awareness. [pause:2] "
                "One... starting to feel the surface beneath you. "
                "Two... movement returning to your fingers and toes. "
                "Three... breathing in fresh, cool air. "
                "Four... feeling clear-headed and refreshed. "
                "Five... open your eyes, fully awake, carrying this peace with you."
            )
        elif style == "Confidence Boost":
            deepener = (
                "[speed:0.88] Picture yourself walking down a beautiful path in an ancient, quiet forest. [pause:3] "
                "With every step you take, the air becomes fresher, and you feel more connected to your strength. [pause:2] "
                "Stepping down... deeper into confidence. [pause:2] "
                "Ten steps... nine... letting go of self-doubt. [pause:2] "
                "Eight... seven... feeling a quiet power building inside. [pause:3] "
                "Six... five... four... three... two... one. Deeply relaxed, standing in your truth."
            )
            suggestion = (
                "[speed:0.85] You are worthy, you are capable, and you are strong. [pause:3] "
                "You trust your decisions. You walk with a calm certainty. [pause:3] "
                "No matter what challenges arise, you possess the resources to handle them with grace. [pause:4] "
                "You are proud of who you are, and you speak your truth clearly. [pause:3] "
                "Let this feeling of self-worth settle deep into your subconscious mind."
            )
            awakening = (
                "[speed:1.0] Preparing to wake now. [pause:2] "
                "One... feeling alive and energized. "
                "Two... stretching your limbs. "
                "Three... carrying this deep confidence forward. "
                "Four... smiling, feeling ready. "
                "Five... eyes open, fully awake and powerful!"
            )
        else: # Ericksonian / default
            deepener = (
                "[speed:0.85] And you might find that you can relax even further... without even trying. [pause:3] "
                "Because your subconscious mind knows exactly how to relax. [pause:2] "
                "You can listen, or you can let my words drift away. [pause:2] "
                "Decompose the noise, double your comfort, and sink deeper... [pause:3] "
                "Into that quiet space where positive change happens automatically."
            )
            suggestion = (
                "[speed:0.85] As you continue to explore this state, you may notice new possibilities. [pause:3] "
                "The topic of your session is: " + prompt + ". [pause:3] "
                "Allow your mind to reorganize, to find solutions, to heal. [pause:4] "
                "Like a river finding its path, your mind is creating positive, new pathways. [pause:4] "
                "You are capable of deep learning, effortless change, and profound integration."
            )
            awakening = (
                "[speed:0.95] Soon, you will bring your focus back to the present. [pause:2] "
                "One... two... feeling fresh energy return. "
                "Three... four... awakening your body and mind. "
                "Five... open your eyes, fully alert, refreshed, and aligned."
            )

        return f"{safety_warning}\n\n{induction}\n\n{deepener}\n\n{suggestion}\n\n{awakening}"

rewriter = HypnosisRewriter()
