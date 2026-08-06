import copy
from typing import List, Any, Optional
from app.core.logger import get_logger

logger = get_logger("HistoryService")

class HistoryService:
    """Manages Undo/Redo history state stack for metadata edits."""
    
    def __init__(self, max_history: int = 30):
        self.max_history = max_history
        self.undo_stack: List[Any] = []
        self.redo_stack: List[Any] = []

    def push_state(self, state_snapshot: Any) -> None:
        """Pushes a deep copy snapshot of state to undo stack."""
        snapshot_copy = copy.deepcopy(state_snapshot)
        self.undo_stack.append(snapshot_copy)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        logger.info("Pushed state to history stack. Current stack size: %d", len(self.undo_stack))

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 1

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self, current_state: Any) -> Optional[Any]:
        """Reverts to previous state snapshot."""
        if not self.can_undo():
            logger.info("Undo requested but stack empty.")
            return None
        
        # Save current state to redo stack
        self.redo_stack.append(copy.deepcopy(current_state))
        
        # Pop previous state
        previous_state = self.undo_stack.pop()
        logger.info("Executed Undo. Undo stack size: %d, Redo stack size: %d", len(self.undo_stack), len(self.redo_stack))
        return copy.deepcopy(previous_state)

    def redo(self, current_state: Any) -> Optional[Any]:
        """Redoes previously undone state."""
        if not self.can_redo():
            return None

        self.undo_stack.append(copy.deepcopy(current_state))
        next_state = self.redo_stack.pop()
        logger.info("Executed Redo. Undo stack size: %d, Redo stack size: %d", len(self.undo_stack), len(self.redo_stack))
        return copy.deepcopy(next_state)

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
