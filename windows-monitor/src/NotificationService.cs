using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;
using System.Threading;
using System.Collections.Generic;
using System.Net.Http.Headers;

namespace WindowsMonitor
{
    public class NotificationService
    {
        private readonly HttpClient httpClient;
        private readonly AlertManager alertManager;
        private readonly string apiEndpoint;
        private readonly int refreshInterval;
        private CancellationTokenSource cancellationTokenSource;
        private bool isRunning;

        public NotificationService(string configPath)
        {
            // Load configuration
            var config = LoadConfiguration(configPath);
            apiEndpoint = config.ATM_API_Endpoint;
            refreshInterval = config.Refresh_Interval;

            // Initialize HTTP client
            httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            
            if (!string.IsNullOrEmpty(config.Authentication?.Username))
            {
                var authToken = Convert.ToBase64String(
                    System.Text.Encoding.ASCII.GetBytes(
                        $"{config.Authentication.Username}:{config.Authentication.Password}"));
                httpClient.DefaultRequestHeaders.Authorization = 
                    new AuthenticationHeaderValue("Basic", authToken);
            }

            alertManager = new AlertManager();
            cancellationTokenSource = new CancellationTokenSource();
        }

        public void StartListening()
        {
            if (isRunning) return;

            isRunning = true;
            cancellationTokenSource = new CancellationTokenSource();

            Task.Run(async () =>
            {
                while (!cancellationTokenSource.Token.IsCancellationRequested)
                {
                    try
                    {
                        await PollATMStatus();
                        await Task.Delay(refreshInterval, cancellationTokenSource.Token);
                    }
                    catch (OperationCanceledException)
                    {
                        break;
                    }
                    catch (Exception ex)
                    {
                        LogError($"Error polling ATM status: {ex.Message}");
                        await Task.Delay(refreshInterval, cancellationTokenSource.Token);
                    }
                }
            }, cancellationTokenSource.Token);
        }

        public void StopListening()
        {
            if (!isRunning) return;

            cancellationTokenSource.Cancel();
            isRunning = false;
        }

        private async Task PollATMStatus()
        {
            try
            {
                var response = await httpClient.GetAsync($"{apiEndpoint}/status");
                response.EnsureSuccessStatusCode();

                var content = await response.Content.ReadAsStringAsync();
                var atmStatuses = JsonSerializer.Deserialize<List<ATMStatus>>(content);

                foreach (var status in atmStatuses)
                {
                    var alert = new ATMAlert
                    {
                        ATM_ID = status.ATM_ID,
                        Status = status.CurrentStatus,
                        ErrorDetails = status.ErrorDetails,
                        Timestamp = DateTime.Now
                    };

                    await alertManager.ProcessAlert(alert);
                }
            }
            catch (Exception ex)
            {
                LogError($"Failed to poll ATM status: {ex.Message}");
                throw;
            }
        }

        public async Task SendResponse(string atmId, string action)
        {
            try
            {
                var response = new
                {
                    ATM_ID = atmId,
                    Action = action,
                    Timestamp = DateTime.Now
                };

                var json = JsonSerializer.Serialize(response);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var apiResponse = await httpClient.PostAsync($"{apiEndpoint}/response", content);
                apiResponse.EnsureSuccessStatusCode();
            }
            catch (Exception ex)
            {
                LogError($"Failed to send response: {ex.Message}");
                throw;
            }
        }

        private Config LoadConfiguration(string path)
        {
            try
            {
                var jsonString = System.IO.File.ReadAllText(path);
                return JsonSerializer.Deserialize<Config>(jsonString);
            }
            catch (Exception ex)
            {
                LogError($"Failed to load configuration: {ex.Message}");
                throw;
            }
        }

        private void LogError(string message)
        {
            // In a production environment, this should write to a proper logging system
            Console.Error.WriteLine($"[{DateTime.Now}] ERROR: {message}");
        }

        public AlertManager GetAlertManager()
        {
            return alertManager;
        }
    }

    public class Config
    {
        public string ATM_API_Endpoint { get; set; }
        public int Refresh_Interval { get; set; }
        public AuthConfig Authentication { get; set; }
    }

    public class AuthConfig
    {
        public string Username { get; set; }
        public string Password { get; set; }
    }

    public class ATMStatus
    {
        public string ATM_ID { get; set; }
        public string CurrentStatus { get; set; }
        public string ErrorDetails { get; set; }
    }
}
