using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models.DTOs
{
    public class AuthRequest
    {
        [JsonPropertyName("nurse_id")]
        public int? NurseId { get; set; }

        [JsonPropertyName("pharmacist_id")]
        public int? PharmacistId { get; set; }

        [JsonPropertyName("name")]
        public required string Name { get; set; }
    }
}
