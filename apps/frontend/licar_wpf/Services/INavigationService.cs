using licar_wpf.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public interface INavigationService
    {
        void ShowLoginView();
        void ShowMainView(User use);
        void CloseWindow(object viewModel);
    }
}
