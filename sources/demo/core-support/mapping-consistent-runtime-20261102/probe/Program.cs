using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using Dapper;
using GeoJSON.Net.Feature;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Npgsql;
using Resgrid.Model;
using Resgrid.Repositories.NoSqlRepository;
using Resgrid.Repositories.DataRepository.Servers.PostgreSql;

static void Check(bool condition, string name)
{
    if (!condition) throw new InvalidOperationException(name);
    Console.WriteLine("PASS " + name);
}

var serialize = typeof(MapLayersDocRepository).GetMethod("SerializeDocument", BindingFlags.NonPublic | BindingFlags.Static)!;
var deserialize = typeof(MapLayersDocRepository).GetMethod("DeserializeDocument", BindingFlags.NonPublic | BindingFlags.Static)!;
var shape = """{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-87.65,41.88]},"properties":{"name":"TRAINING ONLY","shape":"Marker","color":"#0080ff","text":"Staging"}},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-87.66,41.87],[-87.64,41.87],[-87.64,41.89],[-87.66,41.89],[-87.66,41.87]],[[-87.655,41.875],[-87.645,41.875],[-87.645,41.885],[-87.655,41.885],[-87.655,41.875]]]},"properties":{"name":"Zone","shape":"Polygon","color":"#0080ff"}}]}""";
var features = JsonConvert.DeserializeObject<FeatureCollection>(shape)!;
var layer = new MapLayer { DepartmentId = 51, Name = "TRAINING ONLY", Color = "#0080ff", PgId = "17", IsOnByDefault = true, IsSearchable = false, Data = new MapLayerData() };
layer.Data.Hydrate(features);
var encoded = (string)serialize.Invoke(null, new object[] { layer })!;
var restored = (MapLayer)deserialize.Invoke(null, new object[] { encoded })!;
Check(restored.PgId == "17" && restored.GetId() == "17", "PostgreSQL identity retained");
Check(restored.DepartmentId == 51 && restored.Name == layer.Name && restored.Color == layer.Color, "metadata retained");
Check(restored.IsOnByDefault && !restored.IsSearchable, "visibility flags retained");
var actual = JToken.Parse(JsonConvert.SerializeObject(restored.Data.Convert()));
Check(JToken.DeepEquals(actual, JToken.Parse(JsonConvert.SerializeObject(features))), "all original coordinates, properties and polygon holes retained");
Check(actual["features"]![1]!["geometry"]!["coordinates"]!.Count() == 2, "interior polygon ring retained");
var again = (MapLayer)deserialize.Invoke(null, new[] { serialize.Invoke(null, new object[] { restored }) })!;
Check(JToken.DeepEquals(actual, JToken.Parse(JsonConvert.SerializeObject(again.Data.Convert()))), "second save/edit round trip retained");
var bad = JObject.Parse(encoded); bad.Remove("featureCollection");
var rejected = false;
try { deserialize.Invoke(null, new object[] { bad.ToString() }); }
catch (TargetInvocationException e) when (e.InnerException is InvalidOperationException) { rejected = true; }
Check(rejected, "legacy coordinate loss refused without invented geometry");

using var config = JsonDocument.Parse(System.IO.File.ReadAllText("/config/ResgridConfig.json"));
var connectionString = config.RootElement.GetProperty("DataConfig.CoreConnectionString").GetString()!;
Resgrid.Config.DataConfig.CoreConnectionString = connectionString;
await using var connection = new NpgsqlConnection(connectionString);
await connection.OpenAsync();
const string citextSql = "SELECT '68009979-1321-4412-8364-631121fb802e'::citext AS \"WeatherAlertSourceId\"";
var reproduced = false;
try { await connection.QuerySingleAsync<WeatherAlertSource>(citextSql); }
catch (System.Data.DataException) { reproduced = true; }
Check(reproduced, "original citext-to-Guid source-read failure reproduced");
_ = new PostgreSqlConnectionProvider();
SqlMapper.PurgeQueryCache();
var source = await connection.QuerySingleAsync<WeatherAlertSource>(citextSql);
Check(source.WeatherAlertSourceId == Guid.Parse("68009979-1321-4412-8364-631121fb802e"), "legacy citext identifier materializes as exact Guid");
var native = await connection.QuerySingleAsync<WeatherAlertSource>("SELECT @Id::uuid AS \"WeatherAlertSourceId\"", new { Id = source.WeatherAlertSourceId });
Check(native.WeatherAlertSourceId == source.WeatherAlertSourceId, "native UUID read and Guid parameter write preserved");
rejected = false;
try { await connection.QuerySingleAsync<WeatherAlertSource>("SELECT 'not-a-guid'::citext AS \"WeatherAlertSourceId\""); }
catch (System.Data.DataException) { rejected = true; }
Check(rejected, "invalid identifier refused instead of authorizing an empty identity");
await using var transaction = await connection.BeginTransactionAsync();
await connection.ExecuteAsync("CREATE TEMP TABLE academy_guid_roundtrip (legacy_id citext, native_id uuid, value integer) ON COMMIT DROP", transaction: transaction);
var id = source.WeatherAlertSourceId;
Check(await connection.ExecuteAsync("INSERT INTO academy_guid_roundtrip VALUES (@LegacyId, @NativeId, 1)", new { LegacyId = id, NativeId = id }, transaction) == 1, "GUID parameters insert into citext and UUID columns");
Check(await connection.QuerySingleAsync<int>("SELECT value FROM academy_guid_roundtrip WHERE legacy_id = @Id", new { Id = id }, transaction) == 1, "GUID lookup matches a legacy citext identifier");
Check(await connection.QuerySingleAsync<int>("SELECT value FROM academy_guid_roundtrip WHERE native_id = @Id", new { Id = id }, transaction) == 1, "GUID lookup matches a native UUID identifier");
Check(await connection.ExecuteAsync("UPDATE academy_guid_roundtrip SET value = 2 WHERE legacy_id = @Id", new { Id = id }, transaction) == 1, "GUID update matches a legacy citext identifier");
Check(await connection.ExecuteAsync("DELETE FROM academy_guid_roundtrip WHERE legacy_id = @Id", new { Id = id }, transaction) == 1, "GUID delete matches a legacy citext identifier");
await transaction.RollbackAsync();
Console.WriteLine("16 mapping/storage checks passed; temporary writes rolled back; no persistent database mutations.");
