using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;
using Microsoft.AspNetCore.Http;

namespace DemoService.Infrastructure.DataAccess
{
    [DependencyInjection(typeof(ICommunityProvider))]
    public class CommunityProvider : ICommunityProvider
    {
        private static readonly JsonSerializerOptions JsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        private readonly IRestfulClient _restfulClient;
        private readonly IECConfig _eCConfig;
        private readonly IHttpContextAccessor _httpContextAccessor;

        public CommunityProvider(IRestfulClient restfulClient, IECConfig eCConfig,
            IHttpContextAccessor httpContextAccessor)
        {
            _restfulClient = restfulClient;
            _eCConfig = eCConfig;
            _httpContextAccessor = httpContextAccessor;
        }

        public Task<ArticleListPageResponse> ListArticlesAsync(string gameType,
            IReadOnlyDictionary<string, string> queryParameters)
        {
            var rest = new RestfulRequest(_httpContextAccessor, _eCConfig);
            rest.SetUrlParameter("game_type", gameType);
            foreach (var kv in queryParameters)
                rest.SetUrlParameter(kv.Key, kv.Value);
            rest.CreateRequest("CommunityArticlesList");
            return sendJsonAsync<ArticleListPageResponse>(rest.Message);
        }

        public Task<ArticleDocumentResponse> GetArticleAsync(string gameType, string articleId)
        {
            var rest = new RestfulRequest(_httpContextAccessor, _eCConfig);
            rest.SetUrlParameter("game_type", gameType);
            rest.SetUrlParameter("article_id", articleId);
            rest.CreateRequest("CommunityArticleGet");
            return sendJsonAsync<ArticleDocumentResponse>(rest.Message);
        }

        public async Task<ArticleDocumentResponse> CreateArticleAsync(string gameType,
            IReadOnlyList<KeyValuePair<string, string>> formFields)
        {
            var baseUrl = getCommunityGatewayBaseUrl();
            var uri = $"{baseUrl}/api/community/{Uri.EscapeDataString(gameType)}/articles";
            var msg = new HttpRequestMessage(HttpMethod.Post, uri)
            {
                Content = new FormUrlEncodedContent(formFields)
            };
            applyOutboundHeaders(msg);
            return await sendJsonAsync<ArticleDocumentResponse>(msg);
        }

        public Task<ArticleDocumentResponse> UpdateArticleAsync(string gameType, EditCommunityArticleRequest request)
        {
            var rest = new RestfulRequest(_httpContextAccessor, _eCConfig);
            rest.SetUrlParameter("game_type", gameType);
            rest.SetRequestBody(new Dictionary<string, string>
            {
                { "id", request.Id },
                { "content", request.Content }
            });
            rest.CreateRequest("CommunityArticleEdit");
            return sendJsonAsync<ArticleDocumentResponse>(rest.Message);
        }

        public Task<ArticleOkResponse> DeleteArticleAsync(string gameType, string id)
        {
            var rest = new RestfulRequest(_httpContextAccessor, _eCConfig);
            rest.SetUrlParameter("game_type", gameType);
            rest.SetUrlParameter("id", id);
            rest.CreateRequest("CommunityArticleDelete");
            return sendJsonAsync<ArticleOkResponse>(rest.Message);
        }

        private string getCommunityGatewayBaseUrl()
        {
            var gatewayInfos = _eCConfig.GatewayInfos();
            var current = gatewayInfos.Where(x => x.CanUse).OrderBy(x => x.ErrorCounter).FirstOrDefault();
            if (current == null)
                throw ECException.Build(HttpStatusCode.ServiceUnavailable, "No alive gateway.");
            return current.GatewayUrl.TrimEnd('/');
        }

        private async Task<T> sendJsonAsync<T>(HttpRequestMessage msg)
        {
            var resp = await _restfulClient.SendAsync(msg);
            var body = await resp.Content.ReadAsStringAsync();
            if (!resp.IsSuccessStatusCode)
            {
                var msgErr = string.IsNullOrWhiteSpace(body) ? resp.ReasonPhrase : body;
                throw ECException.Build((HttpStatusCode)(int)resp.StatusCode, msgErr);
            }

            if (string.IsNullOrWhiteSpace(body))
                return default;
            try
            {
                return JsonSerializer.Deserialize<T>(body, JsonOptions);
            }
            catch (JsonException ex)
            {
                throw ECException.Build(HttpStatusCode.BadGateway, $"Invalid JSON from community service: {ex.Message}");
            }
        }

        private void applyOutboundHeaders(HttpRequestMessage msg)
        {
            if (_httpContextAccessor?.HttpContext?.Request != null)
            {
                var req = _httpContextAccessor.HttpContext.Request;
                foreach (var header in req.Headers)
                {
                    if (string.Equals(header.Key, "Content-Type", StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(header.Key, "Content-Length", StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(header.Key, "Accept", StringComparison.OrdinalIgnoreCase))
                        continue;
                    msg.Headers.TryAddWithoutValidation(header.Key, header.Value.ToString());
                }

                var host = req.Host.Value;
                if (host == "::1" || host.Contains("localhost", StringComparison.OrdinalIgnoreCase) ||
                    host.Contains("127.0.0.1", StringComparison.OrdinalIgnoreCase) ||
                    host.Contains("192.168.", StringComparison.OrdinalIgnoreCase))
                {
                    if (!msg.Headers.Contains("X-COMPANY"))
                        msg.Headers.TryAddWithoutValidation("X-COMPANY", ConstValues.CompanyCode);
                    if (!msg.Headers.Contains("X-Auth"))
                        msg.Headers.TryAddWithoutValidation("X-Auth", ConstValues.Token);
                }
            }
            else
            {
                if (!msg.Headers.Contains("X-COMPANY"))
                    msg.Headers.TryAddWithoutValidation("X-COMPANY", ConstValues.CompanyCode);
                if (!msg.Headers.Contains("X-Auth"))
                    msg.Headers.TryAddWithoutValidation("X-Auth", ConstValues.Token);
            }
        }
    }
}
