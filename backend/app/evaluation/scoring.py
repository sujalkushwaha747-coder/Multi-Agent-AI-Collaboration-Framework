import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable


WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+-]*")
CLAIM_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class ScoreResult:
    score: float
    methodology: str
    estimated: bool = False


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text or "")]


def token_overlap_score(candidate: str, reference: str) -> float:
    candidate_tokens = Counter(tokenize(candidate))
    reference_tokens = Counter(tokenize(reference))
    if not candidate_tokens or not reference_tokens:
        return 0.0
    overlap = sum((candidate_tokens & reference_tokens).values())
    precision = overlap / max(sum(candidate_tokens.values()), 1)
    recall = overlap / max(sum(reference_tokens.values()), 1)
    if precision + recall == 0:
        return 0.0
    return clamp(100 * (2 * precision * recall) / (precision + recall))


def requirement_coverage_score(prompt: str, response: str) -> float:
    prompt_terms = {
        token
        for token in tokenize(prompt)
        if len(token) > 3 and token not in {"with", "from", "this", "that", "your"}
    }
    response_terms = set(tokenize(response))
    if not prompt_terms:
        return 70.0 if response.strip() else 0.0
    coverage = len(prompt_terms & response_terms) / len(prompt_terms)
    length_bonus = min(len(tokenize(response)) / 250, 1.0) * 15
    return clamp(coverage * 85 + length_bonus)


def quality_score(response: str) -> ScoreResult:
    words = tokenize(response)
    if not words:
        return ScoreResult(0.0, "Empty response receives zero quality.", True)

    paragraphs = [p.strip() for p in response.splitlines() if p.strip()]
    headings = sum(1 for p in paragraphs if p.endswith(":") or p.startswith(("#", "-", "*")))
    sentence_count = max(1, len(CLAIM_RE.split(response.strip())))
    avg_sentence_len = len(words) / sentence_count

    length_score = clamp((len(words) / 220) * 100)
    structure_score = clamp(55 + min(headings, 6) * 7 + min(len(paragraphs), 8) * 3)
    readability_penalty = max(0.0, avg_sentence_len - 32) * 1.2
    clarity_score = clamp(92 - readability_penalty)
    usefulness_score = clamp(45 + min(len(set(words)) / 120, 1.0) * 55)
    score = (
        length_score * 0.20
        + structure_score * 0.25
        + clarity_score * 0.25
        + usefulness_score * 0.30
    )
    return ScoreResult(
        round(clamp(score), 2),
        "Heuristic score using length adequacy, structure, sentence clarity, and lexical usefulness.",
        True,
    )


def accuracy_score(response: str, reference_answer: str | None, evidence: Iterable[str]) -> ScoreResult:
    evidence_text = "\n".join([item for item in evidence if item])
    if reference_answer:
        return ScoreResult(
            round(token_overlap_score(response, reference_answer), 2),
            "Token-level F1 overlap against the supplied reference answer.",
            False,
        )
    if evidence_text:
        response_score = token_overlap_score(response, evidence_text)
        return ScoreResult(
            round(response_score, 2),
            "Evidence-grounded lexical overlap against retrieved knowledge-base context.",
            False,
        )
    fallback = (quality_score(response).score * 0.45) + (
        requirement_coverage_score("", response) * 0.55
    )
    return ScoreResult(
        round(clamp(fallback), 2),
        "Estimated from response completeness and quality because no reference answer or retrieved evidence was available.",
        True,
    )


def hallucination_rate(response: str, evidence: Iterable[str]) -> ScoreResult:
    sentences = [s.strip() for s in CLAIM_RE.split(response.strip()) if len(s.strip()) > 20]
    if not sentences:
        return ScoreResult(0.0, "No substantive factual claims detected.", True)

    evidence_text = "\n".join([item for item in evidence if item])
    if evidence_text:
        unsupported = 0
        for sentence in sentences:
            if token_overlap_score(sentence, evidence_text) < 18:
                unsupported += 1
        rate = 100 * unsupported / len(sentences)
        return ScoreResult(
            round(clamp(rate), 2),
            "Estimated unsupported-claim rate against retrieved evidence chunks.",
            True,
        )

    hedges = sum(
        response.lower().count(term)
        for term in ["probably", "might", "could be", "unknown", "not sure"]
    )
    citations_or_constraints = sum(
        response.lower().count(term)
        for term in ["according to", "based on", "limitation", "assumption", "not evaluated"]
    )
    risk = 35 + max(0, len(sentences) - 8) * 2 + hedges * 2 - citations_or_constraints * 3
    return ScoreResult(
        round(clamp(risk, 5, 85), 2),
        "Estimated hallucination risk because no external evidence was supplied.",
        True,
    )


def completeness_score(prompt: str, response: str) -> ScoreResult:
    return ScoreResult(
        round(requirement_coverage_score(prompt, response), 2),
        "Requirement coverage estimated from important prompt terms addressed in the response.",
        True,
    )


def metric_winner(
    single: float | None, multi: float | None, *, higher_is_better: bool
) -> str:
    if single is None or multi is None:
        return "Not evaluated"
    if math.isclose(single, multi, abs_tol=0.01):
        return "Tie"
    if higher_is_better:
        return "Multi-Agent" if multi > single else "Single-Agent"
    return "Multi-Agent" if multi < single else "Single-Agent"


def safe_improvement_percentage(
    single: float | None, multi: float | None, *, higher_is_better: bool
) -> float | None:
    if single is None or multi is None or math.isclose(single, 0.0):
        return None
    if higher_is_better:
        value = ((multi - single) / single) * 100
    else:
        value = ((single - multi) / single) * 100
    return round(value, 2)


def normalized_overall(
    *,
    accuracy: float | None,
    quality: float | None,
    completeness: float | None,
    hallucination: float | None,
    execution_time: float | None,
    max_execution_time: float | None,
    weights: dict[str, float],
) -> float | None:
    if None in (accuracy, quality, completeness, hallucination):
        return None
    speed = 0.5
    if execution_time is not None and max_execution_time and max_execution_time > 0:
        speed = 1 - min(execution_time / max_execution_time, 1)
    normalized = {
        "accuracy": accuracy / 100,
        "quality": quality / 100,
        "completeness": completeness / 100,
        "hallucination": 1 - (hallucination / 100),
        "execution_time": speed,
    }
    weight_total = sum(weights.values()) or 1
    score = sum(normalized[key] * weight for key, weight in weights.items())
    return round(clamp((score / weight_total) * 100), 2)

