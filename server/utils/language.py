"""Language directives for LLM-generated output.

A single helper used across every generation flow (clinical note, one-line
summary, referral letter, clinical reasoning, and chat) so the clinician's
chosen output language is applied consistently.

The chosen language is independent of the language spoken during the encounter,
which may be Arabic, English, or a code-switched mix. 'auto' leaves the model to
match the input (preserving natural code-switching); the other modes force a
specific output language regardless of the input.
"""

VALID_OUTPUT_LANGUAGES = ("auto", "english", "arabic", "bilingual")

DEFAULT_OUTPUT_LANGUAGE = "auto"

_DIRECTIVES = {
    "auto": "",
    "english": (
        "\n\nOUTPUT LANGUAGE: Write your entire response in English. If the "
        "source material is in another language (for example Arabic), translate "
        "it into clear clinical English. Keep medication names, dosages, and "
        "numerical values accurate, and preserve the requested structure, "
        "headings, and formatting exactly."
    ),
    "arabic": (
        "\n\nOUTPUT LANGUAGE: Write your entire response in Modern Standard "
        "Arabic (العربية الفصحى), regardless of the language of the source "
        "material. Use standard Arabic medical terminology. Medication names and "
        "dosages may remain in Latin script for accuracy. Preserve the requested "
        "structure, headings, and formatting exactly."
    ),
    "bilingual": (
        "\n\nOUTPUT LANGUAGE: Provide your entire response in BOTH English and "
        "Modern Standard Arabic (العربية الفصحى). Give the English version "
        "first, then the Arabic translation below it, clearly separated. Keep "
        "both versions consistent in clinical content, and preserve the "
        "requested structure, headings, and formatting in each."
    ),
}


def normalize_output_language(output_language) -> str:
    """Return a valid output-language key, falling back to the default."""
    if not output_language or not isinstance(output_language, str):
        return DEFAULT_OUTPUT_LANGUAGE
    value = output_language.strip().lower()
    return value if value in VALID_OUTPUT_LANGUAGES else DEFAULT_OUTPUT_LANGUAGE


def language_directive(output_language) -> str:
    """Return a system-prompt directive for the chosen output language.

    Returns an empty string for 'auto' (or unknown values), leaving the model to
    match the language of the input.
    """
    return _DIRECTIVES.get(normalize_output_language(output_language), "")
