from db.models import *

def add_log_to_session(session, log_type, message, data):
    log = Log(log_type=log_type, message=message, data=data)
    session.add(log)
    return log

def add_cron_job_run_info_to_session(session, log_type, message, data, success):
    log = add_log_to_session(session, log_type, message, data)
    session.flush()
    run = CronJobRun(log_id=log.id, success=success)
    session.add(run)