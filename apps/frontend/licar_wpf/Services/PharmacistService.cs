using licar_wpf.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public class PharmacistService
    {
        private readonly ApiClient _apiClient;

        public PharmacistService(ApiClient apiClient)
        {
            _apiClient = apiClient;
        }

        public async Task<List<Delivery>> GetDeliveriesAsync()
        {
            return await _apiClient.GetAsync<List<Delivery>>("/deliveries");
        }

        public async Task<Delivery> GetDeliveryDetailASync(int deliveryId)
        {
            return await _apiClient.GetAsync<Delivery>($"/deliveries/{deliveryId}");
        }

        public async Task<List<Prescription>> GetValidPrescriptionAsync(int patientId, DateTime date)
        {
            string formattedDate = date.ToString("yyyy-mm-dd");

            return await _apiClient.GetAsync<List<Prescription>>($"/prescriptions/valid?patient_id={patientId}&date={formattedDate}");
        }

        public async Task<Prescription> GetPrescriptionDetailAsync(int prescriptionId)
        {
            return await _apiClient.GetAsync<Prescription>($"/prescription/{prescriptionId}");
        }
    }
}
