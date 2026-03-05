package com.eisoo.engine.gateway.connector.mapping;

import com.eisoo.engine.gateway.connector.TypeConfig;

import java.util.Map;

public interface TypeMapping {

    Map<String,Long> getTypeMapping(TypeConfig config, Long columnSize, String connectorName);
}

