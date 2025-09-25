using licar_wpf.Models;
using licar_wpf.Services;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace licar_wpf.ViewModels
{
    public class PharmacistViewModel : ViewModelBase
    {
        private readonly NavigationService _navigationService;
        private readonly PharmacistService _pharmacistService;
        private readonly SseService _sseService;
        private readonly ToastNotificationService _toastService;

        public ObservableCollection<Transport> TransportList { get; } = new ObservableCollection<Transport>();
        public ObservableCollection<Prescription> PrescriptionList { get; } = new ObservableCollection<Prescription>();
        public ObservableCollection<Notification> NotificationList { get; } = new ObservableCollection<Notification>();
        public ObservableCollection<DrugViewModel> DrugList { get; } = new ObservableCollection<DrugViewModel>();

        private Transport _selectedTransport;
        public Transport SelectedTransport
        {
            get => _selectedTransport;
            set
            {
                _selectedTransport = value;
                OnPropertyChanged();
                //LoadPrescriptionsForTransport(value);
                LoadTransportDetails(value);
            }
        }

        private Transport _transportDetails;
        public Transport TransportDetails
        {
            get => _transportDetails;
            set
            {
                _transportDetails = value;
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
                //LoadPrescriptionDetail(value);
                LoadPrescriptionDetailsForTransport(SelectedTransport, value);
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

        public string PharmacistName => UserSession.CurrentUser?.Name;

        public ICommand LoadDeliveriesCommand { get; }

        public PharmacistViewModel(NavigationService navigationService, PharmacistService pharmacistService, SseService sseService, ToastNotificationService toastService)
        {
            _navigationService = navigationService;
            _pharmacistService = pharmacistService;
            _sseService = sseService;
            _toastService = toastService;

            LoadDeliveriesCommand = new RelayCommand(async (p) => await LoadTransports());

            _sseService.TransportRequested += OnTransportRequested;
            _sseService.DrugRecognized += OnDrugRecognized;

            LoadDeliveriesCommand.Execute(null);
        }

        private async Task LoadTransports()
        {
            TransportList.Clear();
            var transports = await _pharmacistService.GetTransportsAsync();
            foreach (var transport in transports)
            {
                TransportList.Add(transport);
            }
        }

        private async void LoadTransportDetails(Transport transport)
        {
            if (transport == null)
            {
                TransportDetails = null;
                PrescriptionList.Clear();
                PrescriptionDetails = null;
                return;
            }

            try
            {
                var details = await _pharmacistService.GetTransportDetailAsync(transport.TransportId);
                TransportDetails = details;

                PrescriptionList.Clear();
                if (details.Prescriptions != null)
                {
                    foreach (var prescription in details.Prescriptions)
                    {
                        PrescriptionList.Add(prescription);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        private async void LoadPrescriptionsForTransport(Transport delivery)
        {
            PrescriptionList.Clear();
            PrescriptionDetails = null;
            if (delivery == null) return;

            var prescriptions = await _pharmacistService.GetValidPrescriptionAsync(delivery.PatientId, DateTime.Now);
            foreach (var prescription in prescriptions)
            {
                PrescriptionList.Add(prescription);
            }
        }

        private async void LoadPrescriptionDetail(Prescription prescription)
        {
            if (prescription == null) return;

            if (prescription.Drugs != null && prescription.Drugs.Count > 0) return;

            var detail = await _pharmacistService.GetPrescriptionDetailAsync(prescription.PrescriptionId);

            PrescriptionDetails = detail;
        }

        private async void LoadPrescriptionDetailsForTransport(Transport transport, Prescription prescription)
        {
            DrugList.Clear();
            if (transport == null || prescription == null)
            {
                PrescriptionDetails = null;
                return;
            }

            try
            {
                var details = await _pharmacistService.GetPrescriptionDetailForTransportAsync(transport.TransportId, prescription.PrescriptionId);

                PrescriptionDetails = details;

                if (details?.Drugs != null)
                {
                    foreach (var drugModel in details.Drugs)
                    {
                        DrugList.Add(new DrugViewModel(drugModel));
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"처방전 상세 정보를 불러오는 데 실패했습니다. \n{ex.Message}");
                PrescriptionDetails = null;
            }
        }

        private void OnTransportRequested(string jsonData)
        {
            // TODO : jsonDate 파싱을 하면 좋을 텐데요
            _toastService.Show("약 요청이 들어왔습니다!!!!!");

            Application.Current.Dispatcher.Invoke(() =>
            {
                NotificationList.Add(new Notification($"요청 알림 : {jsonData}"));
                LoadDeliveriesCommand.Execute(null);
            });
        }

        private void OnDrugRecognized(string jsonData)
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    if (!DrugList.Any()) return;

                    var recognizedDrugUpdate = JsonSerializer.Deserialize<Drug>(jsonData, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                    if (recognizedDrugUpdate == null) return;


                    var drugToUpdate = DrugList.FirstOrDefault(d => d.DrugId == recognizedDrugUpdate.DrugId);

                    if (drugToUpdate != null)
                    {
                        drugToUpdate.Recognized = recognizedDrugUpdate.Recognized;                    
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"[SSE Drug Recognition ERROR] {ex.Message}");
                }
            });
        }
    }
}
