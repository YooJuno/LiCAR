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
        public DateTime RequestTime { get; set; }

        [JsonPropertyName("sendTime")]
        public DateTime? SendTime { get; set; }

        [JsonPropertyName("successTime")]
        public DateTime? SuccessTime { get; set; }

        [JsonPropertyName("status")]
        public string Status { get; set; } // "requested", "in_transit", "completed"

        [JsonPropertyName("robotId")]
        public int RobotId { get; set; }

        [JsonPropertyName("nurseName")]
        public string NurseName { get; set; }

        [JsonPropertyName("pharmacistName")]
        public string PharmacistName { get; set; }

        [JsonPropertyName("patientName")]
        public string? PatientName { get; set; }

        [JsonPropertyName("patientId")]
        public int PatientId { get; set; }
    }
}
