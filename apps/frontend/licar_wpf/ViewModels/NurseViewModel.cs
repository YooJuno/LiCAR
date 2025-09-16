using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using licar_wpf.Models;
using licar_wpf.Models.DTOs;
using licar_wpf.Services;
using licar_wpf.ViewModels.Base;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace licar_wpf.ViewModels
{
    public partial class NurseViewModel : ViewModelBase
    {
        private readonly User _currentUser;
        private readonly IApiService _apiService;

        [ObservableProperty]
        private string? _searchText;

        [ObservableProperty]
        private Patient? _selectedPatient;

        public ObservableCollection<Patient> Patients { get; } = new();

        public NurseViewModel(User currentUser, IApiService apiService)
        {
            _currentUser = currentUser;
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

        [RelayCommand(CanExecute = nameof(CanRequestDelivery))]
        private async Task RequestDeliveryAsync()
        {
            if (SelectedPatient == null) return;

            var request = new DeliveryRequest
            {
                PatientId = SelectedPatient.PatientId,
                NurseId = _currentUser.Id,
                PharmacistId = new Random().Next(1, 4),
                RobotId = 1
            };

            try
            {
                var result = await _apiService.RequestDeliveryAsync(request);
                if (result != null)
                {
                    MessageBox.Show(
                        $"{SelectedPatient.Name}의 약 운반이 성공적으로 요청되었습니다.\n ( 요청 번호 : {result.DeliveryId} )",
                        "요청 성공",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
                else
                {
                    MessageBox.Show("약 운반 요청에 실패하였습니다.", "요청 실패", MessageBoxButton.OK, MessageBoxImage.Exclamation);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"오류가 발생하였습니다.\n{ex.Message}", "오류", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private bool CanRequestDelivery()
        {
            return SelectedPatient != null;
        }

        partial void OnSelectedPatientChanged(Patient? value)
        {
            RequestDeliveryCommand.NotifyCanExecuteChanged();
        }
    }
}
