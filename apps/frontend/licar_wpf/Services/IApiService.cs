using licar_wpf.Models;
using licar_wpf.Models.DTOs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public interface IApiService
    {
        Task<LoginResponse?> LoginAsync(AuthRequest authRequest);

        Task<List<Patient>?> GetPatientsAsync(string? name = null);

        Task<Patient?> GetPatientDetailAsync(int patientId);

        Task<List<Delivery>?> GetDeliveriesAsync();

        Task<Prescription?> GetPrescriptionDetailAsync(int prescriptionId);

        Task<Delivery?> RequestDeliveryAsync(DeliveryRequest deliveryRequest);
    }
}
