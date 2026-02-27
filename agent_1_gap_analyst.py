"""
Agent 1: Gap Analyst
====================
Compares your resume against multiple JDs and outputs:
- Skills you have
- Skills you lack
- ATS keywords to add
- Recommended learning priorities

Usage:
    python agent_1_gap_analyst.py --resume my_resume.txt --jds jd1.txt jd2.txt jd3.txt
    python agent_1_gap_analyst.py --resume my_resume.txt --jd_folder ./jds/
"""

from openai import OpenAI
import argparse
import os
import json
from pathlib import Path


def load_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_jds_from_folder(folder: str) -> dict:
    jd_files = Path(folder).glob("*.txt")
    return {f.stem: load_text(str(f)) for f in jd_files}


def run_gap_analysis(resume: str, jds: dict) -> dict:
    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    # Build combined JD block
    jd_block = "\n\n".join(
        [f"--- JD: {title} ---\n{content}" for title, content in jds.items()]
    )

    system_prompt = """You are a deeply technical QA recruiter with 15+ years of experience 
hiring in India's top product companies and GCCs (Global Capability Centres) in Gurugram, 
Bangalore, and remote. You have reviewed thousands of QA Manager, Test Lead, and SDET resumes.

You understand Indian tech hiring deeply — including what Naukri ATS, LinkedIn, and 
enterprise HR tools scan for. You know the Gurugram corridor companies: Publicis Sapient, 
EXL, Genpact, MakeMyTrip, Info Edge, PolicyBazaar, etc.

Always be brutally honest and specific. No vague advice. Give concrete, actionable gaps."""

    user_prompt = f"""Act as a senior QA recruiter. Analyze my resume against these {len(jds)} job descriptions.

MY RESUME:
{resume}

JOB DESCRIPTIONS:
{jd_block}

Output a JSON object with this EXACT structure:
{{
  "skills_i_have": [
    {{"skill": "string", "evidence_in_resume": "string", "frequency_in_jds": "high/medium/low"}}
  ],
  "skills_i_lack": [
    {{"skill": "string", "why_it_matters": "string", "urgency": "critical/important/nice-to-have", "learning_effort": "1-3 days / 1-2 weeks / 1 month+"}}
  ],
  "ats_keywords_to_add": [
    {{"keyword": "string", "appears_in_n_jds": "number", "where_to_add_in_resume": "string"}}
  ],
  "title_mismatch": "string explaining if your current title may hurt or help",
  "top_3_priorities": ["string", "string", "string"],
  "india_market_insight": "string with Gurugram/remote market specific advice"
}}

Return ONLY valid JSON. No markdown, no explanation outside JSON."""

    print("🔍 Running gap analysis... (this may take 20-30 seconds)")

    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Parse and return
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON if wrapped in markdown
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError("Could not parse JSON from Claude response")

    return result


def print_gap_report(data: dict):
    print("\n" + "=" * 60)
    print("📊 CAREER GAP ANALYSIS REPORT")
    print("=" * 60)

    print("\n✅ SKILLS YOU HAVE:")
    for s in data.get("skills_i_have", []):
        freq_icon = {"high": "🔥", "medium": "👍", "low": "💡"}.get(s.get("frequency_in_jds", ""), "•")
        print(f"  {freq_icon} {s['skill']} — {s.get('frequency_in_jds','').upper()} demand")
        print(f"      Evidence: {s.get('evidence_in_resume','')}")

    print("\n❌ SKILLS YOU LACK:")
    for s in data.get("skills_i_lack", []):
        urgency_icon = {"critical": "🚨", "important": "⚠️", "nice-to-have": "📌"}.get(s.get("urgency", ""), "•")
        print(f"  {urgency_icon} {s['skill']} [{s.get('urgency','').upper()}] — Learn in: {s.get('learning_effort','')}")
        print(f"      Why: {s.get('why_it_matters','')}")

    print("\n🔑 ATS KEYWORDS TO ADD TO YOUR RESUME:")
    for k in sorted(data.get("ats_keywords_to_add", []), key=lambda x: -int(str(x.get("appears_in_n_jds", 0)))):
        print(f"  • \"{k['keyword']}\" (in {k.get('appears_in_n_jds','?')} JDs) → Add to: {k.get('where_to_add_in_resume','')}")

    print(f"\n⚡ TITLE MISMATCH NOTE:")
    print(f"  {data.get('title_mismatch','')}")

    print("\n🎯 YOUR TOP 3 PRIORITIES RIGHT NOW:")
    for i, p in enumerate(data.get("top_3_priorities", []), 1):
        print(f"  {i}. {p}")

    print("\n🇮🇳 INDIA MARKET INSIGHT:")
    print(f"  {data.get('india_market_insight','')}")

    print("\n" + "=" * 60)


def generate_learning_syllabus(skill: str, client: OpenAI) -> str:
    """Bonus: generate a crash course for a specific gap skill"""
    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""Create a 3-day crash course syllabus for "{skill}" specifically for a
QA Manager transitioning to a senior/director role in India's tech industry.

Format:
Day 1: [Topic]
- What to learn (be specific with links/resources)
- Hands-on task
- Time estimate

Day 2: [Topic]
...

Day 3: [Topic]
...

Top 5 interview questions you'll be asked about {skill}:
1. ...
2. ...
...

Keep it practical and India-market relevant."""
        }]
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Gap Analyst Agent")
    parser.add_argument("--resume", required=True, help="Path to your resume .txt file")
    parser.add_argument("--jds", nargs="+", help="Paths to JD text files")
    parser.add_argument("--jd_folder", help="Folder containing JD .txt files")
    parser.add_argument("--learn", help="Generate 3-day syllabus for a specific skill")
    parser.add_argument("--output", help="Save JSON report to this file")
    args = parser.parse_args()

    resume = load_text(args.resume)

    # Load JDs
    jds = {}
    if args.jd_folder:
        jds.update(load_jds_from_folder(args.jd_folder))
    if args.jds:
        for jd_path in args.jds:
            stem = Path(jd_path).stem
            jds[stem] = load_text(jd_path)

    if not jds:
        print("❌ Error: Provide at least one JD via --jds or --jd_folder")
        return

    print(f"📄 Loaded resume + {len(jds)} JDs: {list(jds.keys())}")

    # Run gap analysis
    result = run_gap_analysis(resume, jds)
    print_gap_report(result)

    # Save JSON
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full JSON report saved to: {args.output}")

    # Optional: generate syllabus
    if args.learn:
        client = OpenAI(
            api_key=os.environ.get("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        print(f"\n📚 Generating 3-day crash course for: {args.learn}")
        syllabus = generate_learning_syllabus(args.learn, client)
        print(syllabus)


if __name__ == "__main__":
    main()
