using System;

namespace DemoService.Model
{
    public class PgUser
    {
        public int Id { get; set; }
        public string Username { get; set; }
        public string Email { get; set; }
        public bool? IsActive { get; set; }
        public DateTime? CreatedAt { get; set; }
    }

    public class CreatePgUserRequest
    {
        public string Username { get; set; }
        public string Email { get; set; }
        public bool? IsActive { get; set; }
    }

    public class UpdatePgUserRequest
    {
        public string Username { get; set; }
        public string Email { get; set; }
        public bool? IsActive { get; set; }
    }
}
