using licar_wpf.Models.DTOs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace licar_wpf.Models
{
    public enum UserRole
    {
        Nurse,
        Pharmacist
    }
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public UserRole Role { get; set; }
        public string? Department {  get; set; }

        public User(LoginResponse response)
        {
            Name = response.Name;
            Department = response.Department;

            if (response.NurseId.HasValue)
            {
                Id = response.NurseId.Value;
                Role = UserRole.Nurse;
            }
            else if (response.PharmacistId.HasValue)
            {
                Id = response.PharmacistId.Value;
                Role = UserRole.Pharmacist;
            }
        }
    }
}
