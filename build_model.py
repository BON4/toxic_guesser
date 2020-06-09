from constants import BASE_ROOT
from model.build_pipeline import build_model


if __name__ == '__main__':
    dataset_path = BASE_ROOT / 'model' / 'data' / 'train.csv'
    model_path = BASE_ROOT / 'model'
    build_model(dataset_path, model_path)
