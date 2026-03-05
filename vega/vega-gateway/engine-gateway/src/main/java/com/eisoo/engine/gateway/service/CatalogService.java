package com.eisoo.engine.gateway.service;

import com.eisoo.engine.gateway.domain.dto.CatalogDto;
import org.springframework.http.ResponseEntity;



public interface CatalogService {
    ResponseEntity<?> create(CatalogDto params);

    String showCatalogInfo(String catalogName);
}
