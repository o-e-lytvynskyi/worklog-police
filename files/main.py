import config as configuration
import logging
import report

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
config = configuration.get(logging)

report.make(config, logging)

