using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models
{
    public class Delivery
    {
        [JsonPropertyName("deliveryId")]
        public int DeliveryId { get; set; }

        [JsonPropertyName("requestTime")]
        public string RequestTime { get; set; }

        [JsonPropertyName("sendTime")]
        public string? SendTime { get; set; }

        [JsonPropertyName("successTime")]
        public string? SuccessTime { get; set; }

        [JsonPropertyName("status")]
        public string Status { get; set; } // "requested", "in_transit", "completed"

        [JsonPropertyName("robotId")]
        public int RobotId { get; set; }

        [JsonPropertyName("nurseName")]
        public string NurseName { get; set; }

        [JsonPropertyName("pharmacistName")]
        public string PharmacistName { get; set; }

        [JsonPropertyName("patientId")]
        public int PatientId { get; set; }
    }
}
