using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECFramework.ECService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace DemoService.Controllers
{
    /// <summary>
    /// PostgreSQL user management APIs.
    /// </summary>
    [ApiController]
    [Route("/api/PgUsers")]
    [UrlFilter]
    public class PgUsersController : ControllerBase
    {
        private readonly IPgUserService _pgUserService;

        public PgUsersController(IPgUserService pgUserService)
        {
            _pgUserService = pgUserService;
        }

        /// <summary>
        /// List PostgreSQL users.
        /// </summary>
        /// <returns>User list.</returns>
        [HttpGet("listPgUsers")]
        [ProducesResponseType(typeof(List<PgUser>), StatusCodes.Status200OK)]
        public async Task<List<PgUser>> ListPgUsers()
        {
            return await _pgUserService.ListPgUsersAsync();
        }

        /// <summary>
        /// Get PostgreSQL user by id.
        /// </summary>
        /// <param name="id">User id.</param>
        /// <returns>User data.</returns>
        [HttpGet("getPgUser/{id:int}")]
        [ProducesResponseType(typeof(PgUser), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<PgUser> GetPgUser(int id)
        {
            return await _pgUserService.GetPgUserAsync(id);
        }

        /// <summary>
        /// Create PostgreSQL user.
        /// </summary>
        /// <param name="request">Create request body.</param>
        /// <returns>Created user.</returns>
        [HttpPost("createPgUser")]
        [ProducesResponseType(typeof(PgUser), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<PgUser> CreatePgUser([FromBody] CreatePgUserRequest request)
        {
            return await _pgUserService.CreatePgUserAsync(request);
        }

        /// <summary>
        /// Update PostgreSQL user.
        /// </summary>
        /// <param name="id">User id.</param>
        /// <param name="request">Update request body.</param>
        /// <returns>Updated user.</returns>
        [HttpPut("updatePgUser/{id:int}")]
        [ProducesResponseType(typeof(PgUser), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<PgUser> UpdatePgUser(int id, [FromBody] UpdatePgUserRequest request)
        {
            return await _pgUserService.UpdatePgUserAsync(id, request);
        }

        /// <summary>
        /// Delete PostgreSQL user.
        /// </summary>
        /// <param name="id">User id.</param>
        [HttpDelete("deletePgUser/{id:int}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task DeletePgUser(int id)
        {
            await _pgUserService.DeletePgUserAsync(id);
        }
    }
}
