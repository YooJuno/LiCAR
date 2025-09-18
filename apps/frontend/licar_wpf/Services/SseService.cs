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
    public class SseService
    {
        private HttpClient _httpClient;
        private CancellationTokenSource _cancellationTokenSource;

        public event Action<string> DeliveryRequested;
        public event Action<string> DeliveryCompleted;

        public async Task ConnectAsync(UserRole role, int id)
        {
            if (_cancellationTokenSource != null)
            {
                Disconnect();
            }

            _cancellationTokenSource = new CancellationTokenSource();
            _httpClient = new HttpClient { Timeout = Timeout.InfiniteTimeSpan };

            var rolePath = role == UserRole.Nurse ? "nurse" : "pharmacist";
            var requestUrl = $"http://localhost:8080/api/v1/notifications/subscribe/{rolePath}/{id}";

            try
            {
                var response = await _httpClient.GetAsync(requestUrl, HttpCompletionOption.ResponseHeadersRead, _cancellationTokenSource.Token);
                response.EnsureSuccessStatusCode();

                using (var stream = await response.Content.ReadAsStreamAsync())
                using (var reader = new StreamReader(stream))
                {
                    while (!reader.EndOfStream && !_cancellationTokenSource.IsCancellationRequested)
                    {
                        var line = await reader.ReadLineAsync();
                        if (string.IsNullOrWhiteSpace(line)) continue;

                        if (line.StartsWith("event:"))
                        {
                            var eventType = line.Substring("event:".Length).Trim();
                            var dataLine = await reader.ReadLineAsync();
                            var data = dataLine.Substring("data:".Length).Trim();

                            if (eventType == "deliveryRequest")
                            {
                                DeliveryRequested?.Invoke(data);
                            }
                            else if (eventType == "deliveryComplete")
                            {
                                DeliveryCompleted?.Invoke(data);
                            }
                        }
                    }
                }
            }
            catch (TaskCanceledException)
            {
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }
        
        public void Disconnect()
        {
            if (_cancellationTokenSource != null)
            {
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource?.Dispose();
                _cancellationTokenSource = null;
            }
            if (_httpClient != null)
            {
                _httpClient.Dispose();
                _httpClient = null;
            }
        }
    }
}
