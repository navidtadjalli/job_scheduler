from fastapi import HTTPException, status


class AppException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Application Exception"
    error_code: str = "APP_EXCEPTION"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail={"detail": self.detail, "error_code": self.error_code})


class TaskNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Task not found"
    error_code = "TASK_404"


class TaskCreationFailed(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to create/schedule task"
    error_code = "TASK_CREATE_500"


class TaskDeletionFailed(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = f"Failed to delete task"
    error_code = "TASK_DELETE_500"
