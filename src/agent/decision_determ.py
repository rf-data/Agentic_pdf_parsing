## decision_determ.py
# imports
from typing import List
from collections import Counter

from src.schema.aggregation_schema import AggregatedResult
from src.schema.decision_schema import DecisionResult


class DecisionEngine:

    def decide(self, 
               agg: AggregatedResult, 
               n_docs: int) -> DecisionResult:

        # -------------------------
        # 1. Evidence Strength
        # -------------------------
        n_common = len(agg.common_findings)
        n_conflicts = len(agg.conflicting_findings)

        if n_docs >= 5 and n_common >= 3:
            evidence_strength = "strong"
        elif n_common >= 1:
            evidence_strength = "moderate"
        else:
            evidence_strength = "weak"

        # -------------------------
        # 2. Confidence Level
        # -------------------------
        if agg.overall_quality == "high" and evidence_strength == "strong":
            confidence = "high"
        elif agg.overall_quality in ["high", "medium"]:
            confidence = "medium"
        else:
            confidence = "low"

        # -------------------------
        # 3. Conclusions
        # -------------------------
        conclusions = []

        if agg.dominant_mechanisms:
            conclusions.append(
                f"Dominant mechanisms across documents include: {', '.join(agg.dominant_mechanisms[:3])}."
            )

        if agg.common_entities:
            conclusions.append(
                f"Core entity across documents: {', '.join(agg.common_entities)}."
            )

        # -------------------------
        # 4. Risks
        # -------------------------
        risks = []

        if n_conflicts > n_common:
            risks.append(
                "High inconsistency across findings; results may depend on interpretation or study design."
            )

        if n_docs < 3:
            risks.append(
                "Very small document base; conclusions are not robust."
            )

        if agg.overall_quality != "high":
            risks.append(
                "Overall document quality is not consistently high."
            )

        # -------------------------
        # 5. Recommendations
        # -------------------------
        recommendations = []

        if n_docs < 5:
            recommendations.append(
                "Increase number of documents to improve statistical and conceptual robustness."
            )

        if n_conflicts > 0:
            recommendations.append(
                "Cluster documents into subgroups (e.g., methodology, population) to resolve conflicting findings."
            )

        if not agg.common_findings:
            recommendations.append(
                "No clear consensus detected; further targeted literature review recommended."
            )

        if agg.dominant_mechanisms:
            recommendations.append(
                "Focus further analysis on dominant mechanisms identified."
            )

        # -------------------------
        # 6. Reasoning
        # -------------------------
        reasoning = (
            f"Decision based on {n_docs} documents. "
            f"Consensus findings: {n_common}, conflicting findings: {n_conflicts}. "
            f"Overall quality assessed as {agg.overall_quality}."
        )

        return DecisionResult(
            confidence_level=confidence,
            evidence_strength=evidence_strength,
            key_conclusions=conclusions,
            risks=risks,
            recommendations=recommendations,
            reasoning=reasoning
        )