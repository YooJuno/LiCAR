using licar_wpf.Models;
using licar_wpf.ViewModels;
using licar_wpf.Views;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace licar_wpf.Services
{
    public class NavigationService : INavigationService
    {
        public void ShowLoginView()
        {
            var loginView = new LoginView();

            loginView.DataContext = new LoginViewModel(this, new ApiService());
            loginView.Show();
        }

        public void ShowMainView(User user)
        {
            var mainView = new MainView();

            mainView.DataContext = new MainViewModel(user, this, new SseService());
            mainView.Show();
        }

        public void CloseWindow(object viewModel)
        {
            var window = Application.Current.Windows.OfType<Window>().FirstOrDefault(w => w.DataContext == viewModel);
            window?.Close();
        }
    }
}
