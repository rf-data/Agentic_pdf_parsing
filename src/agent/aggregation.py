## aggregation.py
# imports
from collections import Counter
from typing import List

from src.schema.extraction_schema import ExtractedDocument
from src.schema.aggregation_schema import AggregatedResult
from src.core.session import session




# ------------------
# MAIN FUNCTION
# ------------------

class AggregationEngine:

    def aggregate(self, docs: List[ExtractedDocument]) -> AggregatedResult:
        logger = session.logger

        logger.info("Start aggregating LLM responses.")
        # -------------------------
        # Aggregating 'Entities'
        # -------------------------
        entity_sets = [set(d.key_entities) for d in docs]

        common_entities = list(set.intersection(*entity_sets)) if len(entity_sets) > 1 else list(entity_sets[0])

        all_entities = [e for d in docs for e in d.key_entities]
        unique_entities = list(set(all_entities))

        # -------------------------
        # Aggregating 'Mechanisms'
        # -------------------------
        mech_counter = Counter()

        for d in docs:
            mech_counter.update(d.mechanisms)

        dominant_mechanisms = [m for m, _ in mech_counter.most_common(5)]
        common_mechanisms = [
            m for m in mech_counter
            if mech_counter[m] == len(docs)
        ]

        # -------------------------
        # Aggregating 'Findings'
        # -------------------------
        all_findings = [f for d in docs for f in d.key_findings]

        finding_counter = Counter(all_findings)

        common_findings = [
            f for f, c in finding_counter.items()
            if c >= 2
            # threshold = max(2, len(docs) // 2) ??
            ]

        conflicting_findings = [
            f for f, c in finding_counter.items()
            if c == 1
            ]

        # -------------------------
        # Aggregating 'Quality'
        # -------------------------
        qualities = [d.quality_assessment for d in docs if d.quality_assessment]

        if qualities:
            overall_quality = Counter(qualities).most_common(1)[0][0]
        else:
            overall_quality = "unknown"

        # -------------------------
        # Summary (simple)
        # -------------------------
        summary = self._build_summary(
            common_entities,
            dominant_mechanisms,
            common_findings
            )

        return AggregatedResult(
            common_entities=common_entities,
            unique_entities=unique_entities,
            common_mechanisms=common_mechanisms,
            dominant_mechanisms=dominant_mechanisms,
            common_findings=common_findings,
            conflicting_findings=conflicting_findings,
            overall_quality=overall_quality,
            summary=summary
            )

    def _build_summary(self, entities, mechanisms, findings):

        ent_part = ", ".join(entities) if entities else "no specific topic. They have their distinct topics"
        mech_part = ", ".join(mechanisms[:3]) if mechanisms else "no dominant mechanisms"
        find_part = findings[0] if findings else "no clear consensus"

        return f"The documents at hand commonly cover {ent_part}. Across these documents, dominant mechanisms include {mech_part}. Key consensus: {find_part}."