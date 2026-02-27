"""
Agent 2: Resume Tailor (ATS Optimizer)
=======================================
Takes your base resume + a specific JD and rewrites bullet points
to maximize ATS match score. Outputs:
- Tailored resume with rewritten bullets
- Match score estimate
- Missing keywords inserted naturally

Usage:
    python agent_2_resume_tailor.py --resume my_resume.txt --jd target_jd.txt
    python agent_2_resume_tailor.py --resume my_resume.txt --jd target_jd.txt --output tailored_resume.txt
"""

from openai import OpenAI
import argparse
import json
import re
import os
from pathlib import Path


def load_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_keywords_from_jd(client: OpenAI, jd: str) -> dict:
    """First pass: extract all critical keywords from JD"""
    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Extract all ATS-critical keywords from this job description.
Return ONLY a JSON object:
{{
  "hard_skills": ["list of tools, technologies, frameworks"],
  "soft_skills": ["leadership, communication, etc"],
  "methodologies": ["Agile, Shift-Left, etc"],
  "certifications": ["ISTQB, PMP, etc"],
  "domain_keywords": ["fintech, e-commerce, etc"],
  "action_verbs": ["Led, Architected, Implemented, etc"],
  "title_variants": ["exact role titles mentioned"]
}}

JOB DESCRIPTION:
{jd}

Return ONLY valid JSON."""
        }]
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else {}


def tailor_resume(client: OpenAI, resume: str, jd: str, keywords: dict) -> dict:
    """Second pass: rewrite resume to match JD"""

    keyword_summary = json.dumps(keywords, indent=2)

    response = client.chat.completions.create(
        model="grok-beta",
        max_tokens=5000,
        messages=[
            {"role": "system", "content": """You are an expert resume writer for senior tech professionals in India.
You specialize in QA, Testing, and Engineering Management roles at product companies and GCCs.
You understand Naukri.com and LinkedIn India ATS systems deeply.
You NEVER fabricate experience. You reframe REAL experience using better language.
You write in a confident, executive tone appropriate for Director/Principal level roles."""},
            {"role": "user", "content": f"""Rewrite my resume to maximize ATS match for this specific JD. 

RULES:
1. Never fabricate experience — only rephrase and reframe real experience
2. Inject missing keywords NATURALLY into existing bullet points
3. Lead every bullet with a strong action verb from the JD where possible
4. Add metrics/impact where implied (e.g., "managed team" → "Led team of 8 SDETs")
5. Keep original structure (sections, order) intact
6. Flag any JD requirement that has NO match in my resume (mark as [GAP: xyz])

ATS KEYWORDS TO INJECT:
{keyword_summary}

MY ORIGINAL RESUME:
{resume}

TARGET JOB DESCRIPTION:
{jd}

Return a JSON object:
{{
  "tailored_resume": "Full rewritten resume text, preserving sections",
  "ats_match_score": "estimated score 0-100",
  "score_reasoning": "why this score",
  "bullets_rewritten": [
    {{"original": "string", "rewritten": "string", "keywords_added": ["list"]}}
  ],
  "gaps_flagged": ["list of JD requirements with no resume match"],
  "summary_rewrite": "Rewritten professional summary targeting this JD"
}}

Return ONLY valid JSON."""}
        ]
    )

    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else {"tailored_resume": raw}


def print_tailor_report(data: dict, output_path: str = None):
    score = data.get("ats_match_score", "?")
    score_num = int(str(score).replace("%", "")) if str(score).replace("%", "").isdigit() else 0
    score_bar = "█" * (score_num // 10) + "░" * (10 - score_num // 10)

    print("\n" + "=" * 60)
    print("🎯 RESUME TAILOR REPORT")
    print("=" * 60)

    print(f"\n📊 ATS MATCH SCORE: {score}%")
    print(f"   [{score_bar}]")
    print(f"   {data.get('score_reasoning', '')}")

    target = 80
    if score_num >= target:
        print(f"   ✅ Above {target}% target — ready to apply!")
    else:
        print(f"   ⚠️  Below {target}% target — review gaps below")

    print("\n✍️  KEY BULLET REWRITES:")
    for b in data.get("bullets_rewritten", [])[:5]:  # Show top 5
        print(f"\n  BEFORE: {b.get('original','')}")
        print(f"  AFTER:  {b.get('rewritten','')}")
        if b.get("keywords_added"):
            print(f"  ADDED:  {', '.join(b['keywords_added'])}")

    if data.get("gaps_flagged"):
        print("\n🚨 UNFILLABLE GAPS (be ready to address in interview):")
        for g in data["gaps_flagged"]:
            print(f"  • {g}")

    print("\n📝 REWRITTEN PROFESSIONAL SUMMARY:")
    print(f"  {data.get('summary_rewrite', '')}")

    # Save tailored resume
    tailored = data.get("tailored_resume", "")
    if tailored:
        save_path = output_path or "tailored_resume.txt"
        with open(save_path, "w") as f:
            f.write(tailored)
        print(f"\n💾 Tailored resume saved to: {save_path}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Resume Tailor Agent")
    parser.add_argument("--resume", required=True, help="Path to base resume .txt")
    parser.add_argument("--jd", required=True, help="Path to target JD .txt")
    parser.add_argument("--output", default="tailored_resume.txt", help="Output file for tailored resume")
    args = parser.parse_args()

    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    resume = load_text(args.resume)
    jd = load_text(args.jd)

    print(f"📄 Resume loaded: {args.resume}")
    print(f"📋 JD loaded: {args.jd}")

    # Step 1: Extract keywords
    print("\n🔑 Extracting ATS keywords from JD...")
    keywords = extract_keywords_from_jd(client, jd)
    print(f"   Found: {sum(len(v) for v in keywords.values() if isinstance(v, list))} keywords across {len(keywords)} categories")

    # Step 2: Tailor resume
    print("\n✍️  Tailoring your resume... (30-45 seconds)")
    result = tailor_resume(client, resume, jd, keywords)

    # Step 3: Print report
    print_tailor_report(result, args.output)


if __name__ == "__main__":
    main()
