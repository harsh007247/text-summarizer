from textsummarizer.config.configuration import ConfigurationManager
from textsummarizer.components.model_trainer import Modeltrainer

class ModelTrainerTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        model_trainer_config = config.get_model_trainer_config()
        model_trainer = Modeltrainer(config=model_trainer_config)
        model_trainer.train()