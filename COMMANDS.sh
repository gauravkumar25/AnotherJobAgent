# HOW TO USE YOUR CAREER AGENTS
# ================================
# Replace the sample content below with your real data

# ── STEP 1: SETUP ──────────────────────────────────────
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-your-key-here"   # Get from console.anthropic.com

# ── STEP 2: PREPARE YOUR INPUT FILES ───────────────────
# my_resume.txt       → Paste your resume as plain text
# jd_target.txt       → Paste one JD from Naukri/LinkedIn
# linkedin_profile.txt → Paste a Director's LinkedIn profile text

# ── STEP 3: RUN INDIVIDUAL AGENTS ──────────────────────

# Agent 1: Gap Analysis (compare resume vs multiple JDs)
python agent_1_gap_analyst.py --resume my_resume.txt --jds jd1.txt jd2.txt jd3.txt

# Agent 1: Also generate a 3-day learning crash course for a skill gap
python agent_1_gap_analyst.py --resume my_resume.txt --jds jd1.txt --learn "OpenTelemetry"

# Agent 2: Tailor resume to a specific JD
python agent_2_resume_tailor.py --resume my_resume.txt --jd jd_target.txt --output tailored_resume.txt

# Agent 3: Generate LinkedIn outreach for a specific person
python agent_3_outreach.py --profile linkedin_profile.txt --your_skills "Selenium, CI/CD, Azure DevOps, Test Management"

# Agent 3: Interactive mode (paste profile manually)
python agent_3_outreach.py --interactive

# Agent 4: Mock interview (conversational — type your answers)
python agent_4_interview.py --mode interview --role "QA Director" --company "Publicis Sapient" --persona principal_engineer

# Agent 4: System design interview
python agent_4_interview.py --mode system_design --role "Principal SDET" --system "microservices payment gateway with 10M daily transactions"

# Agent 4: Behavioral prep questions
python agent_4_interview.py --mode behavioral --role "QA Director"

# Agent 4: Code review (roast your old automation code)
python agent_4_interview.py --mode code_review --code old_selenium_test.py

# ── STEP 4: RUN THE FULL PIPELINE ──────────────────────
python run_all.py --resume my_resume.txt --jd jd_target.txt --profile linkedin_profile.txt

# ── INTERVIEW PERSONAS AVAILABLE ───────────────────────
# principal_engineer   → Deep technical, edge cases, architecture
# engineering_manager  → People, process, STAR format
# vp_engineering       → Strategy, ROI, organizational design
# senior_sdet          → Code-heavy, framework design, CI/CD

# ── TIPS ───────────────────────────────────────────────
# • Run Agent 1 first — it tells you WHAT to fix
# • Run Agent 2 for EVERY JD you apply to (different tailoring per company)
# • Run Agent 3 before connecting with anyone senior on LinkedIn
# • Run Agent 4 in interview mode daily for 2 weeks before applying
