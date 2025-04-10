using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows;

namespace WindowsMonitor
{
    public class AlertManager
    {
        private readonly Dictionary<string, ATMStatus> atmStatuses;
        private readonly List<AlertSubscriber> subscribers;

        public AlertManager()
        {
            atmStatuses = new Dictionary<string, ATMStatus>();
            subscribers = new List<AlertSubscriber>();
        }

        public void Subscribe(AlertSubscriber subscriber)
        {
            if (!subscribers.Contains(subscriber))
            {
                subscribers.Add(subscriber);
            }
        }

        public void Unsubscribe(AlertSubscriber subscriber)
        {
            subscribers.Remove(subscriber);
        }

        public async Task ProcessAlert(ATMAlert alert)
        {
            try
            {
                // Update ATM status
                UpdateATMStatus(alert);

                // Determine alert severity
                var severity = DetermineAlertSeverity(alert);

                // Create notification
                var notification = new AlertNotification
                {
                    ATM_ID = alert.ATM_ID,
                    Timestamp = alert.Timestamp,
                    Message = FormatAlertMessage(alert),
                    Severity = severity
                };

                // Notify subscribers
                NotifySubscribers(notification);

                // Log alert
                await LogAlert(alert);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error processing alert: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void UpdateATMStatus(ATMAlert alert)
        {
            if (!atmStatuses.ContainsKey(alert.ATM_ID))
            {
                atmStatuses[alert.ATM_ID] = new ATMStatus();
            }

            var status = atmStatuses[alert.ATM_ID];
            status.LastUpdate = alert.Timestamp;
            status.CurrentStatus = alert.Status;
            status.ErrorDetails = alert.ErrorDetails;
        }

        private AlertSeverity DetermineAlertSeverity(ATMAlert alert)
        {
            // Determine severity based on error type and status
            if (alert.Status == "CRITICAL_ERROR")
                return AlertSeverity.Critical;
            if (alert.Status == "MAINTENANCE_MODE")
                return AlertSeverity.Warning;
            if (alert.Status == "OPERATIONAL")
                return AlertSeverity.Info;

            return AlertSeverity.Unknown;
        }

        private string FormatAlertMessage(ATMAlert alert)
        {
            return $"ATM {alert.ATM_ID}: {alert.Status}\nDetails: {alert.ErrorDetails}";
        }

        private void NotifySubscribers(AlertNotification notification)
        {
            foreach (var subscriber in subscribers)
            {
                try
                {
                    subscriber.OnAlert(notification);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error notifying subscriber: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async Task LogAlert(ATMAlert alert)
        {
            try
            {
                // Log alert to database or file
                await Task.CompletedTask; // Placeholder for actual logging implementation
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error logging alert: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        public ATMStatus GetATMStatus(string atmId)
        {
            return atmStatuses.ContainsKey(atmId) ? atmStatuses[atmId] : null;
        }

        public IEnumerable<string> GetAllATMIds()
        {
            return atmStatuses.Keys;
        }
    }

    public class ATMStatus
    {
        public DateTime LastUpdate { get; set; }
        public string CurrentStatus { get; set; }
        public string ErrorDetails { get; set; }
    }

    public class ATMAlert
    {
        public string ATM_ID { get; set; }
        public string Status { get; set; }
        public string ErrorDetails { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class AlertNotification
    {
        public string ATM_ID { get; set; }
        public string Message { get; set; }
        public AlertSeverity Severity { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public enum AlertSeverity
    {
        Critical,
        Warning,
        Info,
        Unknown
    }

    public interface AlertSubscriber
    {
        void OnAlert(AlertNotification notification);
    }
}
