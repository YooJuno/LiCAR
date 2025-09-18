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

        public ObservableCollection<Delivery> DeliveryList { get; } = new ObservableCollection<Delivery>();
        public ObservableCollection<Prescription> PrescriptionList { get; } = new ObservableCollection<Prescription>();
        public ObservableCollection<Notification> NotificationList { get; } = new ObservableCollection<Notification>();

        private Delivery _selectedDelivery;
        public Delivery SelectedDelivery
        {
            get => _selectedDelivery;
            set
            {
                _selectedDelivery = value;
                OnPropertyChanged();
                LoadPrescriptionsForDelivery(value);
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

            LoadDeliveriesCommand = new RelayCommand(async (p) => await LoadDeliveries());

            _sseService.DeliveryRequested += OnDeliveryRequested;

            LoadDeliveriesCommand.Execute(null);
        }

        private async Task LoadDeliveries()
        {
            DeliveryList.Clear();
            var deliveries = await _pharmacistService.GetDeliveriesAsync();
            foreach (var deliver in deliveries)
            {
                DeliveryList.Add(deliver);
            }
        }

        private async void LoadPrescriptionsForDelivery(Delivery delivery)
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
            _toastService.Show($"[{DateTime.Now}]약 요청이 들어왔습니다!!!");

            Application.Current.Dispatcher.Invoke(() =>
            {
                NotificationList.Add(new Notification($"요청 알림 : {jsonDate}"));
                LoadDeliveriesCommand.Execute(null);
            });
        }
    }
}
