class FinAppApiConfig:
    def __init__(self, config):
        if 'logFilePath' not in config:
            raise KeyError("Missing mandatory log file path in config.")
        if 'dbConnString' not in config:
            raise KeyError("Missing mandatory db connection string in config.")
        self.log_file_path = config['logFilePath']
        self.db_conn_str = config['dbConnString']

def init_config(config):
    global global_api_config
    global_api_config = FinAppApiConfig(config)