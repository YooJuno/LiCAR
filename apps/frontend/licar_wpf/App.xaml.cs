using licar_wpf.Services;
using licar_wpf.ViewModels;
using System.Configuration;
using System.Data;
using System.Windows;

namespace licar_wpf
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            var apiClient = new ApiClient("http://localhost:8080");
            var navigationService = new NavigationService();
            var sseService = new SseService();

            var authService = new AuthService(apiClient);
            var nurseService = new NurseService(apiClient);
            var pharmacistService = new PharmacistService(apiClient);


            var loginViewModel = new LoginViewModel(authService, navigationService, sseService,
                () => new NurseViewModel(navigationService, nurseService, sseService),
                () => new PharmacistViewModel(navigationService, pharmacistService, sseService)
                );

            var mainViewModel = new MainViewModel(navigationService, loginViewModel, sseService);

            var mainWindow = new MainWindow
            {
                DataContext = mainViewModel
            };

            mainWindow.Show();
        }
    }

}
