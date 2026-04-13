## report_llm.py
# import


class ReportBuilder:
    def __init__(self,  aggregate, decision):
        self.agg = aggregate
        self.dec = decision

    def build_md_report(self):

        report = f"""
# Multi-Document Analysis Report

## Topic
{self.agg.document_set_topic}

## Key Findings (Consensus)
{self._format_list(self.agg.consensus_points)}

## Conflicting Points
{self._format_list(self.agg.conflicting_points)}

## Dominant Mechanisms
{self._format_list(self.agg.dominant_mechanisms)}

## Evidence Gaps
{self._format_list(self.agg.evidence_gaps)}

---

## Conclusions
{self._format_list(self.dec.key_conclusions)}

## Risks
{self._format_list(self.dec.main_risks)}

## Recommendations
{self._format_list(self.dec.recommendations)}

## Research Priorities
{self._format_list(self.dec.research_priority)}

---

## Interpretation
{self.agg.overall_interpretation}

## Confidence
Aggregation: {self.agg.confidence}
Decision: {self.dec.confidence}
"""
        return report

    def _format_list(self, items):
        return "\n".join([f"- {i}" for i in items]) if items else "- None"