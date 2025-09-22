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
    public class PharmacistViewModel : ViewModelBase
    {
        private readonly NavigationService _navigationService;
        private readonly PharmacistService _pharmacistService;
        private readonly SseService _sseService;
        private readonly ToastNotificationService _toastService;

        public ObservableCollection<Transport> TransportList { get; } = new ObservableCollection<Transport>();
        public ObservableCollection<Prescription> PrescriptionList { get; } = new ObservableCollection<Prescription>();
        public ObservableCollection<Notification> NotificationList { get; } = new ObservableCollection<Notification>();

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
                LoadPrescriptionDetail(value);
            }
        }

        private Prescription _prescriptionDetail;
        public Prescription PrescriptionDetail
        {
            get => _prescriptionDetail;
            set
            {
                _prescriptionDetail = value;
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

            _sseService.DeliveryRequested += OnDeliveryRequested;

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
                PrescriptionDetail = null;
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
            PrescriptionDetail = null;
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

            PrescriptionDetail = detail;
        }

        private void OnDeliveryRequested(string jsonDate)
        {
            // TODO : jsonDate 파싱을 하면 좋을 텐데요
            _toastService.Show("약 요청이 들어왔습니다!!!!!");

            Application.Current.Dispatcher.Invoke(() =>
            {
                NotificationList.Add(new Notification($"요청 알림 : {jsonDate}"));
                LoadDeliveriesCommand.Execute(null);
            });
        }
    }
}
