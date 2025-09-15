using licar_wpf.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace licar_wpf.Services
{
    public class SseService : ISseService
    {
        private readonly HttpClient _httpClient;
        private CancellationTokenSource? _cancellationTokenSource;
        private const string BaseUrl = "http://localhost:8080/api/v1/notifications/subscribe";

        public event Action<Notification>? NotificationReceived;

        public SseService()
        {
            _httpClient = new HttpClient { Timeout = Timeout.InfiniteTimeSpan };
        }

        public async Task ConnectAsync(UserRole role, int userId)
        {
            Disconnect();
            _cancellationTokenSource = new CancellationTokenSource();

            var rolePath = role == UserRole.Nurse ? "nurse" : "pharmacist";
            var url = $"{BaseUrl}/{rolePath}/{userId}";

            try
            {
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                request.Headers.Accept.Add(new("text/event-stream"));

                var response = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, _cancellationTokenSource.Token);
                response.EnsureSuccessStatusCode();

                using var stream = await response.Content.ReadAsStreamAsync();
                using var reader = new StreamReader(stream);

                while (!_cancellationTokenSource.Token.IsCancellationRequested && !reader.EndOfStream)
                {
                    var line = await reader.ReadLineAsync();

                    if (string.IsNullOrWhiteSpace(line) || !line.StartsWith("data:")) continue;

                    var jsonData = line.Substring("data:".Length).Trim();
                    var notifiaction = JsonSerializer.Deserialize<Notification>(jsonData);

                    if (notifiaction != null)
                    {
                        NotificationReceived?.Invoke(notifiaction);
                    }
                }
            }
            catch (TaskCanceledException)
            {

            }
            catch (Exception ex)
            {
                Console.WriteLine($"SSE Connection error : {ex.Message}");
            }
        }

        public void Disconnect()
        {
            _cancellationTokenSource?.Cancel();
            _cancellationTokenSource?.Dispose();
            _cancellationTokenSource = null;
        }
    }
}
