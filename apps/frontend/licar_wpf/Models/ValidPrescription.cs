using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace licar_wpf.Models
{
    public class ValidPrescription
    {
        [JsonPropertyName("prescriptionId")]
        public int PrescriptionId { get; set; }

        [JsonPropertyName("patientId")]
        public int PatientId { get; set; }

        [JsonPropertyName("patientName")]
        public string PatientName { get; set; }

        [JsonPropertyName("date")]
        public string Date { get; set; }
    }
}
