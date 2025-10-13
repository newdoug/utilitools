import logging
import os

from . import ElasticsearchLogSettings, LOG, set_up_logger

es_host = os.getenv("ES_HOST", "localhost")
es_port = os.getenv("ES_PORT", "9200")
es_username = os.getenv("ES_USERNAME", "elastic")
es_password = os.getenv("ES_PASSWORD", "")
set_up_logger(
    log_level=os.getenv("LOG_LEVEL", logging.DEBUG),
    # use_es=ElasticsearchLogSettings(
    #     url=f"https://{es_host}:{es_port}", username=es_username, password=es_password
    # ),
)
LOG.trace("Test TRACE message")
LOG.debug("Test DEBUG message")
LOG.info("Test INFO message")
LOG.warning("Test WARNING message")
LOG.error("Test ERROR message")
LOG.critical("Test CRITICAL message")
