import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Callable
from app.utils.path_helper import PathHelper
from app.core.logger import get_logger

logger = get_logger("GitService")

class GitService:
    """Service managing Git staging, committing, and remote GitHub repository pushing."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or PathHelper.get_workspace_root()

    def _run_git_cmd(
        self,
        args: List[str],
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[int, str]:
        """Runs git subprocess command in workspace directory."""
        cmd = ["git"] + args
        logger.info("Executing Git command: %s in %s", " ".join(cmd), self.workspace_root)
        if log_callback:
            log_callback(f"Executing: {' '.join(cmd)}\n")

        full_output = []
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                encoding="utf-8",
                errors="replace"
            )

            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    full_output.append(line)
                    if log_callback:
                        log_callback(line)

            process.wait()
            return process.returncode, "".join(full_output)
        except Exception as e:
            err_msg = f"Failed to execute Git command: {e}"
            logger.error(err_msg)
            if log_callback:
                log_callback(err_msg + "\n")
            return -1, err_msg

    def get_git_status(self) -> Dict[str, Any]:
        """Returns workspace git status details."""
        code, output = self._run_git_cmd(["status", "--porcelain"])
        changed_files = [line.strip() for line in output.splitlines() if line.strip()]
        
        b_code, b_output = self._run_git_cmd(["branch", "--show-current"])
        branch = b_output.strip() or "main"

        return {
            "is_clean": len(changed_files) == 0,
            "uncommitted_count": len(changed_files),
            "branch": branch,
            "changed_files": changed_files
        }

    def commit_and_push(
        self,
        commit_message: str = "Updated wallpaper gallery assets & metadata via Asset Manager",
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Stages all changes, commits, and pushes to remote GitHub repository."""
        start_time = time.time()
        
        if log_callback:
            log_callback(f"\n==================================================\n")
            log_callback(f"🚀 STARTING GITHUB SYNC & PUSH PROCESS\n")
            log_callback(f"==================================================\n")

        # Step 1: Stage all changes
        add_code, add_logs = self._run_git_cmd(["add", "-A"], log_callback=log_callback)
        if add_code != 0:
            msg = f"❌ Git staging failed: {add_logs}"
            logger.error(msg)
            return {"success": False, "message": msg, "duration_seconds": 0.0}

        # Step 2: Commit changes
        clean_msg = commit_message.strip() or "Updated wallpaper gallery assets & metadata via Asset Manager"
        commit_code, commit_logs = self._run_git_cmd(["commit", "-m", clean_msg], log_callback=log_callback)

        if "nothing to commit" in commit_logs.lower() or "working tree clean" in commit_logs.lower():
            if log_callback:
                log_callback("\n[INFO] Nothing new to commit. Proceeding to verify remote repository push...\n")
        elif commit_code != 0:
            msg = f"❌ Git commit failed: {commit_logs}"
            logger.error(msg)
            return {"success": False, "message": msg, "duration_seconds": 0.0}

        # Step 3: Get active branch
        _, b_out = self._run_git_cmd(["branch", "--show-current"])
        branch = b_out.strip() or "main"

        # Step 4: Push to GitHub remote repository
        push_code, push_logs = self._run_git_cmd(["push", "origin", branch], log_callback=log_callback)
        duration = round(time.time() - start_time, 2)

        if push_code == 0:
            msg = f"✓ Successfully pushed all changes to GitHub origin/{branch} in {duration}s!"
            logger.info(msg)
            if log_callback:
                log_callback(f"\n[OK] {msg}\n")
            return {
                "success": True,
                "branch": branch,
                "duration_seconds": duration,
                "message": msg
            }
        else:
            msg = f"❌ Git push failed (Exit code {push_code}). See log for details."
            logger.error(msg)
            if log_callback:
                log_callback(f"\n[ERROR] {msg}\n")
            return {
                "success": False,
                "branch": branch,
                "duration_seconds": duration,
                "message": msg
            }
