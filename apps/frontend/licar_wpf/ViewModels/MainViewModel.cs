using licar_wpf.Models;
using licar_wpf.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace licar_wpf.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private readonly NavigationService _navigationService;
        
        private ViewModelBase _currentViewModel;
        public ViewModelBase CurrentViewModel
        {
            get => _currentViewModel;
            set
            {
                _currentViewModel = value;
                OnPropertyChanged();
            }
        }

        public ICommand LogoutCommand { get; }

        public MainViewModel(NavigationService navigationService, LoginViewModel loginViewModel)
        {
            _navigationService = navigationService;
            _navigationService.CurrentViewModelChanged += (viewModel) => CurrentViewModel = viewModel;

            LogoutCommand = new RelayCommand(Logout);

            _navigationService.NavigateTo(loginViewModel);
        }

        private void Logout(object parameter)
        {
            Models.UserSession.Logout();

            _navigationService.NavigateTo(new LoginViewModel(
                new AuthService(new ApiClient()),
                _navigationService,
                new SseService()
                ));
        }
    }
}
