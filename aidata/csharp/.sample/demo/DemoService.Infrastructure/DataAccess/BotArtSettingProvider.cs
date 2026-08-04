using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.DataAccess
{
    [DependencyInjection(typeof(IBotArtSettingProvider))]
    public class BotArtSettingProvider : IBotArtSettingProvider
    {
        private const string ConnectId = "news";

        private const string SelectColumns =
            "account, aihints, aimodes, articlesites, cansame, enabled, footers, gtypes, lastusetime, maxpost, mode, settings, titles, todohours";

        private readonly ICassandraManager _cassandraManager;

        public BotArtSettingProvider(ICassandraManager cassandraManager)
        {
            _cassandraManager = cassandraManager;
        }

        public async Task<List<BotArtSetting>> ListAsync()
        {
            var session = createSessionOrThrow();
            session.ResetParams();
            session.CommandText = $"SELECT {SelectColumns} FROM botartsettings";
            return await session.ExecuteEntityCollectionAsync<BotArtSetting>();
        }

        public async Task<BotArtSetting> GetAsync(string account)
        {
            var session = createSessionOrThrow();
            session.ResetParams();
            session.CommandText = $"SELECT {SelectColumns} FROM botartsettings WHERE account = ?";
            session.DataParams = new object[] { account };
            return await session.ExecuteEntityAsync<BotArtSetting>();
        }

        public async Task<BotArtSetting> CreateAsync(CreateBotArtSettingRequest request)
        {
            var session = createSessionOrThrow();
            session.ResetParams();
            session.CommandText =
                @"INSERT INTO botartsettings (account, aihints, aimodes, articlesites, cansame, enabled, footers, gtypes, lastusetime, maxpost, mode, settings, titles, todohours)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
            session.DataParams = new object[]
            {
                request.Account,
                request.Aihints,
                request.Aimodes,
                request.Articlesites,
                request.Cansame,
                request.Enabled,
                request.Footers,
                request.Gtypes,
                request.Lastusetime,
                request.Maxpost,
                request.Mode,
                request.Settings,
                request.Titles,
                request.Todohours
            };
            await session.ExecCommand();
            return await GetAsync(request.Account);
        }

        public async Task<BotArtSetting> UpdateAsync(string account, UpdateBotArtSettingRequest request)
        {
            var session = createSessionOrThrow();
            session.ResetParams();
            session.CommandText =
                @"UPDATE botartsettings SET aihints = ?, aimodes = ?, articlesites = ?, cansame = ?, enabled = ?, footers = ?, gtypes = ?, lastusetime = ?, maxpost = ?, mode = ?, settings = ?, titles = ?, todohours = ?
WHERE account = ?";
            session.DataParams = new object[]
            {
                request.Aihints,
                request.Aimodes,
                request.Articlesites,
                request.Cansame,
                request.Enabled,
                request.Footers,
                request.Gtypes,
                request.Lastusetime,
                request.Maxpost,
                request.Mode,
                request.Settings,
                request.Titles,
                request.Todohours,
                account
            };
            await session.ExecCommand();
            return await GetAsync(account);
        }

        public async Task DeleteAsync(string account)
        {
            var session = createSessionOrThrow();
            session.ResetParams();
            session.CommandText = "DELETE FROM botartsettings WHERE account = ?";
            session.DataParams = new object[] { account };
            await session.ExecCommand();
        }

        private ICassandraSession createSessionOrThrow()
        {
            try
            {
                return _cassandraManager.CreateSession(ConnectId);
            }
            catch (Exception ex)
            {
                throw ECException.Build(HttpStatusCode.InternalServerError,
                    $"Cassandra settings missing or invalid (ConnectId={ConnectId}). {ex.Message}");
            }
        }
    }
}
