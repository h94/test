using System.Collections.Generic;
using System.Net;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.Validators
{
    [DependencyInjection(typeof(ICommunityArticleValidator))]
    public class CommunityArticleValidator : ICommunityArticleValidator
    {
        public void ValidateGameType(string gameType)
        {
            if (string.IsNullOrWhiteSpace(gameType))
                throw ECException.BuildBadRequest("gameType");
        }

        public void ValidateArticleId(string articleId)
        {
            if (string.IsNullOrWhiteSpace(articleId))
                throw ECException.BuildBadRequest("articleId");
        }

        public void ValidateCreateRequest(CreateCommunityArticleRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (string.IsNullOrWhiteSpace(request.User))
                throw ECException.BuildBadRequest("user");
            if (string.IsNullOrWhiteSpace(request.UserName))
                throw ECException.BuildBadRequest("userName");
            if (string.IsNullOrWhiteSpace(request.ArticType))
                throw ECException.BuildBadRequest("articType");
            if (string.IsNullOrWhiteSpace(request.Content))
                throw ECException.BuildBadRequest("content");
            if (request.Content.Length > 2000)
                throw ECException.Build(HttpStatusCode.BadRequest, "content exceeds 2000 characters.");
        }

        public void ValidateEditRequest(EditCommunityArticleRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (string.IsNullOrWhiteSpace(request.Id))
                throw ECException.BuildBadRequest("id");
            if (string.IsNullOrWhiteSpace(request.Content))
                throw ECException.BuildBadRequest("content");
            if (request.Content.Length > 2000)
                throw ECException.Build(HttpStatusCode.BadRequest, "content exceeds 2000 characters.");
        }

        public void ValidateDeleteId(string id)
        {
            if (string.IsNullOrWhiteSpace(id))
                throw ECException.BuildBadRequest("id");
        }

        public IReadOnlyDictionary<string, string> BuildListArticleQueryParameters(string index, string page,
            bool? showHidden, string leagues, string articTopics, string memberShips)
        {
            var d = new Dictionary<string, string>();
            if (!string.IsNullOrEmpty(index))
                d["index"] = index;
            if (!string.IsNullOrEmpty(page))
                d["page"] = page;
            if (showHidden.HasValue)
                d["show_hidden"] = showHidden.Value ? "true" : "false";
            if (!string.IsNullOrEmpty(leagues))
                d["leagues"] = leagues;
            if (!string.IsNullOrEmpty(articTopics))
                d["articTopics"] = articTopics;
            if (!string.IsNullOrEmpty(memberShips))
                d["memberShips"] = memberShips;
            return d;
        }

        public IReadOnlyList<KeyValuePair<string, string>> BuildCreateArticleFormFields(CreateCommunityArticleRequest r)
        {
            var list = new List<KeyValuePair<string, string>>
            {
                new("user", r.User ?? ""),
                new("userName", r.UserName ?? ""),
                new("rank", r.Rank.ToString()),
                new("headShotPath", r.HeadShotPath ?? ""),
                new("followerCount", r.FollowerCount.ToString()),
                new("articType", r.ArticType ?? ""),
                new("content", r.Content ?? "")
            };
            if (!string.IsNullOrEmpty(r.ArticTopic))
                list.Add(new KeyValuePair<string, string>("articTopic", r.ArticTopic));
            if (!string.IsNullOrEmpty(r.Leagues))
                list.Add(new KeyValuePair<string, string>("leagues", r.Leagues));
            if (!string.IsNullOrEmpty(r.MemberShips))
                list.Add(new KeyValuePair<string, string>("memberShips", r.MemberShips));
            if (!string.IsNullOrEmpty(r.PredictContent))
                list.Add(new KeyValuePair<string, string>("predictContent", r.PredictContent));
            return list;
        }
    }
}
