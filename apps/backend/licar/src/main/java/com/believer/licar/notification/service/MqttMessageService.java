package com.believer.licar.notification.service;

import com.believer.licar.global.config.MqttConfig;
import com.believer.licar.transport.dto.RobotTransportInfoResponse;
import com.believer.licar.transport.service.TransportService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.integration.annotation.ServiceActivators;
import org.springframework.integration.mqtt.support.MqttHeaders;
import org.springframework.messaging.Message;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class MqttMessageService {

    private final TransportService transportService;
    private final MqttConfig.MqttGateway mqttGateway;
    private final ObjectMapper objectMapper;

    @ServiceActivator(inputChannel = "mqttInputChannel")
    public void handleMessage(Message<String> message) {
        Map<String, Object> headers = message.getHeaders();
        String payload = message.getPayload();

        String topic = (String) headers.get(MqttHeaders.RECEIVED_TOPIC);
        log.info("Received MQTT message on topic [{}]: {}", topic, payload);

        try {
            int robotId = Integer.parseInt(topic.substring(topic.lastIndexOf('/') + 1));

            RobotTransportInfoResponse responseDto = transportService.getLatestTransportDetailsForRobot(robotId);
            String jsonResponse = objectMapper.writeValueAsString(responseDto);
            String responseTopic = "robots/response/" + robotId;

            mqttGateway.sendToMqtt(jsonResponse, responseTopic);
            log.info("Sent MQTT response to topic [{}]: {}", responseTopic, jsonResponse);
        } catch (NumberFormatException e) {
            log.error("Failed to parse robotId from topic: {}", topic);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize response DTO to JSON", e);
        } catch (Exception e) {
            log.error("Error processing MQTT message: {}", e.getMessage());
        }
    }
}
