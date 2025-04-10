using System.Windows;

namespace WindowsMonitor
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            // Load ATM data and initialize monitoring
            LoadATMData();
        }

        private void LoadATMData()
        {
            // Logic to load ATM data and populate the ATMListView
        }
    }
}
