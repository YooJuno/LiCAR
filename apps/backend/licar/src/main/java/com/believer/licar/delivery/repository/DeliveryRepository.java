package com.believer.licar.delivery.repository;

import com.believer.licar.delivery.entity.Delivery;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DeliveryRepository extends JpaRepository<Delivery, Integer> {
    Optional<Delivery> findFirstByOrderByDeliveryIdDesc();
}
