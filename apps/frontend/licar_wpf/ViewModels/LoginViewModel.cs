using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using licar_wpf.Models;
using licar_wpf.Models.DTOs;
using licar_wpf.Services;
using licar_wpf.ViewModels.Base;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.ViewModels
{
    public partial class LoginViewModel : ViewModelBase
    {
        private readonly INavigationService _navigationService;
        private readonly IApiService _apiService;

        [ObservableProperty]
        private UserRole _selectedRole = UserRole.Nurse;

        [ObservableProperty]
        private string? _userId;

        [ObservableProperty]
        private string? _userName;

        [ObservableProperty]
        private string? _errorMessage;

        public LoginViewModel(INavigationService navigationService, IApiService apiService)
        {
            _navigationService = navigationService;
            _apiService = apiService;
        }

        [RelayCommand]
        private async Task LoginAsync()
        {
            ErrorMessage = null;
            if (!int.TryParse(UserId, out int id) || string.IsNullOrWhiteSpace(UserName))
            {
                ErrorMessage = "사번과 이름을 올바르게 입력해주세요.";
                return;
            }

            var request = new AuthRequest { Name = UserName };
            if (SelectedRole == UserRole.Nurse)
            {
                request.NurseId = id;
            }
            else
            {
                request.PharmacistId = id;
            }

            var response = await _apiService.LoginAsync(request);

            if (response != null)
            {
                var user = new User(response);
                _navigationService.ShowMainView(user);
                _navigationService.CloseWindow(this);
            }
            else
            {
                ErrorMessage = "인증에 실패하였습니다. 사번과 이름을 확인해주세요.";
            }
        }
    }
}
