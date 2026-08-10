import json
import os

from groq import Groq


class GroqCitationVerifier:

    def __init__(
        self,
        model="llama-3.3-70b-versatile"
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable is not set."
            )

        self.client = Groq(api_key=api_key)
        self.model = model

    def _call(self, prompt):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal citation verification "
                        "system. Follow the requested output "
                        "format exactly."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        return json.loads(content)

    def verify_cat3(self, question):

        prompt = f"""
You are solving LegalCiteBench Category 3:
Citation Error Detection.

IMPORTANT:
This benchmark contains BOTH correct and deliberately
incorrect citations.

Do NOT assume that a citation contains an error.

Your first task is to determine whether the citation
presented in the legal analysis is actually incorrect.

If the citation is valid:
    is_correct = true
    error_type = null
    corrected_citation = null

If the citation is incorrect:
    is_correct = false
    identify the specific error as one of:
        page
        volume
        series

Then provide the corrected citation component.

CRITICAL:
Do not invent a citation error merely because the citation
looks unusual.

Do not change a citation simply because:
- formatting looks unusual
- the case name is abbreviated
- reporter formatting differs
- the citation contains multiple components
- the citation is unfamiliar

Only classify it as incorrect when there is sufficient
reason to determine that one of the citation components is
wrong.

For an incorrect citation, distinguish carefully between:

page:
The page number is wrong.

volume:
The volume number is wrong.

series:
The reporter series is wrong.

Return ONLY valid JSON:

{{
  "is_correct": true,
  "error_type": null,
  "corrected_citation": null
}}

OR:

{{
  "is_correct": false,
  "error_type": "page",
  "corrected_citation": "corrected component"
}}

OR:

{{
  "is_correct": false,
  "error_type": "volume",
  "corrected_citation": "corrected component"
}}

OR:

{{
  "is_correct": false,
  "error_type": "series",
  "corrected_citation": "corrected component"
}}

Do not explain your reasoning.
Do not reproduce the entire legal analysis.
Do not rewrite the complete citation.

LEGAL ANALYSIS:

{question}
"""

        return self._call(prompt)

    def verify_cat4_2(self, question):

        prompt = f"""
You are solving LegalCiteBench CAT4.2:
Case Verification.

Read the legal scenario below.

Determine whether the cited case is the correct
authority for the described proposition.

Return ONLY valid JSON with exactly these fields:

{{
  "is_correct": true,
  "case_name": null,
  "case_citation": null
}}

If the cited case is correct:
- is_correct = true
- provide its case name and citation.

If the cited case is incorrect:
- is_correct = false
- provide the correct case name and citation.

LEGAL SCENARIO:

{question}
"""

        return self._call(prompt)