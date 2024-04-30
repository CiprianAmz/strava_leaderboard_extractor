import logging


class TomiStreamHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno == self.level:
            super().emit(record)


tomi_logger = logging.getLogger(__name__)
tomi_logger.propagate = False
tomi_logger.setLevel(logging.INFO)

stream_handler = TomiStreamHandler()
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("../logs/tomi.log")
file_handler.setLevel(logging.WARNING)

tomi_logger.addHandler(stream_handler)
tomi_logger.addHandler(file_handler)
