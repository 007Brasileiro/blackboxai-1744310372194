# © 2024 Banco do Brasil
# Developed by A1051594 - Aprendiz do Banco do Brasil
# All rights reserved.

import logging
import yaml
from typing import Dict, Tuple, Optional

class HardwareInterface:
    def __init__(self, config_path: str = "../config/settings.yml"):
        self.logger = logging.getLogger('ATMLogger')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['Hardware']
        
    def check_cash_dispenser(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check cash dispenser status including cash levels and mechanical status
        Returns: (status_ok, error_details if any)
        """
        try:
            # Simulate hardware checks
            cash_level = 1500  # This would be actual sensor reading
            if cash_level < self.config['Cash_Dispenser']['Low_Cash_Threshold']:
                return False, {
                    'error_type': 'LOW_CASH',
                    'current_level': cash_level,
                    'threshold': self.config['Cash_Dispenser']['Low_Cash_Threshold']
                }
            return True, None
        except Exception as e:
            self.logger.error(f"Cash dispenser check failed: {str(e)}")
            return False, {'error_type': 'HARDWARE_ERROR', 'details': str(e)}

    def check_card_reader(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check card reader status including connection and mechanical status
        Returns: (status_ok, error_details if any)
        """
        try:
            # Simulate card reader check
            reader_connected = True  # This would be actual hardware check
            if not reader_connected:
                return False, {
                    'error_type': 'READER_DISCONNECTED',
                    'last_status': 'disconnected'
                }
            return True, None
        except Exception as e:
            self.logger.error(f"Card reader check failed: {str(e)}")
            return False, {'error_type': 'HARDWARE_ERROR', 'details': str(e)}

    def check_printer(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check printer status including paper level and connection
        Returns: (status_ok, error_details if any)
        """
        try:
            # Simulate printer check
            paper_level = 200  # This would be actual sensor reading
            if paper_level < self.config['Printer']['Paper_Low_Threshold']:
                return False, {
                    'error_type': 'LOW_PAPER',
                    'current_level': paper_level,
                    'threshold': self.config['Printer']['Paper_Low_Threshold']
                }
            return True, None
        except Exception as e:
            self.logger.error(f"Printer check failed: {str(e)}")
            return False, {'error_type': 'HARDWARE_ERROR', 'details': str(e)}

    def check_display(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check display status including connection and touch functionality
        Returns: (status_ok, error_details if any)
        """
        try:
            # Simulate display check
            display_working = True  # This would be actual hardware check
            touch_working = True    # This would be actual hardware check
            
            if not display_working:
                return False, {'error_type': 'DISPLAY_ERROR', 'details': 'Display not responding'}
            if not touch_working:
                return False, {'error_type': 'TOUCH_ERROR', 'details': 'Touch functionality not working'}
            return True, None
        except Exception as e:
            self.logger.error(f"Display check failed: {str(e)}")
            return False, {'error_type': 'HARDWARE_ERROR', 'details': str(e)}

    def reset_device(self, device_type: str) -> bool:
        """
        Attempt to reset a specific hardware device
        Returns: True if reset successful, False otherwise
        """
        try:
            self.logger.info(f"Attempting to reset {device_type}")
            # Implement actual reset logic here
            return True
        except Exception as e:
            self.logger.error(f"Reset failed for {device_type}: {str(e)}")
            return False

    def get_full_status(self) -> Dict:
        """
        Get comprehensive status of all hardware components
        Returns: Dictionary with status of all components
        """
        cash_status, cash_error = self.check_cash_dispenser()
        card_status, card_error = self.check_card_reader()
        printer_status, printer_error = self.check_printer()
        display_status, display_error = self.check_display()

        return {
            'cash_dispenser': {
                'status': cash_status,
                'error': cash_error
            },
            'card_reader': {
                'status': card_status,
                'error': card_error
            },
            'printer': {
                'status': printer_status,
                'error': printer_error
            },
            'display': {
                'status': display_status,
                'error': display_error
            }
        }
