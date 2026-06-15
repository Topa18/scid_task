from .db_corrector import DatabaseCorrector
from config import reference_config, target_config


if __name__ == '__main__':
    corrector = DatabaseCorrector(reference_config, target_config)

    corrector.correct_database()
    
    # С применением изменений
    # corrector.correct_database(dry_run=False)