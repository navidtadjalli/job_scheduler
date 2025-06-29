from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, detail: str, error_code: str, status_code: int):
        super().__init__(status_code=status_code, detail={"detail": detail, "error_code": error_code})


TaskNotFound = AppException(
    detail="Task not found",
    error_code="TASK_404",
    status_code=status.HTTP_404_NOT_FOUND,
)

SchedulerRemovalFailed = AppException(
    detail="Failed to remove task from scheduler",
    error_code="SCHEDULER_500",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)

TaskCreationFailed = lambda e: AppException(
    detail=f"Failed to create/schedule task: {e}",
    error_code="TASK_CREATE_500",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)

TaskDeletionFailed = lambda e: AppException(
    detail=f"Failed to delete task: {e}",
    error_code="TASK_DELETE_500",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
