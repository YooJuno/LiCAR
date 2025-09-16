using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models.DTOs
{
    public class DeliveryRequest
    {
        [JsonPropertyName("robotId")]
        public int RobotId { get; set; }

        [JsonPropertyName("nurseId")]
        public int NurseId { get; set; }

        [JsonPropertyName("pharmacistId")]
        public int PharmacistId { get; set; }

        [JsonPropertyName("patientId")]
        public int PatientId { get; set; }
    }
}
