import logging


def init_logger():
    _logger = logging.getLogger('real_estate_project')
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    return _logger


logger = init_logger()
