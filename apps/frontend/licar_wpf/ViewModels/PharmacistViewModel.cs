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
                LoadPrescriptionDetails(value);
            }
        }

        public string PharmacistName => UserSession.CurrentUser?.Name;

        public ICommand LoadDeliveriesCommand { get; }

        public PharmacistViewModel(NavigationService navigationService, PharmacistService pharmacistService, SseService sseService)
        {
            _navigationService = navigationService;
            _pharmacistService = pharmacistService;
            _sseService = sseService;

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
            if (delivery == null) return;

            var prescriptions = await _pharmacistService.GetValidPrescriptionAsync(delivery.PatientId, DateTime.Now);
            foreach (var prescription in prescriptions)
            {
                PrescriptionList.Add(prescription);
            }
        }

        private async void LoadPrescriptionDetails(Prescription prescription)
        {
            if (prescription == null) return;

            if (prescription.Drugs != null && prescription.Drugs.Count > 0) return;

            var details = await _pharmacistService.GetPrescriptionDetailAsync(prescription.PrescriptionId);

            prescription.Drugs = details.Drugs;
            prescription.CounsellingNote = details.CounsellingNote;

            OnPropertyChanged(nameof(SelectedPrescription));
        }

        private void OnDeliveryRequested(string jsonDate)
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                NotificationList.Add(new Notification($"요청 알림 : {jsonDate}"));
                LoadDeliveriesCommand.Execute(null);
            });
        }
    }
}
