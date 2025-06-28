"""
Reconnaissance Tasks
"""
from app.core.celery import celery_app
from app.modules.recon.scanner import ReconScanner


@celery_app.task(bind=True)
def run_recon_scan(self, target: str, scan_type: str = "basic"):
    """
    Run reconnaissance scan as background task
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'progress': 0})
        
        # Initialize scanner
        scanner = ReconScanner()
        
        # Run scan based on type
        if scan_type == "basic":
            results = scanner.run_full_scan(target)
        else:
            results = scanner.run_full_scan(target)
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 100})
        
        return {
            'status': 'completed',
            'results': results
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        } 