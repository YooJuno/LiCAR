package com.believer.licar.notification.service;

import com.believer.licar.notification.dto.NotificationCompleteResponse;
import com.believer.licar.notification.dto.NotificationRequestResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotificationService {

    private final Map<Integer, SseEmitter> pharmacistEmitters = new ConcurrentHashMap<>();
    private final Map<Integer, SseEmitter> nurseEmitters = new ConcurrentHashMap<>();
    private static final Long DEFAULT_TIMEOUT = 60 * 60 * 1000L;

    public SseEmitter subscribePharmacist(Integer pharmacistId) {
        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT);
        pharmacistEmitters.put(pharmacistId, emitter);

        emitter.onCompletion(() -> pharmacistEmitters.remove(pharmacistId));
        emitter.onTimeout(() -> pharmacistEmitters.remove(pharmacistId));
        emitter.onError((e) -> pharmacistEmitters.remove(pharmacistId));

        sendToClient(emitter, "connect", "Connection successful. [pharmacist = " + pharmacistId + " ]");

        return emitter;
    }

    public SseEmitter subscribeNurse(Integer nurseId) {
        SseEmitter emitter = new SseEmitter(DEFAULT_TIMEOUT);
        nurseEmitters.put(nurseId, emitter);

        emitter.onCompletion(() -> nurseEmitters.remove(nurseId));
        emitter.onTimeout(() -> nurseEmitters.remove(nurseId));
        emitter.onError((e) -> nurseEmitters.remove(nurseId));

        sendToClient(emitter, "connect", "Connection successful. [nurse = " + nurseId + " ]");

        return emitter;
    }

    public void sendToPharmacist(Integer pharmacistId, NotificationRequestResponse notification) {
        SseEmitter emitter = pharmacistEmitters.get(pharmacistId);

        if (emitter != null) {
            sendToClient(emitter, "deliveryRequest", notification);
        }
    }

    public void setToNurse(Integer nurseId, NotificationCompleteResponse notification) {
        SseEmitter emitter = nurseEmitters.get(nurseId);

        if (emitter != null) {
            sendToClient(emitter, "deliveryComplete", notification);
        }
    }

    public void sendToClient(SseEmitter emitter, String eventName, Object data) {
        try {
            emitter.send(SseEmitter.event()
                    .name(eventName)
                    .data(data));
        } catch (IOException e) {
            log.error("SSE connection error : {}", e.getMessage());

            emitter.completeWithError(e);
        }
    }
}
