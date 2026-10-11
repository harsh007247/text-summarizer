from textsummarizer.constants import *
from textsummarizer.utils.common import read_yaml, creat_directories
from textsummarizer.entity import (DataIngestionConfig,datavalidationConfig,
                                   datatransformationConfig,ModelTrainerConfig,ModelEvaluationConfig)

class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        creat_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        creat_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_url=config.source_url,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir
        )

        return data_ingestion_config
    
    def get_data_validation_config(self) -> datavalidationConfig:
        config=self.config.data_validation
        creat_directories([config.root_dir])

        data_validation_config= datavalidationConfig(
            root_dir=config.root_dir,
            STATUS_FILE=config.STATUS_FILE,
            ALL_REQUIRED_FILES= config.ALL_REQUIRED_FILES,
            )
        return data_validation_config

    def get_data_transformation_config(self) -> datatransformationConfig:
        config=self.config.data_transformation
        creat_directories([config.root_dir])

        data_transformation_config= datatransformationConfig(
            root_dir=config.root_dir,
            data_path=config.data_path,
            tokenizer_name= config.tokenizer_name,
            )
        return data_transformation_config
    
    def get_model_trainer_config(self)-> ModelTrainerConfig:
        config= self.config.model_trainer
        params=self.params.TrainingArguments
        creat_directories([config.root_dir])
        model_trainer_config = ModelTrainerConfig(
                root_dir= config.root_dir,
                data_path= config.data_path,
                model_ckpt= config.model_ckpt,
                num_train_epochs= params.num_train_epochs,
                learning_rate= params.learning_rate, 
                warmup_steps= params.warmup_steps,
                per_device_train_batch_size= params.per_device_train_batch_size,
                per_device_eval_batch_size= params.per_device_eval_batch_size,
                weight_decay= params.weight_decay,
                logging_steps= params.logging_steps,
                evaluation_strategy= params.evaluation_strategy,
                eval_steps= params.eval_steps,
                save_steps= params.save_Steps,
                gradient_accumulation_steps= params.gradient_accumulation_steps,
                save_strategy= params.save_strategy,
                save_total_limit= params.save_total_limit 
        )

        return model_trainer_config

    def get_model_evaluation_config(self)-> ModelEvaluationConfig:
        config=self.config.model_evaluation
        creat_directories([config.root_dir])
        model_evaluation_config= ModelEvaluationConfig(
            root_dir=config.root_dir,
            data_path= config.data_path,
            model_path= config.model_path,
            tokenizer_path= config.tokenizer_path,
            metric_file_name= config.metric_file_name
        )
        return model_evaluation_config