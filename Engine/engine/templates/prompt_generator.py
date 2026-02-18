# prompt_generator.py
import json
import random
import os

# The template you provided
TEMPLATE_JSON = """
{
  "name": "Geo/Character/Story Scaffold",
  "transforms": {
    "GeoMemory": {
      "WorldState": [
        "The current geopolitical landscape and its defining traits",
        "Borders, blocs, and institutions that shape the map",
        "How power flows: governance, trade, conflict, and culture",
        "Where and when these dynamics unfold (regions, timelines, cycles)",
        "Why the world behaves this way: incentives, history, ideology",
        "Interdependencies among states, economies, resources, and publics",
        "Impact on lived reality: stability, prosperity, precarity, opportunity"
      ],
      "Factions": [
        "The key actors (states, coalitions, corporations, movements)",
        "Organization/command structures and capability stacks",
        "What each faction does to project influence or survive",
        "Theatres of operation and flashpoints; recent and looming events",
        "Motivations: security, prestige, profit, ideology, survival",
        "Alliances, rivalries, dependencies, and proxy links",
        "Payoffs and risks distributed to members, rivals, and civilians"
      ],
      "ForcesAtPlay": [
        "Macro forces moving the board (tech, climate, demography, finance)",
        "Vectors and gradients (rates, corridors, chokepoints, supply chains)",
        "Mechanisms translating force into outcomes (policy, markets, war)",
        "Spatial/temporal scope and cadence (now/near/long-term)",
        "Underlying drivers and constraints (resources, norms, path-dependence)",
        "Couplings across domains (cyber \u2194 energy, trade \u2194 security, info \u2194 trust)",
        "Systemic effects (resilience, fragility, tail-risk, upside optionality)"
      ]
    },
    "Characters": {
      "MainCharacter": [
        "Protagonist identity and core trait set",
        "Role, archetype, capabilities, and limitations",
        "What they do in the world; signature actions and skills",
        "Place in setting and timeline; current circumstances",
        "Personal goals, needs, wounds, and convictions",
        "Ties to others and to the world (allies, debts, obligations)",
        "Arc stakes: growth, cost, possible triumphs and failures"
      ],
      "CoStars": [
        "Key supporting characters and foils",
        "Their roles, domains of competence, quirks",
        "How they enable/impede the protagonist",
        "Where/when they intersect the plot and setting",
        "Their aims, loyalties, and hidden agendas",
        "Relational geometry with MC, NPCs, and factions",
        "Net effect on tone, pace, and outcome possibilities"
      ],
      "NPCs": [
        "Ambient personalities populating the world",
        "Types, professions, micro-cultures, and patterns",
        "Services, obstacles, and color they provide",
        "Local contexts, routines, and cadences",
        "Small-scale motives and incentives",
        "Touchpoints with MC/costars/factions; rumor networks",
        "Texture added to realism; leverage for side-quests and clues"
      ]
    },
    "Story": {
      "Setup": [
        "The premise and initial condition",
        "Exposition structure; viewpoint; scene scaffolding",
        "What kicks the motion: inciting beat and early tactics",
        "Opening setting(s), period, and social climate",
        "Why the story must begin now; seed of desire/conflict",
        "Initial links: MC\u2194world, MC\u2194costars, MC\u2194factions",
        "Baseline stakes and tone; promises to the reader"
      ],
      "Confrontation": [
        "The central struggle crystallized",
        "Escalation pattern; midpoint reversals; subplots",
        "Trials, schemes, and counters; resource exchanges",
        "Evolving arenas, deadlines, and constraints",
        "Competing drives and hard choices; ethical pressure",
        "Alliances shift; information flows; cause\u2192effect chains",
        "Rising cost/benefit ledger; what could be won or lost"
      ],
      "Resolution": [
        "The decisive break and new equilibrium",
        "Climax mechanics and denouement cadence",
        "Final actions and consequences; debts settled",
        "Where things land in world-time; aftershocks",
        "Fulfilled/denied desires; transformed beliefs",
        "Stable/ruptured bonds; legacies and open threads",
        "Meaning and impact; what persists; what changes"
      ]
    }
  }
}
"""

def generate_prompts(template_data: dict, num_prompts: int) -> list[str]:
    """Generates a specified number of unique symbolic prompts from the template."""
    
    print(f"Generating {num_prompts} unique prompts...")
    
    # Flatten the template into a list of the 9 phrase lists
    phrase_groups = []
    for transform_group in template_data['transforms'].values():
        for category_phrases in transform_group.values():
            phrase_groups.append(category_phrases)

    if len(phrase_groups) != 9:
        raise ValueError("Template does not contain exactly 9 phrase categories.")

    unique_prompts = set()
    
    # Loop until we have the desired number of unique prompts
    while len(unique_prompts) < num_prompts:
        # Create one prompt by picking a random phrase from each of the 9 groups
        prompt_parts = [random.choice(group) for group in phrase_groups]
        
        # Add the prompt as a tuple to the set to ensure uniqueness
        unique_prompts.add(tuple(prompt_parts))
        
        # Optional: Print progress for large generation tasks
        if len(unique_prompts) % 500 == 0:
            print(f"  ...generated {len(unique_prompts)} prompts")

    # Convert the set of tuples back to a list of formatted strings
    formatted_prompts = ["; ".join(prompt) for prompt in unique_prompts]
    
    print("Prompt generation complete.")
    return formatted_prompts

if __name__ == "__main__":
    # --- Configuration ---
    PROMPTS_TO_GENERATE = 5000
    OUTPUT_FILENAME = "symbolic_prompts.txt"
    
    # Load the template from the JSON string
    template = json.loads(TEMPLATE_JSON)
    
    # Generate the data
    prompts = generate_prompts(template, PROMPTS_TO_GENERATE)
    
    # Write the prompts to a file, one prompt per line
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            for line in prompts:
                f.write(line + "\n")
        print(f"\nSuccessfully saved {len(prompts)} unique prompts to '{os.path.abspath(OUTPUT_FILENAME)}'")
    except IOError as e:
        print(f"Error: Could not write to file {OUTPUT_FILENAME}. Reason: {e}")