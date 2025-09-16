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
            return await _apiClient.GetAsync<List<Patient>>($"/patients?name={name}");
        }

        public async Task<Patient> GetPatientDetailAsync(int patientId)
        {
            return await _apiClient.GetAsync<Patient>($"/patients/{patientId}");
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

            return await _apiClient.PostAsync<Delivery>($"/deliveries", requestBody);
        }
    }
}
