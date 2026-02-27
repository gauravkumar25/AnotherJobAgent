# AnotherJobAgent - Grok API Edition

This project has been updated to use xAI's Grok API instead of Anthropic's Claude API.

## 🎨 Web UI Available!

**NEW:** Beautiful web interface with secure API key management!

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

See [README_WEB_UI.md](README_WEB_UI.md) for full web UI documentation.

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

### 3. Set Up API Key

#### Option A: Local Development (Environment Variables)

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

#### Option B: GitHub Secrets (For CI/CD and GitHub Actions)

1. **Add Secret to Your Repository:**
   - Go to your GitHub repository
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `XAI_API_KEY`
   - Value: Your actual Grok API key
   - Click **Add secret**

2. **Use in GitHub Actions Workflow:**

Create `.github/workflows/run-agents.yml`:

```yaml
name: Run Job Agents

on:
  workflow_dispatch:
    inputs:
      resume_file:
        description: 'Path to resume file'
        required: true
      jd_file:
        description: 'Path to job description file'
        required: true

jobs:
  run-agents:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run agents
        env:
          XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
        run: |
          python run_all.py \
            --resume ${{ github.event.inputs.resume_file }} \
            --jd ${{ github.event.inputs.jd_file }}

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: agent-results
          path: |
            tailored_resume.txt
            outreach_messages.txt
```

3. **Access the Secret in Code:**

The agents already read from `os.environ.get("XAI_API_KEY")`, so GitHub Secrets will automatically work when set in the workflow's `env` section.

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

## Using with GitHub Actions

The agents can be run automatically using GitHub Actions. Here's an example workflow:

### Scheduled Resume Analysis

Create `.github/workflows/weekly-analysis.yml`:

```yaml
name: Weekly Resume Analysis

on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9 AM
  workflow_dispatch:  # Manual trigger

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run gap analysis
        env:
          XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
        run: |
          python agent_1_gap_analyst.py \
            --resume ./data/resume.txt \
            --jd_folder ./data/jds/ \
            --output gap_analysis.json

      - name: Upload analysis
        uses: actions/upload-artifact@v4
        with:
          name: gap-analysis-${{ github.run_number }}
          path: gap_analysis.json
```

### Security Best Practices

- ✅ **Never commit your API key** to the repository
- ✅ **Use GitHub Secrets** for CI/CD workflows
- ✅ **Use `.env` files** for local development (and add `.env` to `.gitignore`)
- ✅ **Rotate API keys** periodically
- ✅ **Monitor API usage** at the xAI Console to detect unauthorized use

## Notes

- Grok uses an OpenAI-compatible API, so we use the `openai` Python library
- The API endpoint is configured to `https://api.x.ai/v1`
- All functionality remains the same, just powered by Grok instead of Claude
- Make sure to monitor your API usage at the xAI Console
- **Never commit API keys** - use environment variables or GitHub Secrets

## Support

For xAI/Grok API issues, visit:
- [xAI Documentation](https://docs.x.ai/)
- [xAI Console](https://console.x.ai/)

For project-specific issues, refer to the original repository or create an issue.
