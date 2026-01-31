"""Job scheduler for periodic data fetching"""

import logging
from typing import List, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class JobScheduler:
    """Job scheduler for managing periodic tasks"""
    
    def __init__(self):
        """Initialize the job scheduler"""
        self.scheduler = BlockingScheduler()
        self._jobs = []
    
    def add_cron_job(
        self,
        func: Callable,
        cron_expression: str,
        job_id: str,
        job_name: str = None
    ) -> None:
        """
        Add a cron-based scheduled job
        
        Args:
            func: Function to execute
            cron_expression: Cron expression (e.g., "0 0 * * *")
            job_id: Unique job identifier
            job_name: Human-readable job name (optional)
        """
        try:
            # Parse cron expression
            parts = cron_expression.strip().split()
            if len(parts) != 5:
                raise ValueError(
                    f"Invalid cron expression: {cron_expression}. "
                    "Expected format: 'minute hour day month day_of_week'"
                )
            
            minute, hour, day, month, day_of_week = parts
            
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                name=job_name or job_id,
                replace_existing=True
            )
            
            self._jobs.append({
                'id': job_id,
                'name': job_name or job_id,
                'cron': cron_expression
            })
            
            logger.info(
                f"Added scheduled job: {job_name or job_id} "
                f"with cron: {cron_expression}"
            )
        
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {str(e)}", exc_info=True)
            raise
    
    def add_interval_job(
        self,
        func: Callable,
        interval_minutes: int,
        job_id: str,
        job_name: str = None
    ) -> None:
        """
        Add an interval-based scheduled job
        
        Args:
            func: Function to execute
            interval_minutes: Interval in minutes
            job_id: Unique job identifier
            job_name: Human-readable job name (optional)
        """
        try:
            self.scheduler.add_job(
                func,
                'interval',
                minutes=interval_minutes,
                id=job_id,
                name=job_name or job_id,
                replace_existing=True
            )
            
            self._jobs.append({
                'id': job_id,
                'name': job_name or job_id,
                'interval': f"{interval_minutes} minutes"
            })
            
            logger.info(
                f"Added interval job: {job_name or job_id} "
                f"every {interval_minutes} minutes"
            )
        
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {str(e)}", exc_info=True)
            raise
    
    def remove_job(self, job_id: str) -> None:
        """
        Remove a scheduled job
        
        Args:
            job_id: Job identifier to remove
        """
        try:
            self.scheduler.remove_job(job_id)
            self._jobs = [job for job in self._jobs if job['id'] != job_id]
            logger.info(f"Removed job: {job_id}")
        
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}", exc_info=True)
    
    def list_jobs(self) -> List[dict]:
        """
        List all scheduled jobs
        
        Returns:
            List of job information dictionaries
        """
        return self._jobs.copy()
    
    def start(self) -> None:
        """Start the scheduler (blocking)"""
        try:
            logger.info("Starting scheduler...")
            logger.info(f"Scheduled jobs: {len(self._jobs)}")
            for job in self._jobs:
                logger.info(f"  - {job}")
            
            self.scheduler.start()
        
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler interrupted, shutting down...")
            self.shutdown()
        
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}", exc_info=True)
            raise
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the scheduler
        
        Args:
            wait: Whether to wait for running jobs to complete
        """
        try:
            logger.info("Shutting down scheduler...")
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler shut down successfully")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)

