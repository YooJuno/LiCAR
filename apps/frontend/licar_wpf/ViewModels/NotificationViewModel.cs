using CommunityToolkit.Mvvm.ComponentModel;
using licar_wpf.Models;
using licar_wpf.ViewModels.Base;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.ViewModels
{
    public partial class NotificationViewModel : ViewModelBase
    {
        [ObservableProperty]
        private string _message;

        [ObservableProperty]
        private DateTime _receivedTime;

        public NotificationViewModel(Notification notification)
        {
            _receivedTime = DateTime.Now;
            _message = FormatMessage(notification);
        }

        private string FormatMessage(Notification notification)
        {
            if (notification.RequestTime.HasValue)
            {
                return $"[{_receivedTime:HH:mm}] 운반 요청 (ID: {notification.DeliveryId})";
            }
            else if (notification.SuccessTime.HasValue)
            {
                return $"[{_receivedTime:HH:mm}] 운반 완료 (ID: {notification.DeliveryId})";
            }

            return $"[{_receivedTime:HH:mm}] 새 알림 (ID: {notification.DeliveryId})";
        }
    }
}
