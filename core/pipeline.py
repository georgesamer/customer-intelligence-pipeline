from data_layer.ingestion.loaders import CSVLoader
from data_layer.processing.cleaner import DataCleaner
from data_layer.processing.transformer import DataTransformer
from ai_engine.trainer import ModelTrainer
from ai_engine.visualizer import Visualizer
from ai_engine.advisor import CustomerAdvisor
from core.config import Config
from utils.logger import setup_logger
from utils.file_utils import ensure_dir


class CustomerPipeline:

    def __init__(self, config_path: str = None):
        self.logger = setup_logger("pipeline")
        self.config = Config(config_path)
        self.logger.info("=" * 60)
        self.logger.info("INITIALIZING CUSTOMER PIPELINE")
        self.logger.info("=" * 60)
        ensure_dir("data")
        ensure_dir("outputs")
        ensure_dir("logs")
        ensure_dir("ai_engine/models")
        self.logger.info("Pipeline initialized successfully")

    def run_from_csv(self, file_path: str = None):
        path = file_path or self.config.csv_path

        self.logger.info(f"\n[1/5] LOADING CSV: {path}")
        loader = CSVLoader(path)
        df = loader.load()
        if df is None:
            self.logger.error("Failed to load data")
            return None
        self.logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        self.logger.info("\n[2/5] CLEANING & TRANSFORMING")
        cleaner = DataCleaner(df, config=self.config.as_dict())
        cleaned_df = cleaner.clean()
        transformer = DataTransformer(cleaned_df, config=self.config.as_dict())
        transformed_df = transformer.transform()
        transformer.export()

        self.logger.info("\n[3/5] TRAINING MODEL")
        trainer = ModelTrainer()
        clustered_df = trainer.train(transformed_df)
        clustered_df.to_csv("outputs/clustered_customers.csv", index=False)

        self.logger.info("\n[4/5] GENERATING CHARTS")
        visualizer = Visualizer(clustered_df)
        visualizer.generate_all()

        self.logger.info("\n[5/5] GETTING AI ADVICE")
        advisor = CustomerAdvisor(model="llama3.1:latest")
        advisor.advise(clustered_df)

        self.logger.info("=" * 60)
        self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 60)

        return clustered_df