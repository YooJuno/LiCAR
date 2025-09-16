using licar_wpf.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public interface ISseService
    {
        event Action<Notification> NotificationReceived;

        Task ConnectAsync(UserRole role, int userId);

        void Disconnect();
    }
}
