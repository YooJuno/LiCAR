using licar_wpf.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public class NurseService
    {
        private readonly ApiClient _apiClient;

        public NurseService(ApiClient client)
        {
            _apiClient = client;
        }

        public async Task<List<Patient>> SearchPatientsAsync(string name)
        {
            return await _apiClient.GetAsync<List<Patient>>($"/api/v1/patients?name={name}");
        }

        public async Task<Patient> GetPatientDetailAsync(int patientId)
        {
            return await _apiClient.GetAsync<Patient>($"/api/v1/patients/{patientId}");
        }

        public async Task<Delivery> RequestDeliveryAsync(int robotId, int nurseId, int pharmacistId, int patientId)
        {
            var requestBody = new
            {
                robotId,
                nurseId,
                pharmacistId,
                patientId
            };

            return await _apiClient.PostAsync<Delivery>($"/api/v1/deliveries", requestBody);
        }

        public async Task<List<Prescription>> GetValidPrescriptionsAsync(int patientId, DateTime date)
        {
            string formattedDate = date.ToString("yyyy-MM-dd");

            return await _apiClient.GetAsync<List<Prescription>>($"/api/v1/prescriptions/valid?patient_id={patientId}&date={formattedDate}");
        }

        public async Task<List<Drug>> GetValidDrugsAsync(int patientId, DateTime date)
        {
            string formattedDate = date.ToString("yyyy-MM-dd");

            return await _apiClient.GetAsync<List<Drug>>($"/api/v1/prescriptions/valid-drugs?patient_id={patientId}&date={formattedDate}");
        }
    }
}
