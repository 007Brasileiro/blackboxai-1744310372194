using System;
using System.Windows;
using System.Threading.Tasks;
using System.IO;

namespace WindowsMonitor
{
    public class Program
    {
        private static NotificationService notificationService;

        [STAThread]
        public static void Main()
        {
            try
            {
                // Initialize services
                InitializeServices();

                // Create and run the application
                var app = new Application();
                var mainWindow = new MainWindow();
                
                // Handle application shutdown
                app.Exit += (s, e) => Shutdown();

                // Start the notification service
                notificationService.StartListening();

                // Run the application
                app.Run(mainWindow);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Critical error starting application: {ex.Message}\n\nApplication will now exit.",
                    "Critical Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
                Environment.Exit(1);
            }
        }

        private static void InitializeServices()
        {
            try
            {
                // Get the configuration file path
                string configPath = Path.Combine(
                    AppDomain.CurrentDomain.BaseDirectory,
                    "config",
                    "settings.json");

                // Ensure config file exists
                if (!File.Exists(configPath))
                {
                    throw new FileNotFoundException(
                        "Configuration file not found. Please ensure settings.json is present in the config directory.");
                }

                // Initialize notification service
                notificationService = new NotificationService(configPath);

                // Additional service initialization can be added here
            }
            catch (Exception ex)
            {
                throw new ApplicationException(
                    "Failed to initialize services. Please check the configuration and try again.", ex);
            }
        }

        private static void Shutdown()
        {
            try
            {
                // Stop the notification service
                notificationService?.StopListening();

                // Additional cleanup can be added here
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error during shutdown: {ex.Message}",
                    "Shutdown Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning);
            }
        }

        public static NotificationService GetNotificationService()
        {
            return notificationService ?? 
                throw new InvalidOperationException("Notification service not initialized");
        }
    }
}
