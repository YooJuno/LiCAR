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
    public partial class NurseViewModel : ViewModelBase
    {
        private readonly IApiService _apiService;

        [ObservableProperty]
        private string? _searchText;

        [ObservableProperty]
        private Patient? _selectedPatient;

        public ObservableCollection<Patient> Patients { get; } = new();

        public NurseViewModel(IApiService apiService)
        {
            _apiService = apiService;
            LoadInitialPatientAsync();
        }

        private async void LoadInitialPatientAsync()
        {
            await SearchPatientAsync();
        }

        [RelayCommand]
        private async Task SearchPatientAsync()
        {
            var result = await _apiService.GetPatientsAsync(SearchText);

            Patients.Clear();

            if (result != null)
            {
                foreach (var patient in result)
                {
                    Patients.Add(patient);
                }
            }
        }


    }
}
