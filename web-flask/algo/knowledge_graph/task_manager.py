# MD5: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
"""
Copyright © 2025 羊羊小栈 (GJQ)
Author: 羊羊小栈 | Time: 2025-10-14

原创作品・禁止二次销售!!系统视频、文档禁止二次发布！
违规者需立即停止侵权并按【羊羊小栈系统版权声明及保护条款】赔偿，承担法律责任。
"""

"""
知识图谱构建任务管理器 - 支持异步任务和进度跟踪
"""
import threading
import uuid
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"      # 待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


class BuildTask:
    """构建任务"""

    def __init__(self, task_id: str, task_type: str):
        self.task_id = task_id
        self.task_type = task_type  # 'incremental' or 'full'
        self.status = TaskStatus.PENDING
        self.progress = 0  # 0-100
        self.current_step = ""
        self.total_documents = 0
        self.processed_documents = 0
        self.current_document = ""
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_documents": self.total_documents,
            "processed_documents": self.processed_documents,
            "current_document": self.current_document,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

    def update_progress(self, progress: int, step: str):
        """更新进度"""
        self.progress = min(100, max(0, progress))
        self.current_step = step
        logger.info(f"Task {self.task_id}: {progress}% - {step}")


class TaskManager:
    """任务管理器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tasks: Dict[str, BuildTask] = {}
        self.lock = threading.Lock()
        logger.info("TaskManager initialized")

    def create_task(self, task_type: str) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        task = BuildTask(task_id, task_type)

        with self.lock:
            self.tasks[task_id] = task

        logger.info(f"Created task {task_id} (type: {task_type})")
        return task_id

    def get_task(self, task_id: str) -> Optional[BuildTask]:
        """获取任务"""
        with self.lock:
            return self.tasks.get(task_id)

    def start_task(self, task_id: str):
        """开始执行任务"""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            logger.info(f"Task {task_id} started")

    def complete_task(self, task_id: str, result: Dict[str, Any]):
        """完成任务"""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.result = result
            task.end_time = datetime.now()
            logger.info(f"Task {task_id} completed")

    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = error
            task.end_time = datetime.now()
            logger.error(f"Task {task_id} failed: {error}")

    def update_task_progress(self, task_id: str, progress: int, step: str,
                            total_docs: int = None, processed_docs: int = None,
                            current_doc: str = None):
        """更新任务进度"""
        task = self.get_task(task_id)
        if task:
            task.update_progress(progress, step)
            if total_docs is not None:
                task.total_documents = total_docs
            if processed_docs is not None:
                task.processed_documents = processed_docs
            if current_doc is not None:
                task.current_document = current_doc

    def run_async_task(self, task_id: str, func: Callable, *args, **kwargs):
        """在后台线程中运行任务"""
        def wrapper():
            try:
                self.start_task(task_id)
                result = func(task_id, *args, **kwargs)
                self.complete_task(task_id, result)
            except Exception as e:
                logger.exception(f"Task {task_id} failed with exception")
                self.fail_task(task_id, str(e))

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        logger.info(f"Task {task_id} started in background thread")

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务（可选的定期清理）"""
        now = datetime.now()
        with self.lock:
            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                if task.end_time:
                    age = (now - task.end_time).total_seconds() / 3600
                    if age > max_age_hours:
                        tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self.tasks[task_id]
                logger.info(f"Cleaned up old task {task_id}")


# 全局任务管理器实例
task_manager = TaskManager()
