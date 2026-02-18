# dystopian_dialogue_generator.py
import random
import os
import json

# --- Core Lore Elements ---
PLAYER_ROLE = "environmental scrubber (futuristic janitor)"
AI_IMPLANT1 = "NavBot (super old GPS bot drawing ASCII maps in your head)"
AI_IMPLANT2 = "Vizzy (broken blackmarket 'Roku' AI, only generates single images to communicate)"
SETTING = "dystopian futuristic city"
PLAYER_STATUS = "low-level, struggling to survive, often overlooked"

# --- Vocabulary for Player Inputs ---
PLAYER_SUBJECTS = [
    "NavBot", "Vizzy", "my route", "this garbage", "the building", "that drone",
    "my implant", "the street", "the air", "my next job", "this payment",
    "that strange signal", "the market", "the slums", "the corporate tower",
    "my energy levels", "this cleanup", "the weather", "the new directive",
    "the old district", "this noise"
]

PLAYER_ACTIONS_VERBS = [
    "tell me", "where's", "what's up with", "can you show", "navigate to", "check",
    "scan", "find", "get me to", "explain", "look at", "what about", "is there",
    "how do I", "why is", "help me with", "report on"
]

PLAYER_ACTIONS_NOUNS = [
    "the nearest scrap yard", "a safe path", "my next pick-up point",
    "the status of sector 7", "what Vizzy wants", "a way out of here",
    "the source of this smell", "any clean water", "my next shift",
    "who owns this area", "security patrols nearby", "the fastest route",
    "my last memory", "a hiding spot", "illegal tech dealers",
    "the black market entrance", "the highest pollution zone"
]

PLAYER_MOODS = [
    "frustrated", "tired", "curious", "suspicious", "resigned", "urgent", "hopeful", "confused", "annoyed"
]

# --- Vocabulary for AI Responses ---
# NavBot responses (often factual, directive, or map-related)
NAVBOT_RESPONSES = [
    f"{AI_IMPLANT1}: Route optimized.",
    f"{AI_IMPLANT1}: Displaying optimal path now.",
    f"{AI_IMPLANT1}: Sector 4-B, hazardous.",
    f"{AI_IMPLANT1}: Proceed north-east.",
    f"{AI_IMPLANT1}: Obstruction detected, rerouting.",
    f"{AI_IMPLANT1}: Target acquired.",
    f"{AI_IMPLANT1}: Estimated time: 0.8 cycles.",
    f"{AI_IMPLANT1}: No safe passage, warning.",
    f"{AI_IMPLANT1}: Memory corruption, path unclear.",
    f"{AI_IMPLANT1}: Recalibrating spatial data.",
    f"{AI_IMPLANT1}: Locating nearest waste disposal unit.",
    f"{AI_IMPLANT1}: Confirming destination coordinates.",
    f"{AI_IMPLANT1}: Entering new grid zone.",
    f"{AI_IMPLANT1}: Anomaly detected at 300 meters.",
    f"{AI_IMPLANT1}: Prioritizing high-contamination areas.",
    f"{AI_IMPLANT1}: Sensor readings nominal."
]

# Vizzy responses (broken, suggestive, image-like text descriptions)
VIZZY_RESPONSES = [
    f"{AI_IMPLANT2}: (CRACKLE) ...image: rusted key.",
    f"{AI_IMPLANT2}: (STATIC) ...visual: flickering neon sign.",
    f"{AI_IMPLANT2}: (GLITCH) ...display: lone scavenger.",
    f"{AI_IMPLANT2}: (BROKEN) ...graphic: empty streets.",
    f"{AI_IMPLANT2}: (BUZZ) ...frame: distant corporate tower.",
    f"{AI_IMPLANT2}: (DISTORTION) ...picture: broken servo arm.",
    f"{AI_IMPLANT2}: (ERROR) ...symbol: single blooming flower.",
    f"{AI_IMPLANT2}: (WAVERING) ...icon: a hidden pipe.",
    f"{AI_IMPLANT2}: (NOISE) ...render: glowing eyes.",
    f"{AI_IMPLANT2}: (FADE) ...flash: dark alley.",
    f"{AI_IMPLANT2}: (FRAGMENT) ...signal: discarded data chip.",
    f"{AI_IMPLANT2}: (JITTER) ...image: abandoned child's toy.",
    f"{AI_IMPLANT2}: (CORRUPTED) ...visual: crumbling wall.",
    f"{AI_IMPLANT2}: (BURST) ...display: a stack of credits.",
    f"{AI_IMPLANT2}: (SHIMMER) ...frame: a forbidden door.",
    f"{AI_IMPLANT2}: (ECHO) ...graphic: the city skyline at dawn."
]

# Combined responses, with a bias towards NavBot for general navigation
AI_RESPONSES_POOL = NAVBOT_RESPONSES * 3 + VIZZY_RESPONSES * 1

# --- Generator Function ---
def generate_dystopian_dialogue(num_pairs: int = 2500) -> list[dict]:
    """
    Generates a list of single-sentence player input/AI response pairs
    for a dystopian futuristic setting.
    """
    print(f"Generating {num_pairs} dialogue pairs for the dystopian RPG...")
    
    dialogue_pairs = []
    
    for _ in range(num_pairs):
        # Generate Player Input
        p_subject = random.choice(PLAYER_SUBJECTS)
        p_verb = random.choice(PLAYER_ACTIONS_VERBS)
        p_noun = random.choice(PLAYER_ACTIONS_NOUNS)
        p_mood = random.choice(PLAYER_MOODS)
        
        # Craft a varied input sentence
        player_input = f"I'm feeling {p_mood}, {p_verb} {p_subject} about {p_noun}."
        
        # Generate AI Response
        ai_response = random.choice(AI_RESPONSES_POOL)
        
        dialogue_pairs.append({
            "player_input": player_input,
            "ai_response": ai_response
        })
        
    print("Dialogue generation complete.")
    return dialogue_pairs

if __name__ == "__main__":
    # Configuration
    PAIRS_TO_GENERATE = 2500
    OUTPUT_FILENAME = "dystopian_dialogue_dataset.jsonl"
    
    # Generate the data
    data = generate_dystopian_dialogue(num_pairs=PAIRS_TO_GENERATE)
    
    # Write the dataset to a JSONL file
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            for pair in data:
                f.write(json.dumps(pair) + "\n")
        print(f"Successfully saved {len(data)} dialogue pairs to '{os.path.abspath(OUTPUT_FILENAME)}'")
    except IOError as e:
        print(f"Error: Could not write to file {OUTPUT_FILENAME}. Reason: {e}")