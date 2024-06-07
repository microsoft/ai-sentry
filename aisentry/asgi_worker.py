import os
from worker.cosmos_logger import cosmos_logger

app_port = os.getenv('COSMOSWORKER_PORT', '7000')
if __name__ == "__main__":
    cosmos_logger.run(host='0.0.0.0', port=7000)