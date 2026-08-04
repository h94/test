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
    /// GM team management APIs.
    /// </summary>
    [ApiController]
    [Route("/api/Gm")]
    [UrlFilter]
    public class GmController : ControllerBase
    {
        private readonly IGmTeamService _gmTeamService;

        public GmController(IGmTeamService gmTeamService)
        {
            _gmTeamService = gmTeamService;
        }

        /// <summary>
        /// List GM teams.
        /// </summary>
        /// <returns>GM team list.</returns>
        [HttpGet("listGmTeams")]
        [ProducesResponseType(typeof(List<GmTeam>), StatusCodes.Status200OK)]
        public async Task<List<GmTeam>> ListGmTeams()
        {
            return await _gmTeamService.ListGmTeamsAsync();
        }

        /// <summary>
        /// Get a GM team by team name.
        /// </summary>
        /// <param name="teamName">Target team name.</param>
        /// <returns>GM team.</returns>
        [HttpGet("getGmTeam/{teamName}")]
        [ProducesResponseType(typeof(GmTeam), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<GmTeam> GetGmTeam(string teamName)
        {
            return await _gmTeamService.GetGmTeamAsync(teamName);
        }

        /// <summary>
        /// Create a GM team.
        /// </summary>
        /// <param name="request">Create request body.</param>
        /// <returns>Created GM team.</returns>
        [HttpPost("createGmTeam")]
        [ProducesResponseType(typeof(GmTeam), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<GmTeam> CreateGmTeam([FromBody] CreateGmTeamRequest request)
        {
            return await _gmTeamService.CreateGmTeamAsync(request);
        }

        /// <summary>
        /// Update a GM team.
        /// </summary>
        /// <param name="teamName">Target team name.</param>
        /// <param name="request">Update request body.</param>
        /// <returns>Updated GM team.</returns>
        [HttpPut("updateGmTeam/{teamName}")]
        [ProducesResponseType(typeof(GmTeam), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<GmTeam> UpdateGmTeam(string teamName, [FromBody] UpdateGmTeamRequest request)
        {
            return await _gmTeamService.UpdateGmTeamAsync(teamName, request);
        }

        /// <summary>
        /// Delete a GM team.
        /// </summary>
        /// <param name="teamName">Target team name.</param>
        [HttpDelete("deleteGmTeam/{teamName}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task DeleteGmTeam(string teamName)
        {
            await _gmTeamService.DeleteGmTeamAsync(teamName);
        }
    }
}
