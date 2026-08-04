using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;
using MySql.Data.MySqlClient;

namespace DemoService.Infrastructure.DataAccess
{
    [DependencyInjection(typeof(IGmTeamProvider))]
    public class GmTeamProvider : IGmTeamProvider
    {
        private const string ConnectId = "GM";

        private const string SelectColumns =
            "TeamName, Description, AuthToken, Enabled, WhiteList, LastUpdTime";

        private readonly IMySQLManager _mySQLManager;

        public GmTeamProvider(IMySQLManager mySQLManager)
        {
            _mySQLManager = mySQLManager;
        }

        public async Task<List<GmTeam>> ListAsync()
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = $"SELECT {SelectColumns} FROM teams ORDER BY TeamName";
            return await cmd.ExecuteEntityCollectionAsync<GmTeam>();
        }

        public async Task<GmTeam> GetAsync(string teamName)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = $"SELECT {SelectColumns} FROM teams WHERE TeamName = @TeamName";
            cmd.AddParameter("@TeamName", MySqlDbType.String, teamName);
            return await cmd.ExecuteEntityAsync<GmTeam>();
        }

        public async Task<GmTeam> CreateAsync(CreateGmTeamRequest request)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText =
                @"INSERT INTO teams (TeamName, Description, AuthToken, Enabled, WhiteList)
VALUES (@TeamName, @Description, @AuthToken, @Enabled, @WhiteList)";
            cmd.AddParameter("@TeamName", MySqlDbType.String, request.TeamName);
            cmd.AddParameter("@Description", MySqlDbType.String, request.Description);
            cmd.AddParameter("@AuthToken", MySqlDbType.String, request.AuthToken);
            cmd.AddParameter("@Enabled", MySqlDbType.Byte, request.Enabled ? (byte)1 : (byte)0);
            cmd.AddParameter("@WhiteList", MySqlDbType.VarChar, request.WhiteList);
            await cmd.ExecuteNonQueryAsync();
            return await GetAsync(request.TeamName);
        }

        public async Task<GmTeam> UpdateAsync(string teamName, UpdateGmTeamRequest request)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText =
                @"UPDATE teams SET Description = @Description, AuthToken = @AuthToken, Enabled = @Enabled, WhiteList = @WhiteList
WHERE TeamName = @TeamName";
            cmd.AddParameter("@TeamName", MySqlDbType.String, teamName);
            cmd.AddParameter("@Description", MySqlDbType.String, request.Description);
            cmd.AddParameter("@AuthToken", MySqlDbType.String, request.AuthToken);
            cmd.AddParameter("@Enabled", MySqlDbType.Byte, request.Enabled ? (byte)1 : (byte)0);
            cmd.AddParameter("@WhiteList", MySqlDbType.VarChar, request.WhiteList);
            await cmd.ExecuteNonQueryAsync();
            return await GetAsync(teamName);
        }

        public async Task<bool> DeleteAsync(string teamName)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = "DELETE FROM teams WHERE TeamName = @TeamName";
            cmd.AddParameter("@TeamName", MySqlDbType.String, teamName);
            var n = await cmd.ExecuteNonQueryAsync();
            return n > 0;
        }

        private IDbMySQLCommand createCommandOrThrow()
        {
            var cmd = _mySQLManager.CreateDBCommand(ConnectId);
            if (cmd == null)
                throw ECException.Build(HttpStatusCode.InternalServerError,
                    "MySQL settings missing: AppSettings.MySQLSettings (ConnectId=GM).");
            return cmd;
        }
    }
}
