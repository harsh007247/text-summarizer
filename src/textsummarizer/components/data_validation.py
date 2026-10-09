import os
from textsummarizer.logging import logger
from textsummarizer.entity import datavalidationConfig

class DataValidation:
    def __init__(self,config: datavalidationConfig):
        self.config=config

    def validate_all_files_exists(self)->bool:
        try:
            validate_status=None
            all_files=os.listdir(os.path.join("artifacts","data_ingestion","samsum_dataset"))
            for file in all_files:
                if file not in self.config.ALL_REQUIRED_FILES:
                    validate_status=False
                    with open(self.config.STATUS_FILE,"w") as f:
                        f.write(f"validation status: {validate_status}")

                else:
                    validate_status=True
                    with open(self.config.STATUS_FILE,"w") as f:
                        f.write(f"validation status: {validate_status}")
            return validate_status

        except Exception as e:
            raise e