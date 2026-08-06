import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple

from app.utils.path_helper import PathHelper
from app.services.asset_validator_service import AssetValidatorService
from app.services.size_analyzer_service import SizeAnalyzerService
from app.services.metadata_service import MetadataService
from app.services.metadata_validation_service import MetadataValidationService
from app.services.flutter_detector_service import FlutterDetectorService
from app.core.logger import get_logger

logger = get_logger("ReleaseValidatorService")

class ReleaseValidatorService:
    """Master Release Validation service orchestrating all scanners and report generation."""
    
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()
        self.metadata_service = MetadataService(workspace_root=self.workspace_root)
        self.detector_service = FlutterDetectorService(workspace_root=self.workspace_root)
        
        self.reports_dir = PathHelper.get_tool_root() / "logs" / "validation_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.reports_dir / "history.json"

    def run_full_validation(self) -> Dict[str, Any]:
        """Runs complete release validation audit across all categories."""
        start_time = time.time()
        all_issues: List[Dict[str, Any]] = []

        # 1. Asset Validation
        asset_issues = AssetValidatorService.audit_assets(self.workspace_root)
        all_issues.extend(asset_issues)

        # 2. Metadata Validation
        wallpapers = self.metadata_service.load_wallpapers_json()
        categories = self.metadata_service.load_categories_json()
        collections = self.metadata_service.load_collections_json()
        
        is_meta_ok, meta_issues = MetadataValidationService.validate_metadata(
            wallpapers, categories, collections, workspace_root=self.workspace_root
        )
        for issue in meta_issues:
            all_issues.append({
                "category": "Metadata Validation",
                "severity": issue["type"],
                "location": f"ID: {issue['id']}",
                "problem": issue["message"],
                "fix": "Edit metadata record in Metadata Manager screen."
            })

        # 3. Size Analysis
        size_results = SizeAnalyzerService.analyze_storage_size(self.workspace_root)
        all_issues.extend(size_results["issues"])

        # 4. Flutter Project Validation
        pubspec_ok, warnings = self.detector_service.verify_pubspec_assets()
        for warn in warnings:
            all_issues.append({
                "category": "Flutter Workspace",
                "severity": "Warning",
                "location": "pubspec.yaml",
                "problem": warn,
                "fix": "Add missing asset paths to pubspec.yaml assets section."
            })

        # Aggregate Statistics
        error_count = sum(1 for i in all_issues if i["severity"] == "Error")
        warning_count = sum(1 for i in all_issues if i["severity"] == "Warning")
        pass_count = max(0, len(wallpapers) * 5 - len(all_issues))
        total_checks = pass_count + len(all_issues)
        
        duration = round(time.time() - start_time, 2)

        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration,
            "total_checks": total_checks,
            "pass_count": pass_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "storage_stats": size_results,
            "issues": all_issues
        }

        # Save History Snapshot & Reports
        self._save_to_history(results)
        self.export_html_report(results)
        self.export_json_report(results)
        self.export_text_report(results)

        logger.info("Full validation completed in %.2fs. Checks: %d, Passed: %d, Warnings: %d, Errors: %d",
                    duration, total_checks, pass_count, warning_count, error_count)
        return results

    def _save_to_history(self, results: Dict[str, Any]) -> None:
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.insert(0, {
            "timestamp": results["timestamp"],
            "total_checks": results["total_checks"],
            "pass_count": results["pass_count"],
            "warning_count": results["warning_count"],
            "error_count": results["error_count"],
            "total_size_mb": results["storage_stats"]["total_size_mb"]
        })
        history = history[:20]  # Keep last 20 runs

        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error("Failed saving validation history: %s", e)

    def export_text_report(self, results: Dict[str, Any]) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"validation_report_{timestamp}.txt"
        
        lines = [
            "==========================================================",
            "WALLPAPER GALLERY — RELEASE VALIDATION REPORT",
            "==========================================================",
            f"Timestamp: {results['timestamp']}",
            f"Duration: {results['duration_seconds']}s",
            "",
            "SUMMARY STATS:",
            f"  - Total Checks Run: {results['total_checks']}",
            f"  - Passed:           {results['pass_count']}",
            f"  - Warnings:         {results['warning_count']}",
            f"  - Errors:           {results['error_count']}",
            f"  - Total Asset Size: {results['storage_stats']['total_size_mb']} MB",
            "",
            "DETAILED ISSUES & FIX SUGGESTIONS:",
        ]

        if not results["issues"]:
            lines.append("  ✓ All release quality validation checks passed cleanly!")
        else:
            for idx, issue in enumerate(results["issues"], 1):
                lines.extend([
                    f"[{idx}] {issue['severity'].upper()} - {issue['category']}",
                    f"    Location: {issue['location']}",
                    f"    Problem:  {issue['problem']}",
                    f"    Fix:      {issue['fix']}",
                    ""
                ])

        lines.append("==========================================================")
        report_file.write_text("\n".join(lines), encoding="utf-8")
        return report_file

    def export_json_report(self, results: Dict[str, Any]) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"validation_report_{timestamp}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        return report_file

    def export_html_report(self, results: Dict[str, Any]) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"validation_report_{timestamp}.html"

        issue_rows = ""
        for issue in results["issues"]:
            color = "#EF4444" if issue["severity"] == "Error" else "#F59E0B"
            issue_rows += f"""
            <tr>
                <td><span style="background:{color}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold;">{issue['severity']}</span></td>
                <td><b>{issue['category']}</b></td>
                <td><code>{issue['location']}</code></td>
                <td>{issue['problem']}</td>
                <td style="color:#10B981; font-weight:bold;">{issue['fix']}</td>
            </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Release Validation Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0F172A; color: #F8FAFC; padding: 20px; }}
                h1 {{ color: #38BDF8; }}
                .card {{ background: #1E293B; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #334155; }}
                th {{ background: #334155; }}
            </style>
        </head>
        <body>
            <h1>🛡️ Flutter Wallpaper Gallery — Release Validation Report</h1>
            <div class="card">
                <h3>Scan Summary ({results['timestamp']})</h3>
                <p><b>Total Checks:</b> {results['total_checks']} | <b>Passed:</b> {results['pass_count']} | <b>Warnings:</b> {results['warning_count']} | <b>Errors:</b> {results['error_count']}</p>
                <p><b>Total App Asset Size:</b> {results['storage_stats']['total_size_mb']} MB</p>
            </div>
            <div class="card">
                <h3>Audit Issues & Actionable Fixes</h3>
                <table>
                    <thead>
                        <tr><th>Severity</th><th>Category</th><th>Location</th><th>Problem</th><th>Actionable Fix</th></tr>
                    </thead>
                    <tbody>
                        {issue_rows if issue_rows else '<tr><td colspan="5">✓ All checks passed cleanly! Ready for release.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        report_file.write_text(html_content, encoding="utf-8")
        return report_file
