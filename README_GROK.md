# AnotherJobAgent - Grok API Edition

This project has been updated to use xAI's Grok API instead of Anthropic's Claude API.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Grok API Key

1. Visit [xAI Console](https://console.x.ai/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

```
XAI_API_KEY=your_actual_api_key_here
```

Or export it directly in your shell:

```bash
export XAI_API_KEY="your_actual_api_key_here"
```

### 4. Run the Agents

All commands remain the same as the original project:

#### Run All Agents in Pipeline
```bash
python run_all.py --resume my_resume.txt --jd target_jd.txt --profile linkedin.txt
```

#### Run Individual Agents

**Gap Analysis:**
```bash
python agent_1_gap_analyst.py --resume my_resume.txt --jds jd1.txt jd2.txt jd3.txt
```

**Resume Tailoring:**
```bash
python agent_2_resume_tailor.py --resume my_resume.txt --jd target_jd.txt
```

**LinkedIn Outreach:**
```bash
python agent_3_outreach.py --profile director_profile.txt --your_skills "Selenium, CI/CD, Azure DevOps"
```

**Interview Prep:**
```bash
# Behavioral interview prep
python agent_4_interview.py --mode behavioral --role "QA Director"

# Mock interview
python agent_4_interview.py --mode interview --role "QA Director" --company "Publicis Sapient"

# Code review
python agent_4_interview.py --mode code_review --code my_old_test.py

# System design
python agent_4_interview.py --mode system_design --role "Principal SDET" --system "payment gateway testing"
```

## Changes Made

### API Migration
- **From:** Anthropic Claude API (`anthropic` library)
- **To:** xAI Grok API (`openai` library with Grok endpoint)

### Model Changes
- **From:** `claude-opus-4-6`, `claude-sonnet-4-6`
- **To:** `grok-beta`

### Code Changes
- Updated all agent files to use OpenAI client with Grok endpoint
- Changed API call format from `client.messages.create()` to `client.chat.completions.create()`
- Updated response parsing from `message.content[0].text` to `response.choices[0].message.content`
- Added environment variable support for `XAI_API_KEY`

## Notes

- Grok uses an OpenAI-compatible API, so we use the `openai` Python library
- The API endpoint is configured to `https://api.x.ai/v1`
- All functionality remains the same, just powered by Grok instead of Claude
- Make sure to monitor your API usage at the xAI Console

## Support

For xAI/Grok API issues, visit:
- [xAI Documentation](https://docs.x.ai/)
- [xAI Console](https://console.x.ai/)

For project-specific issues, refer to the original repository or create an issue.
