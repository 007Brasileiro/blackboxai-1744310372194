# © 2024 Banco do Brasil
# Developed by A1051594 - Aprendiz do Banco do Brasil
# All rights reserved.

import logging
import yaml
import json
import requests
import subprocess
from typing import Dict, Optional, List
from datetime import datetime
import threading
import webbrowser

class MaintenanceSystem:
    def __init__(self, config_path: str = "../config/settings.yml"):
        self.logger = logging.getLogger('ATMLogger')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self.network_config = config['Network']
            self.maintenance_config = config['Maintenance_Thresholds']
            self.security_config = config['Security']

        self.maintenance_mode = False
        self.error_history: List[Dict] = []
        self.maintenance_ui_server = None

    def run_maintenance(self, error_details: Dict) -> bool:
        """
        Execute maintenance routines based on error details
        Returns: True if maintenance was successful, False otherwise
        """
        try:
            self.logger.info(f"Starting maintenance routine for error: {error_details}")
            
            # Add error to history
            self.error_history.append({
                'timestamp': datetime.now().isoformat(),
                'error': error_details
            })

            # Check if error threshold is exceeded
            if self._check_error_threshold(error_details['error_type']):
                self.logger.warning(f"Error threshold exceeded for {error_details['error_type']}")
                self._enter_maintenance_mode(error_details)
                return False

            # Attempt automated repair
            success = self._perform_automated_repair(error_details)
            
            # Notify Windows monitoring system
            self.notify_windows_monitor({
                'atm_id': self.network_config['ATM_ID'],
                'error_details': error_details,
                'maintenance_status': 'SUCCESS' if success else 'FAILED',
                'timestamp': datetime.now().isoformat()
            })

            return success

        except Exception as e:
            self.logger.error(f"Maintenance routine failed: {str(e)}")
            self.notify_windows_monitor({
                'atm_id': self.network_config['ATM_ID'],
                'error': str(e),
                'maintenance_status': 'ERROR',
                'timestamp': datetime.now().isoformat()
            })
            return False

    def _check_error_threshold(self, error_type: str) -> bool:
        """
        Check if number of errors exceeds threshold
        """
        recent_errors = [
            e for e in self.error_history 
            if e['error']['error_type'] == error_type and 
            (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 
            self.maintenance_config['Auto_Reset_Interval']
        ]
        
        threshold = self.maintenance_config.get(f'Max_{error_type}', 3)
        return len(recent_errors) >= threshold

    def _perform_automated_repair(self, error_details: Dict) -> bool:
        """
        Attempt automated repair based on error type
        """
        try:
            repair_actions = {
                'NOTE_JAM': self._clear_note_jam,
                'CARD_READER_ERROR': self._reset_card_reader,
                'PRINTER_ERROR': self._reset_printer,
                'DISPLAY_ERROR': self._reset_display
            }

            repair_func = repair_actions.get(error_details['error_type'])
            if repair_func:
                return repair_func()
            
            self.logger.warning(f"No automated repair available for {error_details['error_type']}")
            return False

        except Exception as e:
            self.logger.error(f"Automated repair failed: {str(e)}")
            return False

    def _enter_maintenance_mode(self, error_details: Dict):
        """
        Enter maintenance mode and launch maintenance UI
        """
        try:
            self.maintenance_mode = True
            self.logger.info("Entering maintenance mode")

            # Start maintenance UI server
            self._start_maintenance_ui_server()

            # Notify Windows monitoring system
            self.notify_windows_monitor({
                'atm_id': self.network_config['ATM_ID'],
                'status': 'MAINTENANCE_MODE',
                'error_details': error_details,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            self.logger.error(f"Failed to enter maintenance mode: {str(e)}")

    def _start_maintenance_ui_server(self):
        """
        Start a simple HTTP server for the maintenance UI
        """
        try:
            # Kill any existing process using port 8000
            subprocess.run(['pkill', '-f', 'python.*http.server.*8000'], 
                         stderr=subprocess.DEVNULL)
            
            # Start new server in a separate thread
            server_thread = threading.Thread(
                target=lambda: subprocess.run([
                    'python3', '-m', 'http.server', '8000', 
                    '-d', '../ui'
                ])
            )
            server_thread.daemon = True
            server_thread.start()
            
            self.maintenance_ui_server = server_thread
            self.logger.info("Maintenance UI server started")

        except Exception as e:
            self.logger.error(f"Failed to start maintenance UI server: {str(e)}")
            raise

    def notify_windows_monitor(self, notification_data: Dict):
        """
        Send notification to Windows monitoring system
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.security_config["Auth_Token"]}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.network_config['Windows_Monitor_Endpoint'],
                json=notification_data,
                headers=headers,
                verify=self.security_config['SSL_Cert_Path'],
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"Notification failed: {response.text}")

            self.logger.info("Successfully notified Windows monitoring system")

        except Exception as e:
            self.logger.error(f"Failed to notify Windows monitor: {str(e)}")
            # Continue execution even if notification fails

    # Hardware-specific repair routines
    def _clear_note_jam(self) -> bool:
        """Attempt to clear a note jam"""
        try:
            # Implement note jam clearing logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear note jam: {str(e)}")
            return False

    def _reset_card_reader(self) -> bool:
        """Reset the card reader"""
        try:
            # Implement card reader reset logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset card reader: {str(e)}")
            return False

    def _reset_printer(self) -> bool:
        """Reset the printer"""
        try:
            # Implement printer reset logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset printer: {str(e)}")
            return False

    def _reset_display(self) -> bool:
        """Reset the display"""
        try:
            # Implement display reset logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset display: {str(e)}")
            return False

    def exit_maintenance_mode(self) -> bool:
        """
        Exit maintenance mode
        """
        try:
            if self.maintenance_ui_server:
                # Stop the maintenance UI server
                subprocess.run(['pkill', '-f', 'python.*http.server.*8000'], 
                             stderr=subprocess.DEVNULL)
                self.maintenance_ui_server = None

            self.maintenance_mode = False
            self.logger.info("Exited maintenance mode")
            
            # Notify Windows monitoring system
            self.notify_windows_monitor({
                'atm_id': self.network_config['ATM_ID'],
                'status': 'OPERATIONAL',
                'timestamp': datetime.now().isoformat()
            })
            
            return True

        except Exception as e:
            self.logger.error(f"Failed to exit maintenance mode: {str(e)}")
            return False
