## orchestrator.py
# import
from pathlib import Path
from typing import List

import src.tools.text_extraction as extract
import src.utils.path_helper as ph
import src.utils.llm_helper as llm


class AnalysisOrchestrator:

    def __init__(self, 
                 extraction, 
                 agg_det, 
                 agg_llm, 
                 decision, 
                 reporter,
                 config):
        
        self.extraction = extraction
        self.agg_det = agg_det
        self.agg_llm = agg_llm
        self.decision = decision
        self.reporter = reporter
        self.config = config

    def run(self, pdfs: List[Path | str]):

        # if isinstance(pdfs, (Path, str)):
        #     pdfs = ph.list_files(pdfs, "pdf")

        extract_engine = self.extraction(self.config)

        docs = []
        for pdf in pdfs:
            text = extract.extract_text_per_page(pdf)
            doc, _ = extract_engine.extract_info_with_retry(text)
            docs.append(doc)

        # deterministic aggregation
        agg_det_engine = self.agg_det()
        agg_det = agg_det_engine.aggregate(docs)

        # LLM aggregation
        agg_llm_engine = self.agg_llm(self.config)
        llm_input = llm.build_llm_aggregation_input(docs, agg_det) 
        agg_llm, _ = agg_llm_engine.aggregate_with_retry(llm_input)

        # decision
        decision_engine = self.decision(self.config)
        decision = decision_engine.decide(agg_llm)

        # report
        rep_builder = self.reporter(agg_llm, decision)
        report = rep_builder.build_md_report()

        return report