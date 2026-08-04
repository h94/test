using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;
using NpgsqlTypes;

namespace DemoService.Infrastructure.DataAccess
{
    [DependencyInjection(typeof(IPgUserProvider))]
    public class PgUserProvider : IPgUserProvider
    {
        private const string ConnectId = "test";

        private const string SelectColumns =
            @"id AS ""Id"", username AS ""Username"", email AS ""Email"", is_active AS ""IsActive"", created_at AS ""CreatedAt""";

        private readonly IPostgreSQLManager _postgresql;

        public PgUserProvider(IPostgreSQLManager postgresql)
        {
            _postgresql = postgresql;
        }

        public async Task<List<PgUser>> ListAsync()
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = $"SELECT {SelectColumns} FROM users ORDER BY id";
            return await cmd.ExecuteEntityCollectionAsync<PgUser>();
        }

        public async Task<PgUser> GetAsync(int id)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = $"SELECT {SelectColumns} FROM users WHERE id = @id";
            cmd.AddParameter("@id", NpgsqlDbType.Integer, id);
            return await cmd.ExecuteEntityAsync<PgUser>();
        }

        public async Task<PgUser> CreateAsync(CreatePgUserRequest request)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = $@"INSERT INTO users (username, email, is_active) VALUES (@username, @email, @is_active)
RETURNING {SelectColumns}";
            cmd.AddParameter("@username", NpgsqlDbType.Varchar, request.Username);
            cmd.AddParameter("@email", NpgsqlDbType.Varchar, (object)request.Email ?? DBNull.Value);
            cmd.AddParameter("@is_active", NpgsqlDbType.Boolean, request.IsActive ?? true);
            return await cmd.ExecuteEntityAsync<PgUser>();
        }

        public async Task<PgUser> UpdateAsync(int id, UpdatePgUserRequest request)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = $@"UPDATE users SET
  username = @username,
  email = COALESCE(@email, email),
  is_active = COALESCE(@is_active, is_active)
WHERE id = @id
RETURNING {SelectColumns}";
            cmd.AddParameter("@id", NpgsqlDbType.Integer, id);
            cmd.AddParameter("@username", NpgsqlDbType.Varchar, request.Username);
            cmd.AddParameter("@email", NpgsqlDbType.Varchar, (object)request.Email ?? DBNull.Value);
            cmd.AddParameter("@is_active", NpgsqlDbType.Boolean, (object)request.IsActive ?? DBNull.Value);
            return await cmd.ExecuteEntityAsync<PgUser>();
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var cmd = createCommandOrThrow();
            cmd.CommandText = "DELETE FROM users WHERE id = @id";
            cmd.AddParameter("@id", NpgsqlDbType.Integer, id);
            var n = await cmd.ExecuteNonQueryAsync();
            return n > 0;
        }

        private IDbPostgreSQLCommand createCommandOrThrow()
        {
            var cmd = _postgresql.CreateDBCommand(ConnectId);
            if (cmd == null)
                throw ECException.Build(HttpStatusCode.InternalServerError,
                    "PostgreSQL settings missing: AppSettings.PostgreSQLSettings (ConnectId=test).");
            return cmd;
        }
    }
}
