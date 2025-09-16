using CommunityToolkit.Mvvm.ComponentModel;
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
    public partial class PharmacistViewModel : ViewModelBase
    {
        private readonly IApiService _apiService;
        private readonly User _currentUser;

        [ObservableProperty]
        private Delivery? _selectedDelivery;

        [ObservableProperty]
        private Prescription? _selectedPrescriptionDetail;

        [ObservableProperty]
        private string _statusMessage;

        public ObservableCollection<Delivery> Deliveries { get; } = new();

        public PharmacistViewModel(User user, IApiService apiService)
        {
            _currentUser = user;
            _apiService = apiService;
            LoadDeliveriesAsync();
            _statusMessage = "운반 요청을 선택하여 처방전을 확인하세요.";
        }

        private async void LoadDeliveriesAsync()
        {
            var result = await _apiService.GetDeliveriesAsync();
            Deliveries.Clear();

            if (result != null)
            {
                foreach (var delivery in result)
                {
                    if (delivery.PharmacistName == _currentUser.Name)
                    {
                        Deliveries.Add(delivery);
                    }
                }
            }
        }

        async partial void OnSelectedDeliveryChanged(Delivery? value)
        {
            SelectedPrescriptionDetail = null;

            if (value == null)
            {
                StatusMessage = "운반 요청을 선택하여 처방전을 확인하세요.";
                return;
            }

            try
            {
                StatusMessage = $"{value.PatientName} 님의 처방전을 조회 중입니다...";
                var validPrescriptions = await _apiService.GetValidPrescriptionsAsync(value.PatientId, DateTime.Now);

                if (validPrescriptions == null || !validPrescriptions.Any())
                {
                    StatusMessage = "해당 환자의 처방전이 존재하지 않습니다.";
                    return;
                }

                var firstValidPrescription = validPrescriptions.FirstOrDefault();
                if (firstValidPrescription == null) return;

                var prescriptionId = firstValidPrescription.PrescriptionId;
                StatusMessage = $"처방전( ID : {prescriptionId})의 상세 정보를 불러오는 중입니다...";

                SelectedPrescriptionDetail = await _apiService.GetPrescriptionDetailAsync(prescriptionId);

                if (SelectedPrescriptionDetail != null)
                {
                    StatusMessage = "처방전 상세 정보 불러오기 완료.";
                }
                else
                {
                    StatusMessage = "처방전 상세 정보 불러오는데 실패했습니다.";
                }
            }
            catch (Exception ex)
            {
                StatusMessage = "오류가 발생했습니다. : " + ex.Message;
            }
        }
    }
}
