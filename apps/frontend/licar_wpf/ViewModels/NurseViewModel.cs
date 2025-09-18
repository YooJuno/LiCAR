using licar_wpf.Models;
using licar_wpf.Services;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace licar_wpf.ViewModels
{
    public partial class NurseViewModel : ViewModelBase
    {
        private readonly NavigationService _navigationService;
        private readonly NurseService _nurseService;
        private readonly SseService _sseService;

        private string _searchKeyword;
        public string SearchKeyword { get => _searchKeyword; set { _searchKeyword = value; OnPropertyChanged(); } }

        public ObservableCollection<Patient> PatientList { get; } = new ObservableCollection<Patient>();
        public ObservableCollection<Notification> NotificationList { get; } = new ObservableCollection<Notification>();

        private Patient _selectedPatient;
        public Patient SelectedPatient
        {
            get => _selectedPatient;
            set
            {
                _selectedPatient = value;
                OnPropertyChanged();
                LoadPatientDetails(value?.PatientId ?? 0);

                RequestDeliveryCommand.RaiseCanExecuteChanged();
            }
        }

        public string NurseName => UserSession.CurrentUser?.Name;

        public ICommand SearchCommand { get; }
        public RelayCommand RequestDeliveryCommand { get; }

        public NurseViewModel(NavigationService navigationService, NurseService nurseService, SseService sseService)
        {
            _navigationService = navigationService;
            _nurseService = nurseService;
            _sseService = sseService;

            SearchCommand = new RelayCommand(async (p) => await SearchPatients());
            RequestDeliveryCommand = new RelayCommand(async (p) => await RequestDelivery(), (p) => SelectedPatient != null);

            _sseService.DeliveryCompleted += OnDeliveryCompleted;
        }

        private async Task SearchPatients()
        {
            PatientList.Clear();
            var patients = await _nurseService.SearchPatientsAsync(SearchKeyword);
            foreach (var patient in patients)
            {
                PatientList.Add(patient);
            }
        }

        private async void LoadPatientDetails(int patientId)
        {
            if (patientId == 0) return;
            var details = await _nurseService.GetPatientDetailAsync(patientId);

            SelectedPatient.Birthday = details.Birthday;
            SelectedPatient.AdmissionDate = details.AdmissionDate;
            SelectedPatient.DischargeDate = details.DischargeDate;
            SelectedPatient.NurseName = details.NurseName;
            OnPropertyChanged(nameof(SelectedPatient));
        }

        private async Task RequestDelivery()
        {
            try
            {
                var random = new Random();
                //int pharmacistId = random.Next(1, 4);

                var result = await _nurseService.RequestDeliveryAsync(1, UserSession.CurrentUser.Id, 1, SelectedPatient.PatientId);

                Application.Current.Dispatcher.Invoke(() =>
                {
                    MessageBox.Show($"성공적으로 요청되었습니다. \n( 요청번호 : {result.DeliveryId})", "성공", MessageBoxButton.OK, MessageBoxImage.Information);
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"요청에 실패했습니다. \n{ex}", "실패", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        private void OnDeliveryCompleted(string jsonData)
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                // TODO : jsonData 파싱 후 메시지 디자인
                NotificationList.Add(new Notification($"운반 완료 알림 : {jsonData}"));
            });
        }
    }
}
