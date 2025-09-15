using licar_wpf.Models;
using licar_wpf.Models.DTOs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;

namespace licar_wpf.Services
{
    public class ApiService : IApiService
    {
        private readonly HttpClient _httpClient;
        private const string BaseUrl = "http://localhost:8080/api/v1";

        public ApiService()
        {
            _httpClient = new HttpClient();
        }

        public async Task<LoginResponse?> LoginAsync(AuthRequest authRequest)
        {
            string url;

            if (authRequest.NurseId.HasValue)
            {
                url = $"{BaseUrl}/auth/nurse/login";
            }
            else if (authRequest.PharmacistId.HasValue)
            {
                url = $"{BaseUrl}/auth/pharmacist/login";
            }
            else
            {
                return null;
            }

            var response = await _httpClient.PostAsJsonAsync(url, authRequest);

            if (response.IsSuccessStatusCode)
            {
                return await response.Content.ReadFromJsonAsync<LoginResponse>();
            }

            return null;
        }

        public async Task<List<Patient>?> GetPatientsAsync(string? name = null)
        {
            var url = string.IsNullOrWhiteSpace(name) ? $"{BaseUrl}/patients" : $"{BaseUrl}/patients?name={name}";
            
            return await _httpClient.GetFromJsonAsync<List<Patient>>(url);
        }

        public async Task<Patient?> GetPatientDetailAsync(int patientId)
        {
            var url = $"{BaseUrl}/patients/{patientId}";

            return await _httpClient.GetFromJsonAsync<Patient>(url);
        }

        public async Task<List<Delivery>?> GetDeliveriesAsync()
        {
            var url = $"{BaseUrl}/deliveries";

            return await _httpClient.GetFromJsonAsync<List<Delivery>>(url);
        }

        public async Task<Prescription?> GetPrescriptionDetailAsync(int prescriptionId)
        {
            var url = $"{BaseUrl}/prescriptions/{prescriptionId}";

            return await _httpClient.GetFromJsonAsync<Prescription>(url);
        }

        public async Task<Delivery?> RequestDeliveryAsync(DeliveryRequest deliveryRequest)
        {
            var url = $"{BaseUrl}/deliveries";
            var response = await _httpClient.PostAsJsonAsync(url, deliveryRequest);

            if (response.IsSuccessStatusCode)
            {
                return await response.Content.ReadFromJsonAsync<Delivery>();
            }

            return null;
        }
    }
}
