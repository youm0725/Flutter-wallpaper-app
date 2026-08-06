import time
import concurrent.futures
import threading
from pathlib import Path
from typing import List, Dict, Callable, Optional
from app.models.imported_wallpaper import ImportedWallpaperItem
from app.models.processing_task import ProcessingTask
from app.services.image_processing_engine import ImageProcessingEngine, QUALITY_PRESETS
from app.core.logger import get_logger

logger = get_logger("ProcessingQueueManager")

class ProcessingQueueManager:
    """Manages multithreaded wallpaper processing queue, controls, and progress tracking."""
    
    def __init__(self):
        self.tasks: List[ProcessingTask] = []
        self.is_running: bool = False
        self.is_paused: bool = False
        self.is_cancelled: bool = False
        
        self.preset: str = "Balanced"
        self.max_workers: int = 4
        
        self.start_time: float = 0.0
        self.total_processed: int = 0

    def add_imported_items(self, items: List[ImportedWallpaperItem], category: str = "general") -> List[ProcessingTask]:
        """Creates processing tasks from imported wallpaper items."""
        new_tasks: List[ProcessingTask] = []
        for item in items:
            # Skip duplicate task for same item
            if any(t.imported_item.id == item.id for t in self.tasks):
                continue
            
            task = ProcessingTask(
                id=f"task_{item.id}",
                imported_item=item,
                category=category,
                status="Waiting",
                original_size_bytes=item.file_size_bytes
            )
            self.tasks.append(task)
            new_tasks.append(task)
            
        logger.info("Added %d items to processing queue. Total queue length: %d", len(new_tasks), len(self.tasks))
        return new_tasks

    def clear_queue(self) -> None:
        """Clears all tasks in queue."""
        if self.is_running:
            self.cancel_processing()
        self.tasks.clear()
        logger.info("Processing queue cleared.")

    def start_processing(
        self,
        preset: str = "Balanced",
        on_progress: Optional[Callable[[Dict], None]] = None,
        on_completed: Optional[Callable[[], None]] = None
    ) -> None:
        """Launches multithreaded processing worker thread."""
        if self.is_running:
            return

        self.preset = preset
        self.is_running = True
        self.is_paused = False
        self.is_cancelled = False
        self.start_time = time.time()

        # Launch background orchestrator thread
        threading.Thread(
            target=self._run_queue_thread,
            args=(on_progress, on_completed),
            daemon=True
        ).start()

    def pause_processing(self) -> None:
        self.is_paused = True
        logger.info("Processing queue paused.")

    def resume_processing(self) -> None:
        self.is_paused = False
        logger.info("Processing queue resumed.")

    def cancel_processing(self) -> None:
        self.is_cancelled = True
        self.is_running = False
        logger.info("Processing queue cancelled.")

    def _run_queue_thread(
        self,
        on_progress: Optional[Callable[[Dict], None]],
        on_completed: Optional[Callable[[], None]]
    ) -> None:
        pending_tasks = [t for t in self.tasks if t.status in ("Waiting", "Failed")]
        total_count = len(pending_tasks)
        
        logger.info("Starting batch processing of %d tasks with preset %s...", total_count, self.preset)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for task in pending_tasks:
                if self.is_cancelled:
                    break

                # Handle Pause
                while self.is_paused and not self.is_cancelled:
                    time.sleep(0.2)

                if self.is_cancelled:
                    break

                future = executor.submit(
                    ImageProcessingEngine.process_wallpaper,
                    task,
                    self.preset
                )
                future_to_task[future] = task

            # Collect results as completed
            completed_count = 0
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                completed_count += 1
                
                # Emit progress status
                if on_progress:
                    stats = self.get_progress_stats(total_count, completed_count)
                    on_progress(stats)

        self.is_running = False
        logger.info("Batch processing finished in %.2fs.", time.time() - self.start_time)
        
        if on_completed:
            on_completed()

    def get_progress_stats(self, total_batch: int = 0, current_done: int = 0) -> Dict:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == "Completed")
        failed = sum(1 for t in self.tasks if t.status == "Failed")
        processing = sum(1 for t in self.tasks if t.status == "Processing")
        waiting = sum(1 for t in self.tasks if t.status == "Waiting")

        elapsed = time.time() - self.start_time if self.is_running else 0.0
        
        pct = (completed / total * 100) if total > 0 else 0.0
        
        # Estimate remaining time
        rate = completed / elapsed if elapsed > 0 and completed > 0 else 0.0
        rem_count = total - completed
        est_rem_seconds = rem_count / rate if rate > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "processing": processing,
            "waiting": waiting,
            "percentage": round(pct, 1),
            "elapsed_seconds": round(elapsed, 1),
            "est_remaining_seconds": round(est_rem_seconds, 1),
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "preset": self.preset
        }
