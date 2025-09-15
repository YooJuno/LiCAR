using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models
{
    public class Notification
    {
        public string EventType { get; set; }

        [JsonPropertyName("deliveryId")]
        public int DeliveryId { get; set; }

        [JsonPropertyName("requestTime")]
        public DateTime? RequestTime { get; set; }

        [JsonPropertyName("successTime")]
        public DateTime? SuccessTime { get; set; }

        [JsonPropertyName("nurseId")]
        public int? NurseId { get; set; }

        [JsonPropertyName("pahrmacistId")]
        public int? PharmacistId { get; set; }
    }
}
