using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models.DTOs
{
    public class LoginResponse
    {
        [JsonPropertyName("nurseId")]
        public int? NurseId { get; set; }

        [JsonPropertyName("pharmacistId")]
        public int? PharmacistId { get; set; }

        [JsonPropertyName("name")]
        public required string Name { get; set; }

        [JsonPropertyName("department")]
        public string? Department { get; set; }
    }
}
