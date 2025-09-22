using licar_wpf.Models;
using licar_wpf.Services;
using licar_wpf.Views;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace licar_wpf.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private readonly NavigationService _navigationService;
        private readonly SseService _sseService;
        private readonly ToastNotificationService _toastService;
        private readonly Func<LoginViewModel> _loginViewModelFactory;

        public ObservableCollection<ToastNotificationViewModel> Notifications => _toastService.Notifications;
        
        private ViewModelBase _currentViewModel;
        public ViewModelBase CurrentViewModel
        {
            get => _currentViewModel;
            set
            {
                _currentViewModel = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(IsUserLoggedIn));
                OnPropertyChanged(nameof(CurrentUserNameAndRole));
            }
        }

        public bool IsUserLoggedIn => CurrentViewModel is not LoginViewModel;

        public string CurrentUserNameAndRole
        {
            get
            {
                if (UserSession.IsLoggedIn)
                {
                    string role = UserSession.CurrentUser.Role == UserRole.Nurse ? "간호사" : "약사";
                    return $"[ {role} ] {UserSession.CurrentUser.Name}";
                }
                return string.Empty;
            }
        }

        public ICommand LogoutCommand { get; }

        public MainViewModel(NavigationService navigationService, SseService sseService, ToastNotificationService toastService, Func<LoginViewModel> loginViewModelFactory) 
        {
            _navigationService = navigationService;
            _sseService = sseService;
            _toastService = toastService;
            _loginViewModelFactory = loginViewModelFactory;

            _navigationService.CurrentViewModelChanged += (viewModel) => CurrentViewModel = viewModel;

            LogoutCommand = new RelayCommand(Logout);

            _navigationService.NavigateTo(_loginViewModelFactory());
        }

        private void Logout(object parameter)
        {
            _sseService.Disconnect();
            
            UserSession.Logout();

            _navigationService.NavigateTo(_loginViewModelFactory());
        }
    }
}
