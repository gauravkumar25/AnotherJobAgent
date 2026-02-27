"""
Agent 4: Interview Prep (Mock Interviewer + Code Reviewer)
===========================================================
Two modes:
1. MOCK INTERVIEW — Simulates a tough technical/behavioral interview panel
2. CODE REVIEW — "Roasts" your old automation code and suggests staff-engineer-level refactors

Usage:
    # Mock interview
    python agent_4_interview.py --mode interview --role "QA Director" --company "Publicis Sapient"
    
    # System design interview
    python agent_4_interview.py --mode interview --role "Principal SDET" --topic "test strategy for payment gateway"
    
    # Code review
    python agent_4_interview.py --mode code_review --code my_old_test.py
    
    # Behavioral interview (STAR format)
    python agent_4_interview.py --mode behavioral --role "QA Manager"
"""

from openai import OpenAI
import argparse
import os
from pathlib import Path


def load_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


INTERVIEWER_PERSONAS = {
    "principal_engineer": {
        "title": "Principal Engineer",
        "style": "Asks deep architectural questions. Interrupts if you miss edge cases. Wants to see trade-off thinking.",
        "focus": "scalability, design patterns, system design, observability"
    },
    "engineering_manager": {
        "title": "Engineering Manager",
        "style": "Focused on people, process, and delivery. Wants STAR-format answers. Probes conflict resolution.",
        "focus": "team management, stakeholder communication, metrics, hiring"
    },
    "vp_engineering": {
        "title": "VP of Engineering",
        "style": "Strategic thinker. Asks about ROI, business impact, organizational design. Doesn't care about syntax.",
        "focus": "QA strategy, cost reduction, quality culture, executive communication"
    },
    "senior_sdet": {
        "title": "Senior SDET (Peer Interviewer)",
        "style": "Wants code. Will ask you to whiteboard. Will challenge your technical choices.",
        "focus": "coding patterns, framework design, CI/CD, test architecture"
    }
}


def run_mock_interview(
    client: OpenAI,
    role: str,
    company: str,
    topic: str = None,
    persona_key: str = "principal_engineer"
):
    persona = INTERVIEWER_PERSONAS.get(persona_key, INTERVIEWER_PERSONAS["principal_engineer"])

    system_prompt = f"""You are a {persona['title']} at {company}, interviewing a candidate for a {role} position.

YOUR INTERVIEW STYLE: {persona['style']}
YOUR FOCUS AREAS: {persona['focus']}

INTERVIEW RULES:
1. Ask ONE question at a time
2. After the candidate answers, give honest feedback (what was good, what was missing)
3. Then ask the FOLLOW-UP or NEXT question
4. If they miss critical edge cases, interrupt with "What about [edge case]?"
5. After 6-8 questions, give a final assessment: Hire / No Hire / Borderline — with specific reasons
6. Be tough but fair. This is a Gurugram-based GCC or product company. They have high standards.
7. Occasionally add India-context scenarios (e.g., "Our team has 3 engineers in Gurugram, 2 in US")

TOPIC FOR TODAY: {topic or f"General {role} interview covering technical depth and leadership"}

Start the interview now. Introduce yourself briefly, then ask Question 1."""

    conversation_history = [{"role": "system", "content": system_prompt}]

    print(f"\n🎙️  MOCK INTERVIEW SESSION")
    print(f"   Role: {role} | Company: {company}")
    print(f"   Interviewer: {persona['title']}")
    print("="*60)
    print("   Type 'quit' to end | Type 'skip' to skip a question")
    print("   Type 'hint' to get a hint on the current question")
    print("="*60 + "\n")

    # Initial message
    initial_response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=500,
        messages=conversation_history + [{"role": "user", "content": "Start the interview."}]
    )

    interviewer_msg = initial_response.choices[0].message.content
    print(f"🧑‍💼 Interviewer: {interviewer_msg}\n")
    conversation_history.append({"role": "user", "content": "Start the interview."})
    conversation_history.append({"role": "assistant", "content": interviewer_msg})

    while True:
        candidate_input = input("You: ").strip()

        if candidate_input.lower() == "quit":
            print("\n📝 Requesting final assessment...")
            conversation_history.append({"role": "user", "content": candidate_input})
            conversation_history.append({"role": "user", "content": "Give me your final assessment. Hire/No Hire and why. Be specific."})

            final = client.chat.completions.create(
                model="grok-beta",
                max_tokens=800,
                messages=conversation_history
            )
            print(f"\n🧑‍💼 Final Assessment:\n{final.choices[0].message.content}")
            break

        if candidate_input.lower() == "hint":
            hint_messages = conversation_history + [
                {"role": "user", "content": "Give me a hint — what key points should a strong candidate cover in their answer to your last question? Don't give the full answer, just the framework."}
            ]
            hint = client.chat.completions.create(
                model="grok-beta",
                max_tokens=400,
                messages=hint_messages
            )
            print(f"\n💡 Hint: {hint.choices[0].message.content}\n")
            continue

        if candidate_input.lower() == "skip":
            candidate_input = "I'll skip this question and move to the next."

        conversation_history.append({"role": "user", "content": candidate_input})

        response = client.chat.completions.create(
            model="grok-beta",
            max_tokens=600,
            messages=conversation_history
        )

        interviewer_response = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": interviewer_response})

        print(f"\n🧑‍💼 Interviewer: {interviewer_response}\n")


def run_code_review(client: OpenAI, code: str, language: str = "python"):
    """Roasts your code and suggests staff-engineer-level refactors"""

    print("\n🔍 CODE REVIEW SESSION")
    print("="*60)
    print("Analyzing your code as a Staff/Principal Engineer would...\n")

    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": """You are a Staff Engineer / Principal SDET with 15+ years of experience.
You've seen thousands of automation codebases. You are direct, sometimes blunt, but always constructive.
You don't sugarcoat — if code is bad, you say so. But you always explain WHY and show HOW to fix it.
You reference specific design patterns, SOLID principles, and industry best practices."""},
            {"role": "user", "content": f"""Roast this automation code. Be direct. Tell me:

1. WHAT'S WRONG (be specific — line by line if needed)
   - Maintainability issues
   - Scalability problems  
   - Design pattern violations
   - Missing abstractions
   - Test quality issues (flakiness, assertions, test isolation)

2. HOW A STAFF ENGINEER WOULD REFACTOR IT
   - Show the refactored version with comments explaining each change
   - Name the design patterns used (Page Object Model, Builder Pattern, etc.)

3. INTERVIEW IMPACT
   - If you showed this code in an interview, what would a panel think?
   - What 3 questions would they ask you about it?

4. THE 3 MOST CRITICAL CHANGES (for quick wins before an interview)

CODE TO REVIEW ({language}):
```{language}
{code}
```"""}
        ]
    )

    print(response.choices[0].message.content)


def run_behavioral_prep(client: OpenAI, role: str):
    """Generate STAR-format behavioral questions with coaching"""

    print("\n🎯 BEHAVIORAL INTERVIEW PREP")
    print("="*60)

    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=3000,
        messages=[
            {"role": "system", "content": """You are an interview coach specializing in senior tech roles in India's product companies.
You know the behavioral questions that GCC companies (Google, Microsoft, Publicis Sapient),
product startups (Zomato, Meesho, PolicyBazaar), and service companies (Infosys, Wipro leadership) ask.
You teach the STAR method but also know when to use different frameworks (SOAR, CAR)."""},
            {"role": "user", "content": f"""Generate the top 10 behavioral interview questions for a {role} role, 
specifically in India's tech industry context.

For each question:
1. THE QUESTION (exact wording interviewers use)
2. WHY THEY ASK IT (what they're really evaluating)
3. STRONG ANSWER FRAMEWORK (STAR structure with what to include)
4. INDIA-SPECIFIC ANGLE (e.g., managing offshore teams, working with US stakeholders, vendor management)
5. RED FLAGS (what answers immediately get you rejected)

Focus on these themes:
- Team conflict and resolution
- Dealing with unrealistic deadlines
- Managing underperformers
- Stakeholder pushback on quality
- Building a QA team from scratch or improving an existing one
- Cross-cultural/remote team management"""}
        ]
    )

    print(response.choices[0].message.content)


def run_system_design(client: OpenAI, role: str, system_to_design: str):
    """Generate a system design interview challenge with expected answers"""

    print(f"\n🏗️  SYSTEM DESIGN INTERVIEW: {system_to_design}")
    print("="*60)

    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=3000,
        messages=[
            {"role": "system", "content": """You are a Principal Engineer conducting a system design interview.
You specialize in test infrastructure and QA system design at scale.
Your questions expose whether candidates think at junior level (just "write tests")
or at architect level (observability, flakiness mitigation, scalability, cost)."""},
            {"role": "user", "content": f"""Design a test strategy and test infrastructure for: {system_to_design}

This is for a {role} candidate. Structure your response as:

PART 1 — THE CHALLENGE BRIEF (what you'd tell the candidate)
PART 2 — WHAT A STRONG CANDIDATE COVERS
  - Functional testing approach
  - Non-functional testing (performance, security, chaos)
  - CI/CD integration
  - Observability and reporting
  - Edge cases they must mention
  - India/remote team considerations

PART 3 — SAMPLE STRONG ANSWER (model answer they should aim for)
PART 4 — COMMON MISTAKES (what junior-level candidates say that fails them)
PART 5 — FOLLOW-UP QUESTIONS TO PROBE DEEPER"""}
        ]
    )

    print(response.choices[0].message.content)


def main():
    parser = argparse.ArgumentParser(description="Interview Prep Agent")
    parser.add_argument("--mode", required=True,
                       choices=["interview", "code_review", "behavioral", "system_design"],
                       help="Interview mode")
    parser.add_argument("--role", default="QA Director", help="Target role")
    parser.add_argument("--company", default="a top product company", help="Target company")
    parser.add_argument("--topic", help="Specific interview topic")
    parser.add_argument("--persona", default="principal_engineer",
                       choices=list(INTERVIEWER_PERSONAS.keys()),
                       help="Interviewer persona")
    parser.add_argument("--code", help="Path to code file for review")
    parser.add_argument("--system", help="System to design (for system_design mode)")
    args = parser.parse_args()

    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    if args.mode == "interview":
        run_mock_interview(client, args.role, args.company, args.topic, args.persona)

    elif args.mode == "code_review":
        if not args.code:
            print("❌ --code is required for code_review mode")
            return
        code = load_text(args.code)
        lang = Path(args.code).suffix.lstrip(".") or "python"
        run_code_review(client, code, lang)

    elif args.mode == "behavioral":
        run_behavioral_prep(client, args.role)

    elif args.mode == "system_design":
        system = args.system or args.topic or "an e-commerce checkout system"
        run_system_design(client, args.role, system)


if __name__ == "__main__":
    main()
