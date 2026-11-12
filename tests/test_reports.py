import pytest
from modules.report_generator import ReportGenerator

def test_metrics_calculation_standard_case():
    """Verify standard TP, TN, FP, FN mathematical formulas."""
    metrics = ReportGenerator.calculate_metrics(tp=96, tn=50, fp=0, fn=4, avg_latency_ms=92.4)
    
    # Accuracy = (96 + 50) / 150 = 97.33%
    assert pytest.approx(metrics["accuracy"], 0.01) == 97.33
    # FAR = 0 / 50 = 0.00%
    assert metrics["far"] == 0.0
    # FRR = 4 / 100 = 4.00%
    assert metrics["frr"] == 4.0
    # Precision = 96 / 96 = 100.0%
    assert metrics["precision"] == 100.0
    # Recall = 96 / 100 = 96.0%
    assert metrics["recall"] == 96.0

def test_metrics_zero_division_guard():
    """Metrics must handle zero denominator without crashing."""
    metrics = ReportGenerator.calculate_metrics(tp=0, tn=0, fp=0, fn=0)
    assert metrics["accuracy"] == 0.0
    assert metrics["far"] == 0.0
    assert metrics["frr"] == 0.0
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0

def test_export_markdown_report(tmp_path):
    """Ensure report exporter writes valid markdown file."""
    report = ReportGenerator.generate_default_benchmark()
    out_file = tmp_path / "test_report.md"
    ReportGenerator.export_markdown_report(report, output_path=str(out_file))
    
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "Face Recognition System" in content
    assert "Confusion Matrix" in content

