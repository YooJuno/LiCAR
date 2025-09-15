using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using licar_wpf.Models;
using licar_wpf.Services;
using licar_wpf.ViewModels.Base;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.ViewModels
{
    public partial class MainViewModel : ViewModelBase
    {
        private readonly INavigationService _navigationService;
        private readonly ISseService _sseService;

        [ObservableProperty]
        private User _currentUser;

        [ObservableProperty]
        private ViewModelBase _currentView;

        public ObservableCollection<NotificationViewModel> Notifications { get; } = new();

        public MainViewModel(User user, INavigationService navigationService, ISseService sseService)
        {
            _currentUser = user;
            _navigationService = navigationService;
            _sseService = sseService;

            if (user.Role == UserRole.Nurse)
            {
                _currentView = new NurseViewModel(new ApiService());
            }
            else
            {
                _currentView = new PharmacistViewModel(new ApiService());
            }

            _sseService.NotificationReceived += OnNotificationReceived;
            _sseService.ConnectAsync(user.Role, user.Id);
        }

        private void OnNotificationReceived(Notification notification)
        {
            App.Current.Dispatcher.Invoke(() =>
            {
                Notifications.Add(new NotificationViewModel(notification));
            });
        }

        [RelayCommand]
        private void Logout()
        {
            _sseService.Disconnect();
            _navigationService.ShowLoginView();
            _navigationService.CloseWindow(this);
        }
    }
}
