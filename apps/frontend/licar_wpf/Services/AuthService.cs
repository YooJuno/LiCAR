using licar_wpf.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public class AuthService
    {
        private readonly ApiClient _apiClient;

        public AuthService(ApiClient apiClient)
        {
            _apiClient = apiClient;
        }

        public async Task<Nurse> LoginNurseAsync(int nurseId, string name)
        {
            var requestBody = new { nurseId, name };

            return await _apiClient.PostAsync<Nurse>("/auth/nurse/login", requestBody);
        }

        public async Task<Pharmacist> LoginPharmacistAsync(int pharmacistId, string name)
        {
            var requestBody = new { pharmacistId, name };

            return await _apiClient.PostAsync<Pharmacist>("/auth/pharmacist/login", requestBody);
        }
    }
}
