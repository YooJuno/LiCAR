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
        private readonly ToastNotificationService _toastService;

        private string _searchKeyword;
        public string SearchKeyword { get => _searchKeyword; set { _searchKeyword = value; OnPropertyChanged(); } }

        public ObservableCollection<Patient> PatientList { get; } = new ObservableCollection<Patient>();
        public ObservableCollection<Notification> NotificationList { get; } = new ObservableCollection<Notification>();
        public ObservableCollection<Prescription> ValidPrescriptionList { get; } = new ObservableCollection<Prescription>();

        private Patient _selectedPatient;
        public Patient SelectedPatient
        {
            get => _selectedPatient;
            set
            {
                _selectedPatient = value;
                OnPropertyChanged();
                LoadPatientDetails(value);
                LoadValidPrescriptionsAsync(value);

                (RequestDeliveryCommand as RelayCommand)?.RaiseCanExecuteChanged();
            }
        }

        private Patient _patientDetails;
        public Patient PatientDetails
        {
            get => _patientDetails;
            private set
            {
                _patientDetails = value;
                OnPropertyChanged();
            }
        }

        private Prescription _selectedPrescription;
        public Prescription SelectedPrescription
        {
            get => _selectedPrescription;
            set
            {
                _selectedPrescription = value;
                OnPropertyChanged();

                LoadPrescriptionDetailsAsync(value);
            }
        }

        private Prescription _prescriptionDetails;
        public Prescription PrescriptionDetails
        {
            get => _prescriptionDetails;
            set
            {
                _prescriptionDetails = value;
                OnPropertyChanged();
            }
        }

        public string NurseName => UserSession.CurrentUser?.Name;

        public ICommand SearchCommand { get; }
        public RelayCommand RequestDeliveryCommand { get; }

        public NurseViewModel(NavigationService navigationService, NurseService nurseService, SseService sseService, ToastNotificationService toastService)
        {
            _navigationService = navigationService;
            _nurseService = nurseService;
            _sseService = sseService;
            _toastService = toastService;

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

        private async void LoadPatientDetails(Patient patient)
        {
            if (patient == null)
            {
                PatientDetails = null;
                return;
            }
            var details = await _nurseService.GetPatientDetailAsync(patient.PatientId);

            PatientDetails = details;
        }

        private async void LoadValidPrescriptionsAsync(Patient patient)
        {
            ValidPrescriptionList.Clear();
            PrescriptionDetails = null;

            if (patient == null) return;

            var prescriptions = await _nurseService.GetValidPrescriptionsAsync(patient.PatientId, DateTime.Now);
            foreach (var prescription in prescriptions)
            {
                ValidPrescriptionList.Add(prescription);
            }
        }

        private async void LoadPrescriptionDetailsAsync(Prescription prescription)
        {
            if (prescription == null)
            {
                PrescriptionDetails = null;
                return;
            }

            try
            {
                var prescription_details = await _nurseService.GetPrescriptionDetailsAsync(prescription.PrescriptionId);
                PrescriptionDetails = prescription_details;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"처방전 상세 정보를 불러오는 데 실패했습니다.\n{ex.Message}");
                PrescriptionDetails = null;
            }
        }

        private async Task RequestDelivery()
        {
            try
            {
                var random = new Random();
                //int pharmacistId = random.Next(1, 4);

                var result = await _nurseService.RequestTransportAsync(1, UserSession.CurrentUser.Id, 1, SelectedPatient.PatientId);

                Application.Current.Dispatcher.Invoke(() =>
                {
                    MessageBox.Show($"성공적으로 요청되었습니다. \n( 요청번호 : {result.TransportId})", "성공", MessageBoxButton.OK, MessageBoxImage.Information);
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"요청에 실패했습니다. \n{ex}", "실패", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        private void OnDeliveryCompleted(string jsonData)
        {
            // TODO : jsonData 파싱 후 메시지 디자인
            _toastService.Show("약 운반 완료!!!!!!!!!!!!!");

            Application.Current.Dispatcher.Invoke(() =>
            {
                NotificationList.Add(new Notification($"운반 완료 알림 : {jsonData}"));
            });
        }
    }
}
