"""
Agent 3: Outreach Drafter (LinkedIn Personalization)
======================================================
Generates highly personalized LinkedIn connection requests and follow-up messages.
Avoids the generic "I'd love to connect" that gets ignored.

Usage:
    # From a LinkedIn profile text file
    python agent_3_outreach.py --profile director_profile.txt --your_skills "Selenium, CI/CD, Azure DevOps"

    # Batch mode: process multiple profiles
    python agent_3_outreach.py --profiles_folder ./profiles/ --your_skills "Selenium, CI/CD"

    # With a specific angle (e.g., referral, job interest)
    python agent_3_outreach.py --profile profile.txt --your_skills "..." --angle "job_interest"
"""

from openai import OpenAI
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


def load_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


OUTREACH_ANGLES = {
    "connect": "just building a professional network, no immediate ask",
    "job_interest": "interested in opportunities at their company",
    "referral_ask": "hoping they can refer you to a specific role",
    "insight_ask": "asking for career advice or industry insights",
    "collaboration": "potential collaboration or knowledge sharing"
}


def generate_outreach(
    client: OpenAI,
    profile_text: str,
    your_skills: str,
    angle: str = "connect",
    your_name: str = "QA Professional"
) -> dict:

    angle_desc = OUTREACH_ANGLES.get(angle, angle)

    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": """You are an expert at professional networking in India's tech industry.
You understand the LinkedIn culture of Gurugram, NCR, and remote tech hiring.
You write messages that feel human, specific, and respectful of the recipient's time.
You never use phrases like: "I'd love to connect", "I came across your profile",
"Reaching out to expand my network", or any generic opener.
You always find ONE specific thing from their profile to reference."""},
            {"role": "user", "content": f"""Write LinkedIn outreach messages for this person. 

MY BACKGROUND/SKILLS: {your_skills}
OUTREACH ANGLE: {angle_desc}
MY NAME: {your_name}

THEIR LINKEDIN PROFILE:
{profile_text}

Generate 3 variants, each with a different hook strategy:
Variant A — Reference their recent post or achievement
Variant B — Reference a shared tool/tech or industry challenge  
Variant C — Lead with a genuine question or insight

For each variant output:
CONNECTION REQUEST (max 300 chars — LinkedIn limit):
[message here]

FOLLOW-UP MESSAGE (if they accept, send after 2 days, max 500 chars):
[message here]

HOOK STRATEGY USED: [explain what you noticed in their profile]

---

Also output one EMAIL SUBJECT LINE for cold email (if email is available):
[subject]

Keep all messages:
- Specific to THIS person (mention their name, company, or a real detail)
- Confident but not desperate
- India-culturally appropriate (formal enough but not stiff)
- Focused on value exchange, not just asking"""}
        ]
    )

    return response.choices[0].message.content


def batch_outreach(profiles_folder: str, your_skills: str, angle: str, your_name: str):
    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    profiles = list(Path(profiles_folder).glob("*.txt"))

    print(f"\n📋 Processing {len(profiles)} profiles from {profiles_folder}")
    
    results = []
    for profile_path in profiles:
        person_name = profile_path.stem.replace("_", " ").title()
        print(f"\n{'='*50}")
        print(f"👤 Generating outreach for: {person_name}")
        print("="*50)
        
        profile_text = load_text(str(profile_path))
        result = generate_outreach(client, profile_text, your_skills, angle, your_name)
        
        print(result)
        results.append({"person": person_name, "messages": result})
        
    return results


def single_outreach(profile_path: str, your_skills: str, angle: str, your_name: str):
    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    profile_text = load_text(profile_path)
    
    person_name = Path(profile_path).stem.replace("_", " ").title()
    print(f"\n👤 Generating personalized outreach for: {person_name}")
    print("="*60)

    result = generate_outreach(client, profile_text, your_skills, angle, your_name)
    
    print(result)

    # Save to file
    output_file = f"outreach_{Path(profile_path).stem}.txt"
    with open(output_file, "w") as f:
        f.write(f"OUTREACH MESSAGES FOR: {person_name}\n")
        f.write("="*60 + "\n\n")
        f.write(result)
    print(f"\n💾 Messages saved to: {output_file}")


def interactive_mode():
    """Run as an interactive CLI agent"""
    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    
    print("\n🤝 LinkedIn Outreach Drafter — Interactive Mode")
    print("="*50)
    
    your_name = input("Your name: ").strip() or "QA Professional"
    your_skills = input("Your key skills (comma-separated): ").strip()
    
    print("\nOutreach angle options:")
    for key, desc in OUTREACH_ANGLES.items():
        print(f"  {key}: {desc}")
    angle = input("\nChoose angle (default: connect): ").strip() or "connect"
    
    print("\nPaste the LinkedIn profile text (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    profile_text = "\n".join(lines).strip()

    if not profile_text:
        print("❌ No profile text provided.")
        return

    print("\n✍️  Generating personalized outreach...")
    result = generate_outreach(client, profile_text, your_skills, angle, your_name)
    print("\n" + "="*60)
    print(result)


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Outreach Drafter Agent")
    parser.add_argument("--profile", help="Path to a single LinkedIn profile .txt")
    parser.add_argument("--profiles_folder", help="Folder with multiple profile .txt files")
    parser.add_argument("--your_skills", default="QA Automation, Test Management, CI/CD, Selenium",
                        help="Your key skills")
    parser.add_argument("--angle", default="connect", 
                        choices=list(OUTREACH_ANGLES.keys()),
                        help="Outreach angle/goal")
    parser.add_argument("--your_name", default="QA Professional", help="Your name")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.profiles_folder:
        batch_outreach(args.profiles_folder, args.your_skills, args.angle, args.your_name)
    elif args.profile:
        single_outreach(args.profile, args.your_skills, args.angle, args.your_name)
    else:
        print("💡 No args provided — launching interactive mode...")
        interactive_mode()


if __name__ == "__main__":
    main()
