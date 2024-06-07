import os
from worker.usage_summary import usage_logger


app_port = os.getenv('USAGE_WORKER_PORT', '7001')
if __name__ == "__main__":
    usage_logger.run(host='0.0.0.0', port=7001)