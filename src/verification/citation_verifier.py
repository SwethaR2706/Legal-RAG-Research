import json
import re


class CitationVerifier:

    def __init__(self, model_fn=None):
        self.model_fn = model_fn

    def build_cat3_prompt(self, question):
        return f"""
You are a legal citation verification system.

Analyze the following legal analysis and determine whether
the citation is correct.

If the citation is correct:
- state that there is no citation error.

If the citation is incorrect:
- identify the error type:
  - page
  - volume
  - reporter series
- provide the corrected citation.

Return JSON only:

{{
  "is_correct": true or false,
  "error_type": null or "page" or "volume" or "series",
  "corrected_citation": null or "string"
}}

LEGAL ANALYSIS:
{question}
"""

    def build_cat4_prompt(self, question):
        return f"""
You are a legal case citation verification system.

Determine whether the cited case in the following legal
scenario is the correct authority.

If it is correct, report that the citation is valid.

If it is incorrect, identify the correct case and citation.

Return JSON only:

{{
  "is_correct": true or false,
  "case_name": "string or null",
  "case_citation": "string or null"
}}

LEGAL SCENARIO:
{question}
"""

    def predict_cat3(self, question):
        if self.model_fn is None:
            raise RuntimeError(
                "No model backend configured for CitationVerifier."
            )

        prompt = self.build_cat3_prompt(question)
        response = self.model_fn(prompt)

        return self._parse_json(response)

    def predict_cat4(self, question):
        if self.model_fn is None:
            raise RuntimeError(
                "No model backend configured for CitationVerifier."
            )

        prompt = self.build_cat4_prompt(question)
        response = self.model_fn(prompt)

        return self._parse_json(response)

    @staticmethod
    def _parse_json(response):

        if isinstance(response, dict):
            return response

        text = response.strip()

        # Remove markdown code fences if the model adds them.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        try:
            return json.loads(text)
        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                text,
                flags=re.DOTALL
            )

            if match:
                return json.loads(match.group(0))

            raise ValueError(
                f"Could not parse model response as JSON:\n{text}"
            )