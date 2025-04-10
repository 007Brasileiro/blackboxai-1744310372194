# © 2024 Banco do Brasil
# Developed by A1051594 - Aprendiz do Banco do Brasil
# All rights reserved.

import logging
import yaml
import json
import requests
from typing import Dict, Tuple, Optional
from time import sleep

class AIMonitor:
    def __init__(self, config_path: str = "../config/settings.yml"):
        self.logger = logging.getLogger('ATMLogger')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self.ai_config = config['OpenRouteAI']
            self.maintenance_config = config['Maintenance_Thresholds']
        
        self.api_key = self.ai_config['API_Key']
        self.endpoint = self.ai_config['Endpoint']
        self.max_retries = self.ai_config['Max_Retries']
        self.timeout = self.ai_config['Timeout']

    def diagnose_issue(self, sensor_data: Dict) -> Tuple[str, Dict]:
        """
        Diagnose issues using OpenRoute AI based on sensor data
        Returns: (issue_type, diagnosis_details)
        """
        try:
            # Prepare the prompt for AI analysis
            prompt = self._prepare_diagnostic_prompt(sensor_data)
            
            # Make API call with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = self._call_openroute_ai(prompt)
                    diagnosis = self._parse_ai_response(response)
                    return diagnosis['issue_type'], diagnosis['details']
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise
                    sleep(2 ** attempt)  # Exponential backoff
                    
        except Exception as e:
            self.logger.error(f"AI diagnosis failed: {str(e)}")
            return 'DIAGNOSIS_ERROR', {'error': str(e)}

    def perform_self_repair(self, issue_type: str, diagnosis_details: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Attempt self-repair based on AI diagnosis
        Returns: (success, repair_details if any)
        """
        try:
            # Generate repair strategy using AI
            repair_prompt = self._prepare_repair_prompt(issue_type, diagnosis_details)
            repair_strategy = self._call_openroute_ai(repair_prompt)
            
            # Execute repair strategy
            success = self._execute_repair_strategy(repair_strategy)
            
            if success:
                self.logger.info(f"Self-repair successful for issue: {issue_type}")
                return True, {"repair_action": repair_strategy}
            else:
                self.logger.warning(f"Self-repair failed for issue: {issue_type}")
                return False, {"failed_repair": repair_strategy}
                
        except Exception as e:
            self.logger.error(f"Self-repair failed: {str(e)}")
            return False, {"error": str(e)}

    def _prepare_diagnostic_prompt(self, sensor_data: Dict) -> str:
        """
        Prepare a detailed prompt for AI diagnosis
        """
        return json.dumps({
            "task": "diagnose_atm_issue",
            "sensor_data": sensor_data,
            "thresholds": self.maintenance_config
        })

    def _prepare_repair_prompt(self, issue_type: str, diagnosis_details: Dict) -> str:
        """
        Prepare a prompt for AI repair strategy
        """
        return json.dumps({
            "task": "generate_repair_strategy",
            "issue_type": issue_type,
            "diagnosis": diagnosis_details,
            "maintenance_thresholds": self.maintenance_config
        })

    def _call_openroute_ai(self, prompt: str) -> Dict:
        """
        Make API call to OpenRoute AI
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.endpoint,
            headers=headers,
            json={"prompt": prompt},
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"AI API call failed: {response.text}")
            
        return response.json()

    def _parse_ai_response(self, response: Dict) -> Dict:
        """
        Parse and validate AI response
        """
        try:
            # Extract relevant information from AI response
            parsed = {
                'issue_type': response.get('diagnosis', {}).get('type'),
                'details': response.get('diagnosis', {}).get('details')
            }
            
            if not parsed['issue_type'] or not parsed['details']:
                raise ValueError("Invalid AI response format")
                
            return parsed
            
        except Exception as e:
            raise Exception(f"Failed to parse AI response: {str(e)}")

    def _execute_repair_strategy(self, strategy: Dict) -> bool:
        """
        Execute the repair strategy provided by AI
        Returns: True if repair was successful, False otherwise
        """
        try:
            # Implement the repair strategy
            # This would involve calling appropriate hardware control functions
            # based on the AI-provided strategy
            
            # For simulation purposes:
            if strategy.get('repair_confidence', 0) > 0.8:
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to execute repair strategy: {str(e)}")
            return False

    def get_maintenance_recommendation(self, error_history: list) -> Dict:
        """
        Get AI recommendation for maintenance based on error history
        """
        try:
            prompt = json.dumps({
                "task": "maintenance_recommendation",
                "error_history": error_history,
                "thresholds": self.maintenance_config
            })
            
            response = self._call_openroute_ai(prompt)
            return {
                "recommended_action": response.get("recommendation"),
                "urgency_level": response.get("urgency"),
                "details": response.get("details")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get maintenance recommendation: {str(e)}")
            return {
                "recommended_action": "MANUAL_CHECK_REQUIRED",
                "urgency_level": "HIGH",
                "details": f"Failed to get AI recommendation: {str(e)}"
            }
