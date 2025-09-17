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
        private readonly SseService _sseService;
        
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

        public MainViewModel(NavigationService navigationService, LoginViewModel loginViewModel, SseService sseService)
        {
            _navigationService = navigationService;
            _sseService = sseService;
            _navigationService.CurrentViewModelChanged += (viewModel) => CurrentViewModel = viewModel;

            LogoutCommand = new RelayCommand(Logout);

            _navigationService.NavigateTo(loginViewModel);
        }

        private void Logout(object parameter)
        {
            _sseService.Disconnect();
            
            UserSession.Logout();

            _navigationService.NavigateTo(new LoginViewModel(
                new AuthService(new ApiClient()),
                _navigationService,
                _sseService,
                () => new NurseViewModel(_navigationService, new NurseService(new ApiClient()), _sseService),
                () => new PharmacistViewModel(_navigationService, new PharmacistService(new ApiClient()), _sseService)
                ));
        }
    }
}
