# © 2024 Banco do Brasil
# Developed by A1051594 - Aprendiz do Banco do Brasil
# All rights reserved.

import logging
import yaml
import time
from typing import Dict, Optional
from logger import setup_logger
from hardware import HardwareInterface
from ai_monitor import AIMonitor
from maintenance import MaintenanceSystem

class ATMSystem:
    def __init__(self, config_path: str = "../config/settings.yml"):
        # Initialize logger
        self.logger = setup_logger()
        self.logger.info("Initializing ATM System")

        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

        # Initialize components
        try:
            self.hardware = HardwareInterface(config_path)
            self.ai_monitor = AIMonitor(config_path)
            self.maintenance = MaintenanceSystem(config_path)
            self.running = False
            self.in_maintenance = False
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise

    def start(self):
        """
        Start the ATM system and begin monitoring
        """
        try:
            self.logger.info("Starting ATM system")
            self.running = True
            self._main_loop()
        except Exception as e:
            self.logger.error(f"Failed to start ATM system: {str(e)}")
            self.shutdown()

    def shutdown(self):
        """
        Gracefully shutdown the ATM system
        """
        self.logger.info("Shutting down ATM system")
        self.running = False
        if self.in_maintenance:
            self.maintenance.exit_maintenance_mode()

    def _main_loop(self):
        """
        Main operational loop of the ATM system
        """
        while self.running:
            try:
                # Skip monitoring if in maintenance mode
                if self.in_maintenance:
                    time.sleep(5)
                    continue

                # Check all hardware components
                status = self.hardware.get_full_status()
                self._process_status(status)

                # Wait before next check
                time.sleep(self.config.get('Hardware', {}).get('Check_Interval', 30))

            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                if self._should_enter_maintenance(str(e)):
                    self._handle_critical_error(str(e))
                time.sleep(5)

    def _process_status(self, status: Dict):
        """
        Process the status of all hardware components
        """
        try:
            for component, details in status.items():
                if not details['status']:  # Component has an error
                    self.logger.warning(f"Error detected in {component}: {details['error']}")
                    
                    # Get AI diagnosis
                    issue_type, diagnosis = self.ai_monitor.diagnose_issue({
                        'component': component,
                        'error': details['error']
                    })

                    # Attempt self-repair if diagnosis is available
                    if issue_type != 'DIAGNOSIS_ERROR':
                        repair_success, repair_details = self.ai_monitor.perform_self_repair(
                            issue_type, diagnosis
                        )

                        if not repair_success:
                            # If repair failed, run maintenance
                            self._handle_repair_failure(component, details['error'], repair_details)
                    else:
                        # If diagnosis failed, enter maintenance mode
                        self._handle_critical_error(f"AI diagnosis failed for {component}")

        except Exception as e:
            self.logger.error(f"Error processing status: {str(e)}")
            self._handle_critical_error(str(e))

    def _handle_repair_failure(self, component: str, error: Dict, repair_details: Optional[Dict]):
        """
        Handle failed repair attempts
        """
        try:
            self.logger.warning(f"Repair failed for {component}")
            
            # Run maintenance routines
            maintenance_success = self.maintenance.run_maintenance({
                'component': component,
                'error': error,
                'repair_attempt': repair_details
            })

            if not maintenance_success:
                self._enter_maintenance_mode({
                    'component': component,
                    'error': error,
                    'repair_attempt': repair_details
                })

        except Exception as e:
            self.logger.error(f"Error handling repair failure: {str(e)}")
            self._handle_critical_error(str(e))

    def _enter_maintenance_mode(self, error_details: Dict):
        """
        Enter maintenance mode
        """
        try:
            self.logger.info("Entering maintenance mode")
            self.in_maintenance = True
            self.maintenance.run_maintenance(error_details)
        except Exception as e:
            self.logger.error(f"Failed to enter maintenance mode: {str(e)}")
            self._handle_critical_error(str(e))

    def _handle_critical_error(self, error: str):
        """
        Handle critical system errors
        """
        self.logger.error(f"Critical error: {error}")
        try:
            # Notify monitoring system of critical error
            self.maintenance.notify_windows_monitor({
                'atm_id': self.config['ATM_ID'],
                'status': 'CRITICAL_ERROR',
                'error': error,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Enter maintenance mode
            self._enter_maintenance_mode({
                'error_type': 'CRITICAL_ERROR',
                'details': error
            })

        except Exception as e:
            self.logger.critical(f"Failed to handle critical error: {str(e)}")
            self.shutdown()

    def _should_enter_maintenance(self, error: str) -> bool:
        """
        Determine if the system should enter maintenance mode based on the error
        """
        critical_keywords = ['CRITICAL', 'FATAL', 'HARDWARE_FAILURE']
        return any(keyword in error.upper() for keyword in critical_keywords)

if __name__ == "__main__":
    try:
        atm = ATMSystem()
        atm.start()
    except Exception as e:
        logging.error(f"Failed to start ATM system: {str(e)}")
        raise
