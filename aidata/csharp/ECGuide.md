# ECFramework / ECCore Common Library Usage Guide

This guide is grounded in **`demo/DemoService`**, **`src/Core/ECCore`**, and **`src/ECService`**. Use it for AI-assisted development in this repository.

## Labeling (how to read statements)

| Label | Meaning |
|--------|---------|
| **Confirmed** | Observed in `demo/DemoService` or stated as **organizational policy** below. |
| **Inferred** | Derived from ECCore / ECService **source code**; not exercised as an acceptance test in DemoService. |
| **Need Confirmation** | Not found in DemoService; do **not** invent behavior—verify in code or ask the team. |
| **Confirmed policy** | Organization rule; treat as **MUST** / **MUST NOT** alongside library facts. |

---

## 1. Scope and reference projects

**Confirmed**

- Primary sample: `demo/DemoService` (host), `demo/DemoService.DomainService`, `demo/DemoService.Infrastructure`, `demo/DemoService.Interface`, `demo/DemoService.Model`.
- Framework entry: `src/ECService/EDASFramework.cs`, `src/ECService/WebHostBuilderExtensions.cs`, `src/ECService/StartupBase.cs`, `src/ECService/ECServiceStartup.cs`.
- Core library: `src/Core/ECCore`.
- Solution projects target **`net10.0`** (requires **.NET 10 SDK**).

**Out of scope** unless explicitly marked *Need Confirmation*: `demo/WSDemo`, `aidata/csharp/.sample`, `aidata/templates` (they are not `demo/DemoService`).

---

## 2. Host bootstrap and Startup

**Confirmed**

- `Program.Main` calls `EDASFramework.Bootstrap<Startup>(args)` (`demo/DemoService/Program.cs`).
- `EDASFramework.CreateWebHostBuilder<TStartUp>` uses `WebHost.CreateDefaultBuilder(args)`, then **`.UseECFramework()`**, Kestrel, default URL `http://*:5000`, and **`.UseStartup<TStartUp>()`** (`src/ECService/EDASFramework.cs`).
- **`UseECFramework()`** (`src/ECService/WebHostBuilderExtensions.cs`) wires `ECLibraryContainer.Current.ConfigureServices` and merges `IConfiguration` into the framework service collection during host configuration.
- **`StartupBase`** (`src/ECService/StartupBase.cs`) implements **`IStartup`**. Hosting invokes **`IStartup.ConfigureServices`** → virtual **`ConfigureServices`** → **`CreateServiceProvider`**.
- **`ECServiceStartup`** overrides **`CreateServiceProvider`** to call **`services.BootstrapApplicationServiceProvider()`** (see §3). Project `Startup` classes inherit **`ECServiceStartup`**, not `StartupBase` directly.

**Confirmed (DemoService)**

- `Startup` inherits **`ECServiceStartup`** and overrides `ConfigureServices` / `Configure`; DemoService adds a named `HttpClient("Default")` with a permissive certificate callback, then calls `base.ConfigureServices` / `base.Configure` (`demo/DemoService/Startup.cs`).

**Inferred**

- `WebHost` / `WebHost.CreateDefaultBuilder` are obsolete on .NET 10 (`ASPDEPR008`) but remain the EC host entry; `WebApplicationBuilder` migration is out of scope unless explicitly requested.

---

## 3. Dependency injection (`[DependencyInjection]`)

**Confirmed**

- Implementation types are marked with **`[DependencyInjection(typeof(I…))]`** (e.g. Domain services and Infrastructure providers under `demo/DemoService.DomainService` and `demo/DemoService.Infrastructure`).
- **`DependencyInjectionAttribute`** defaults **`Lifetime`** to **`ServiceLifetime.Singleton`** (`src/Core/ECCore/DI/DependencyInjectionAttribute.cs`).
- Application services are merged and the provider is built via **`services.BootstrapApplicationServiceProvider()`** from `ECServiceStartup.CreateServiceProvider` → **`ECLibraryContainer.BootstrapApplicationServiceProvider`** (`src/Core/ECCore/ECLibraryContainer.cs`).
- **`StartupBase` MUST implement `IStartup`** so hosting calls **`CreateServiceProvider`**. Otherwise `[DependencyInjection]` scan results are not merged into the ASP.NET Core container (symptom: `Unable to resolve service for type '…'`).

**Confirmed policy**

- New DomainService / Infrastructure bindings **MUST** use **`ServiceLifetime.Singleton`** for `[DependencyInjection]`. **MUST NOT** switch those registrations to Scoped/Transient unless a future written exception exists (this guide does not list such exceptions).
- **MUST NOT** remove **`IStartup`** from `StartupBase` or bypass **`BootstrapApplicationServiceProvider`** for standard EC-hosted Web APIs.

**Inferred**

- **`Helper.BuildServiceDescriptionCollection`** (`src/Core/ECCore/DI/Utility.cs`) scans loaded assemblies for concrete classes with `[DependencyInjection]` and builds service descriptors. The **full enumerated list** of all registered services is **not** a DemoService deliverable and **MUST NOT** be assumed or fabricated by AI.

**Confirmed (DemoService)**

- DemoService code does **not** reference `IDictionaryUtility` or `IActivator` directly. **`DictionaryUtilityExtensions`** in ECCore are **optional** convenience wrappers; business code **MAY** use BCL / native dictionary APIs instead.

---

## 4. Configuration

**Confirmed**

- **`AppSettingProvider`** uses `_config.GetAppSettings<AppSettings>()` (`demo/DemoService.Infrastructure/DataAccess/AppSettingProvider.cs`).
- Models live under `demo/DemoService.Model` (e.g. `AppSettings : DefaultAppSettings` in `demo/DemoService.Model/Models.cs`).
- **`IECConfig` / `DefaultECConfig`** live under `src/Core/ECCore/Configuration`.
- Example JSON: `demo/DemoService/appsettings.json`, environment overrides such as `demo/DemoService/appsettings.Development.json`.

**Confirmed policy (Zookeeper / remote config)**

- Remote config / Zookeeper paths in **`DefaultECConfig`** are **legacy** only. This guide **MUST NOT** instruct enabling them as a current configuration method.

---

## 5. Data access (PostgreSQL, MySQL, Cassandra, Redis)

**Confirmed (patterns from DemoService Infrastructure)**

- **PostgreSQL** — `PgUserProvider`: `IPostgreSQLManager.CreateDBCommand(connectId)`, `IDbPostgreSQLCommand` with `CommandText`, `AddParameter`, `ExecuteEntityAsync` / `ExecuteEntityCollectionAsync` / `ExecuteNonQueryAsync`; missing configuration uses `ECException.Build(...)` (`demo/DemoService.Infrastructure/DataAccess/PgUserProvider.cs`).
- **MySQL** — `GmTeamProvider`: `IMySQLManager.CreateDBCommand`, `IDbMySQLCommand`, `MySqlDbType` parameters (`demo/DemoService.Infrastructure/DataAccess/GmTeamProvider.cs`).
- **Cassandra** — `BotArtSettingProvider`: `ICassandraManager.CreateSession`, `ICassandraSession` `CommandText` / `DataParams`, `ExecuteEntityAsync` / `ExecCommand` (`demo/DemoService.Infrastructure/DataAccess/BotArtSettingProvider.cs`).
- **Redis** — `CacheUserProvider`: `IRedisManager` hash/key APIs; model helpers e.g. `demo/DemoService.Model/CacheUserRedis.cs` (`demo/DemoService.Infrastructure/DataAccess/CacheUserProvider.cs`).

**Do / Don’t (observed)**

- SQL / data-store specific code appears under **`demo/DemoService.Infrastructure/DataAccess/*Provider.cs`**, not in Controllers.

**Confirmed policy (transactions)**

- Application code **MUST NOT** implement distributed transactions across resources. For multi-step atomicity, **MUST** use **database stored procedures** (or equivalent DB-side mechanisms). This guide does **not** invent a DemoService transaction API.

---

## 6. Outbound HTTP

**Confirmed**

- **`RestfulClient`** is registered with `[DependencyInjection(typeof(IRestfulClient))]` and uses **`IHttpClientFactory`** internally (`src/Core/ECCore/Http/Implement/RestfulClient.cs`) — **library implementation detail**.
- **`CommunityProvider`**: `new RestfulRequest(IHttpContextAccessor, IECConfig)`, `SetUrlParameter`, `CreateRequest(…)` → **`IRestfulClient.SendAsync(HttpRequestMessage)`** (`demo/DemoService.Infrastructure/DataAccess/CommunityProvider.cs`). **`RestfulRequest`** resolves gateway-style settings via `GetAppSettings<DefaultAppSettings>()` / `RestfulSetting` (`src/Core/ECCore/Http/Implement/RestfulRequest.cs`).

**Confirmed (Demo-only pattern)**

- In the same file, **`CreateArticleAsync`** builds `HttpRequestMessage` + **`FormUrlEncodedContent`** and calls **`_restfulClient.SendAsync(msg)`** — a **`application/x-www-form-urlencoded`** path **specific to this demo**, not the default `RestfulRequest` flow.

Align with **`aidata/csharp/.cursor_rules`**: prefer ECCore HTTP abstractions; raw HTTP only where documented exceptions apply, isolated in Infrastructure, not in Controller/Service layer.

---

## 7. Logging (`IKafkaLogger` and `KafkaLoggerSettings`)

**Confirmed**

- Domain services inject **`IKafkaLogger`** and call **`_logger.Log(LogLevel.*, string)`** (e.g. `demo/DemoService.DomainService/PgUserService.cs`). Interface: `src/Core/ECCore/Logger/IKafkaLogger.cs`.
- **`KafkaLoggerSettings`** includes `GroupId`, `BootstrapServers`, `Topic`, optional **`LokiPath`** (`src/Core/ECCore/Logger/IKafkaLogger.cs`).

**Confirmed (`ECServiceStartup`)**

- Global exception handler: if **`Configuration.GetSection("KafkaLoggerSettings").Exists()`**, it resolves **`IKafkaLogger`** through **`ECLibraryContainer.Current.GetService<IKafkaLogger>()`** and logs at **Error** for `HttpResponseException` and unhandled exceptions (`src/ECService/ECServiceStartup.cs`).

**Confirmed policy**

- **MUST** declare Kafka / Loki-related endpoints and options in **`appsettings.json`** or equivalent layered config (`appsettings.*.json`, environment-variable-backed configuration with the **same section shape**). **MUST NOT** rely on ad-hoc hard-coded endpoints in code without a matching configuration section.

**Inferred (implementation detail — cite source)**

- Queueing, background threads, Kafka produce, optional Loki push, and message shaping are implemented in **`DefaultKafkaLogger`** (`src/Core/ECCore/Logger/Implement/DefaultKafkaLogger.cs`). When describing behavior beyond Demo-confirmed usage, **MUST** label as **Inferred** from that file and **MUST NOT** invent defaults or operational guarantees.

---

## 8. Errors and API responses

**Confirmed**

- **`ECException.Build`**, **`BuildNotFound`**, **`BuildBadRequest`** produce **`HttpResponseException`** (`src/Core/ECCore/ExceptionHandler/ECException.cs`).
- **`ECServiceStartup`** exception middleware returns JSON shaped as **`{ Error = … }`** with status from `HttpResponseException` (`src/ECService/ECServiceStartup.cs`).
- Demo controllers generally return **`Task<T>`** / **`Task`** and let the pipeline handle errors (`demo/DemoService/Controllers`).

---

## 9. Cross-cutting library behavior (`ECLibraryContainer`)

**Inferred**

- `ECLibraryContainer` copies a **subset** of scanned services (including `IDictionaryUtility`, `IActivator`, `IDependencyInjectionProviderFactory`, static path abstractions) into an early **`frameworkServiceCollection`** for bootstrap (`src/Core/ECCore/ECLibraryContainer.cs`).

**MUST NOT**

- Maintain or require a “full service inventory” in documentation beyond describing the **scan-based registration** mechanism.

---

## 10. Swagger, metrics, and pipeline (ECServiceStartup)

**Inferred / Confirmed (library)**

- `ECServiceStartup.Configure` wires exception handling, Prometheus metrics, Swagger, routing, CORS, etc. (`src/ECService/ECServiceStartup.cs`). Exact feature set **Inferred** from source; DemoService does not document every flag.
- Swagger is registered in **`ECService`** via **`Swashbuckle.AspNetCore` 7.2.0**. Project Startup classes **MUST NOT** add duplicate `AddSwaggerGen` (see `layer-service.mdc`).

---

## 11. Project references and NuGet (net10)

**Confirmed**

- Class libraries needing ASP.NET types use **`<FrameworkReference Include="Microsoft.AspNetCore.App" />`**. **MUST NOT** add legacy **`Microsoft.AspNetCore.*` 2.x** package references.
- Web host projects use **`Microsoft.NET.Sdk.Web`**; no duplicate AspNetCore packages needed.
- **`Microsoft.Extensions.*`** in `.csproj` files use **10.0.x** where explicitly referenced.
- Root **`Directory.Build.props`** pins **`Newtonsoft.Json` 13.0.3** for transitive vulnerability overrides.

**Confirmed policy**

- Copy **`TargetFramework`**, **`FrameworkReference`**, and Extensions versions from sibling `.csproj` under **`demo/`** or **`src/`** — not from `.sample` or `aidata/templates`.

---

## 12. `demo/DemoService` layout (quick map)

| Area | Paths |
|------|--------|
| API | `demo/DemoService/Controllers/` — `CacheController`, `CommunityController`, `GmController`, `NewsController`, `PgUsersController`, `SettingsController` |
| Domain | `demo/DemoService.DomainService/` — `BotArtSettingService`, `CacheUserService`, `CommunityArticleService`, `GmTeamService`, `PgUserService`, `SettingsService` |
| Infrastructure — data access | `demo/DemoService.Infrastructure/DataAccess/` — `AppSettingProvider`, `BotArtSettingProvider`, `CacheUserProvider`, `CommunityProvider`, `GmTeamProvider`, `PgUserProvider` |
| Infrastructure — validators | `demo/DemoService.Infrastructure/Validators/` — `BotArtSettingValidator`, `CacheUserValidator`, `CommunityArticleValidator`, `GmTeamValidator`, `PgUserValidator`, `SettingsValidator` |

---

## 13. Gaps, boundaries, and what not to guess

**Confirmed**

- DemoService does **not** use `IDictionaryUtility` / `IActivator` in source.
- Organizational policies in this document (**Singleton** for `[DependencyInjection]`, **Zookeeper legacy only**, **no distributed transactions in app code—use SP**, **Kafka/Loki in configuration files**) override generic assumptions.

**Inferred**

- **`DefaultKafkaLogger`** internal behavior — see `src/Core/ECCore/Logger/Implement/DefaultKafkaLogger.cs`.
- Full **`BuildServiceDescriptionCollection`** outcome depends on which assemblies are loaded — **do not enumerate** without checking the codebase.

**Need Confirmation**

- Any behavior **not** visible in **`demo/DemoService`** or the cited ECCore / ECService files.

**Out of scope**

- `demo/WSDemo`, `aidata/csharp/.sample`, `aidata/templates` unless explicitly brought into scope.

**Confirmed (`.sample`, `aidata/templates`)**

- Sample / template sources may lag behind `demo/DemoService` (older TFM or packages). For **`.csproj`**, **TFM**, and **host bootstrap**, treat **`demo/`** and **`src/`** as authoritative.

---

## How AI Should Use This Guide

1. **Search `demo/DemoService` first** for patterns (Controllers → DomainService → Infrastructure).
2. Treat statements in this file as **Confirmed** only where they match **DemoService** or **explicit policy** above; library internals are **Inferred** from cited paths.
3. If something is **not** in DemoService or ECCore sources, mark it **Need Confirmation** — **do not** invent architecture, config keys, or transaction strategies.
4. Respect **`aidata/csharp/.cursor_rules`**; on conflict with **Confirmed policy** in this guide, **Confirmed policy** in this guide wins for EC host, DI lifetime, Zookeeper, transactions, and Kafka/Loki configuration.

---

*Document path: `aidata/csharp/ECGuide.md`*
