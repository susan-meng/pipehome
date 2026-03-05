package com.eisoo.engine.gateway.domain.dto;

import lombok.Data;

@Data
public class CatalogNode {
    private String catalogName;
    private String pushdownRule;
    private String isEnabled;
}
