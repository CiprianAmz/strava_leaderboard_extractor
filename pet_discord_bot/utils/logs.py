import logging
import os


class TomiStreamHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno == self.level:
            super().emit(record)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
tomi_logger = logging.getLogger(__name__)
tomi_logger.propagate = False
tomi_logger.setLevel(logging.INFO)

stream_handler = TomiStreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), '../../logs/tomi.log'))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

tomi_logger.addHandler(stream_handler)
tomi_logger.addHandler(file_handler)
