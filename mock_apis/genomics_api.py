"""Genomics API — Quality Checks & Assay Status (port 8003)."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

QC_RECORDS = {
    "BeadChip": {"product": "BeadChip", "passed_qc": True, "defect_rate": 0.02,
                 "concordance": 0.995, "grade": "A", "last_tested": "2026-06-07T14:20:00Z",
                 "next_test_due": "2026-07-07"},
    "NextSeq":  {"product": "NextSeq",  "passed_qc": True, "defect_rate": 0.05,
                 "concordance": 0.988, "grade": "B", "last_tested": "2026-06-06T10:00:00Z",
                 "next_test_due": "2026-07-06"},
    "HiSeq":    {"product": "HiSeq",    "passed_qc": False, "defect_rate": 0.12,
                 "concordance": 0.971, "grade": "C", "last_tested": "2026-06-05T08:30:00Z",
                 "next_test_due": "2026-06-19"},
}

ASSAYS = {
    "ASY-789": {"assay_id": "ASY-789", "status": "completed", "variants_detected": 42,
                "confidence_threshold": 0.99, "samples_processed": 100},
    "ASY-790": {"assay_id": "ASY-790", "status": "running",   "variants_detected": 0,
                "confidence_threshold": 0.99, "samples_processed": 30},
    "ASY-791": {"assay_id": "ASY-791", "status": "failed",    "variants_detected": 0,
                "confidence_threshold": 0.99, "samples_processed": 5,
                "failure_reason": "Low input material"},
}


app = FastAPI(title="Genomics API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/genomics/qc")
def get_qc(product: str):
    """Return QC metrics for a product."""
    if product not in QC_RECORDS:
        raise HTTPException(status_code=404, detail=f"No QC data for product '{product}'")
    return QC_RECORDS[product]


@app.get("/genomics/assay-status")
def get_assay_status(assay_id: str):
    """Return assay run status and results."""
    if assay_id not in ASSAYS:
        raise HTTPException(status_code=404, detail=f"Assay '{assay_id}' not found")
    return ASSAYS[assay_id]


@app.get("/health")
def health():
    return {"service": "Genomics API", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_apis.genomics_api:app", host="0.0.0.0", port=8003, reload=True)
