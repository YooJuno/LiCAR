using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models
{
    public class Drug
    {
        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("form")]
        public string Form { get; set; }

        [JsonPropertyName("dosage")]
        public int Dosage { get; set; }

        [JsonPropertyName("unit")]
        public string Unit { get; set; }
    }
}
