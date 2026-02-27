"""
Master Orchestrator: Run All Agents in a Pipeline
==================================================
Orchestrates all 4 agents in the optimal sequence for your job search.

Usage:
    python run_all.py --resume my_resume.txt --jd target_jd.txt --profile linkedin.txt
"""

from openai import OpenAI
import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Import all agents
sys.path.insert(0, os.path.dirname(__file__))
from agent_1_gap_analyst import load_text, load_jds_from_folder, run_gap_analysis, print_gap_report
from agent_2_resume_tailor import extract_keywords_from_jd, tailor_resume, print_tailor_report
from agent_3_outreach import generate_outreach
from agent_4_interview import run_behavioral_prep, INTERVIEWER_PERSONAS


def orchestrate(resume_path: str, jd_path: str, profile_path: str = None):
    client = OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    resume = load_text(resume_path)
    jd = load_text(jd_path)

    print("\n" + "🚀 " * 20)
    print("   CAREER AGENT PIPELINE STARTING")
    print("🚀 " * 20)

    # ── STEP 1: Gap Analysis ──────────────────────────────
    print("\n\n📊 STEP 1/4: GAP ANALYSIS")
    print("-" * 40)
    jds = {"target_role": jd}
    gap_data = run_gap_analysis(resume, jds)
    print_gap_report(gap_data)

    # ── STEP 2: Resume Tailoring ──────────────────────────
    print("\n\n✍️  STEP 2/4: RESUME TAILORING")
    print("-" * 40)
    keywords = extract_keywords_from_jd(client, jd)
    tailor_data = tailor_resume(client, resume, jd, keywords)
    print_tailor_report(tailor_data, "tailored_resume.txt")

    # ── STEP 3: Outreach (if profile provided) ────────────
    if profile_path:
        print("\n\n🤝 STEP 3/4: LINKEDIN OUTREACH")
        print("-" * 40)
        profile = load_text(profile_path)
        skills_summary = ", ".join(
            [s["skill"] for s in gap_data.get("skills_i_have", [])[:5]]
        )
        outreach = generate_outreach(client, profile, skills_summary, "job_interest")
        print(outreach)
        with open("outreach_messages.txt", "w") as f:
            f.write(outreach)
        print("\n💾 Outreach saved to: outreach_messages.txt")
    else:
        print("\n⏭️  STEP 3/4: SKIPPED (no --profile provided)")

    # ── STEP 4: Interview Prep Summary ───────────────────
    print("\n\n🎙️  STEP 4/4: INTERVIEW PREP — TOP 5 BEHAVIORAL QUESTIONS")
    print("-" * 40)
    run_behavioral_prep(client, "QA Director / Principal SDET")

    # ── FINAL SUMMARY ─────────────────────────────────────
    print("\n\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE — YOUR ACTION PLAN")
    print("=" * 60)

    priorities = gap_data.get("top_3_priorities", [])
    for i, p in enumerate(priorities, 1):
        print(f"  Week {i}: {p}")

    score = tailor_data.get("ats_match_score", "?")
    print(f"\n  📊 Resume ATS Score: {score}%")
    print(f"  📄 Tailored resume: tailored_resume.txt")
    if profile_path:
        print(f"  🤝 Outreach messages: outreach_messages.txt")
    print("\n  Good luck! 🎯")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Career Agent Pipeline Orchestrator")
    parser.add_argument("--resume", required=True, help="Path to your resume .txt")
    parser.add_argument("--jd", required=True, help="Path to target JD .txt")
    parser.add_argument("--profile", help="(Optional) LinkedIn profile .txt for outreach")
    args = parser.parse_args()

    orchestrate(args.resume, args.jd, args.profile)


if __name__ == "__main__":
    main()
