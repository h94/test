using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace DemoService.Model
{
    /// <summary>對應 community OpenAPI ArticleDocumentResponse（aidata/webapi/communityservice.json）。</summary>
    public class ArticleDocumentResponse
    {
        public string Id { get; set; }
        public string ArticType { get; set; }
        [JsonPropertyName("game_type")]
        public string GameType { get; set; }
        public string User { get; set; }
        public string UserName { get; set; }
        public string Content { get; set; }
        public object ArticTopic { get; set; }
        public object Leagues { get; set; }
        public object MemberShips { get; set; }
        public object PredictContent { get; set; }
        [JsonPropertyName("create_timestamp")]
        public long? CreateTimestamp { get; set; }
        [JsonPropertyName("edit_timestamp")]
        public long? EditTimestamp { get; set; }
        public object Comments { get; set; }
        [JsonPropertyName("like_count")]
        public object LikeCount { get; set; }
        public int? CommentCount { get; set; }
        public int? Rank { get; set; }
        public int? FollowerCount { get; set; }
        public object HeadShotPath { get; set; }
        public bool? Top { get; set; }
        public bool? Hot { get; set; }
        [JsonPropertyName("hot_score")]
        public object HotScore { get; set; }
        public bool? Hidden { get; set; }
    }

    public class ArticleListPageResponse
    {
        public List<ArticleDocumentResponse> Articles { get; set; }
        [JsonPropertyName("next_page")]
        public bool? NextPage { get; set; }
        [JsonPropertyName("need_click")]
        public bool? NeedClick { get; set; }
    }

    public class ArticleOkResponse
    {
        public string Status { get; set; }
    }

    /// <summary>CreateArticleArgs — 對外 API 以 JSON 接收，Infrastructure 轉成 form-urlencoded。</summary>
    public class CreateCommunityArticleRequest
    {
        public string User { get; set; }
        public string UserName { get; set; }
        public int Rank { get; set; }
        public string HeadShotPath { get; set; }
        public int FollowerCount { get; set; }
        public string ArticType { get; set; }
        public string Content { get; set; }
        public string ArticTopic { get; set; }
        public string Leagues { get; set; }
        public string MemberShips { get; set; }
        public string PredictContent { get; set; }
    }

    /// <summary>EditArticleArgs。</summary>
    public class EditCommunityArticleRequest
    {
        public string Id { get; set; }
        public string Content { get; set; }
    }
}
