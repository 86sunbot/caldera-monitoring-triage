# Google AI Studio Deployment & Integration Guide
### Caldera Therapeutics · Clinical Monitoring Triage (Team 2)

This repository natively supports **Google AI Studio** for live LLM candidate observation extraction.

---

## 1. Running via Google AI Studio API

### Step 1: Obtain a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com).
2. Click **Get API Key** and create a free key.

### Step 2: Set the Environment Variable
```bash
export GEMINI_API_KEY="your-google-ai-studio-api-key"
```

### Step 3: Run the Pipeline with AI Studio
```bash
cd /Users/suryap/.gemini/antigravity/scratch/caldera-monitoring-triage
.venv/bin/python src/main.py --use-ai-studio --format markdown
```
The pipeline will call `gemini-2.5-flash` via Google AI Studio's structured JSON schema endpoint, returning verbatim citations into the reviewer packet. If no key is provided, it falls back seamlessly to the deterministic engine.

---

## 2. Running in the Google AI Studio Web Playground

If you wish to demonstrate the prompt directly inside the [Google AI Studio Web UI](https://aistudio.google.com/prompts/new_chat):

### Model Configuration
- **Model**: `Gemini 2.5 Flash` (or `Gemini 1.5 Flash`)
- **Temperature**: `0.1` (low temperature ensures strict verbatim sentence reproduction)
- **Response Format**: `JSON`

### System Instructions
Copy and paste this into the **System Instructions** box in Google AI Studio:

```text
You are a clinical monitoring triage assistant for Caldera Therapeutics.
Your duty is SURFACING candidate signals from monitoring reports, NOT PREDICTING or SCORING.

CRITICAL GOVERNANCE MANDATES:
1. NEVER output a risk score, priority, rating, or deviation confirmation.
2. Every candidate observation MUST cite the exact page number and verbatim sentence from the report text.
3. Classify each observation into one of these neutral themes:
   - 'Informed Consent'
   - 'Investigational Product & Accountability'
   - 'Temperature Monitoring'
   - 'Staff Training & Delegation'
   - 'Safety & Adverse Events'
4. If no candidate observations exist in the report, return an empty list.
```

### Structured Output Schema (JSON Schema)
In the Google AI Studio settings under **Structured Output / Response Schema**, paste:

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "page_number": {
        "type": "integer"
      },
      "verbatim_sentence": {
        "type": "string"
      },
      "theme": {
        "type": "string",
        "enum": [
          "Informed Consent",
          "Investigational Product & Accountability",
          "Temperature Monitoring",
          "Staff Training & Delegation",
          "Safety & Adverse Events"
        ]
      }
    },
    "required": [
      "page_number",
      "verbatim_sentence",
      "theme"
    ]
  }
}
```

### Test Input Prompt
Paste the following sample text into the User message:

```text
Study Report ID: MVR-2024-001
Site ID: SITE-101
Visit Date: 2024-01-15

Report Content:
--- PAGE 1 ---
Caldera Study CAL-301 Interim Monitoring Visit 1. Site 101 demonstrated good overall progress.

--- PAGE 2 ---
During regulatory binder review, informed consent form version 3 was signed prior to baseline screening for Subject 001. However, subject 003 signed an outdated consent document prior to initial dosing.

--- PAGE 3 ---
Pharmacy check: Investigational product storage was inspected. Drug accountability logs were complete and up to date.
```
