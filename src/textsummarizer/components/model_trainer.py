import torch
import os
from textsummarizer.entity import ModelTrainerConfig
from transformers import TrainingArguments,Trainer
from transformers import DataCollatorForSeq2Seq
from transformers import AutoModelForSeq2SeqLM,AutoTokenizer
from datasets import load_from_disk

class Modeltrainer:
    def __init__(self,config: ModelTrainerConfig):
        self.config= config

    def train(self):
        device="cuda" if torch.cuda.is_available() else "cpu"
        tokenizer=AutoTokenizer.from_pretrained(self.config.model_ckpt)
        model_pegasus=AutoModelForSeq2SeqLM.from_pretrained(self.config.model_ckpt).to(device)
        seq2seq_data_collator= DataCollatorForSeq2Seq(tokenizer, model=model_pegasus)

        dataset_samsum_pt= load_from_disk(self.config.data_path)

        trainer_args = TrainingArguments(
        output_dir=self.config.root_dir,
        num_train_epochs=self.config.num_train_epochs,

        per_device_train_batch_size=self.config.per_device_train_batch_size,
        per_device_eval_batch_size=self.config.per_device_eval_batch_size,

        learning_rate= self.config.learning_rate,
        weight_decay=self.config.weight_decay,
        warmup_steps=self.config.warmup_steps,#500 steps tkk lr gradually increase krega ek dum nhi bdate

        logging_steps=self.config.logging_steps,#kitne steps baad trainning ki info print krni h

        eval_strategy=self.config.evaluation_strategy,
        eval_steps=self.config.eval_steps,

        save_strategy=self.config.save_strategy,
        save_total_limit=self.config.save_total_limit
        )

        trainer= Trainer(model=model_pegasus,args=trainer_args,
                         processing_class=tokenizer,data_collator=seq2seq_data_collator,
                         train_dataset=dataset_samsum_pt["train"],eval_dataset=dataset_samsum_pt["validation"])

        trainer.train()

        #save model
        model_pegasus.save_pretrained(os.path.join(self.config.root_dir,"pegasus-samsum-model"))
        #save tokeinzer
        tokenizer.save_pretrained(os.path.join(self.config.root_dir,"tokenizer"))

        



