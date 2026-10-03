from configparser import ConfigParser


class Config():
    def __init__(self, config_file = "ai_engineer_tienda_hogar/config.ini"):
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_text_embedding_model(self):
        return self.config['DEFAULT'].get('TEXT_EMBEDDING_MODEL')
        