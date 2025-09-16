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
    public class RelayCommand : ICommand
    {
        private readonly Action<object> _execute;
        private readonly Predicate<object> _canExecute;
        public event EventHandler CanExecuteChanged;
        public RelayCommand(Action<object> execute, Predicate<object> canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }
        public bool CanExecute(object parameter) => _canExecute == null || _canExecute(parameter);
        public void Execute(object parameter) => _execute(parameter);
        public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
    }
    public class LoginViewModel : ViewModelBase
    {
        private readonly AuthService _authService;
        private readonly NavigationService _navigationService;
        private readonly SseService _sseService;

        private int _userId;
        public int UserId { get => _userId; set { _userId = value; OnPropertyChanged(); } }

        private string _userName;
        public string UserName { get => _userName; set { _userName = value; OnPropertyChanged(); } }

        private string _errorMessage;
        public string ErroeMessage { get => _errorMessage; set { _errorMessage = value; OnPropertyChanged(); } }

        public bool IsNurseRole { get; set; } = true;

        public ICommand LoginCommand { get; }

        public LoginViewModel(AuthService authService, NavigationService navigationService, SseService sseService)
        {
            _authService = authService;
            _navigationService = navigationService;
            _sseService = sseService;
            LoginCommand = new RelayCommand(async (p) => await ExecuteLogin(), (p) => !string.IsNullOrEmpty(UserName));
        }

        private async Task ExecuteLogin()
        {
            ErroeMessage = string.Empty;

            try
            {
                if (IsNurseRole)
                {
                    var nurse = await _authService.LoginNurseAsync(UserId, UserName);
                    UserSession.Login(new CurrentUser { Id = nurse.NurseId, Name = nurse.Name, Role = UserRole.Nurse, Department = nurse.Department });

                    _ = _sseService.ConnectAsync(UserRole.Nurse, nurse.NurseId);

                    _navigationService.NavigateTo(new NurseViewModel(_navigationService, new NurseService(new ApiClient()), _sseService));
                }
                else
                {
                    var pharmacist = await _authService.LoginPharmacistAsync(UserId, UserName);
                    UserSession.Login(new CurrentUser { Id = pharmacist.PharmacistId, Name = pharmacist.Name, Role = UserRole.Pharmacist });

                    _ = _sseService.ConnectAsync(UserRole.Pharmacist, pharmacist.PharmacistId);

                    _navigationService.NavigateTo(new PharmacistViewModel(_navigationService, new PharmacistService(new ApiClient()), _sseService));
                }
            }
            catch (Exception ex)
            {
                ErroeMessage = "인증에 실패하였습니다. 사번과 이름을 확인해주세요.";
            }
        }
    }
}
