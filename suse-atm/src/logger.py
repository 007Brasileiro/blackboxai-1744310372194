# © 2024 Banco do Brasil
# Developed by A1051594 - Aprendiz do Banco do Brasil
# All rights reserved.

import logging

def setup_logger():
    logger = logging.getLogger('ATMLogger')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('atm_log.txt')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
