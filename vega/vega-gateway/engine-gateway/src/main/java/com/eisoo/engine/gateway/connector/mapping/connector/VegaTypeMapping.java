package com.eisoo.engine.gateway.connector.mapping.connector;

import com.eisoo.engine.gateway.connector.TypeConfig;
import com.eisoo.engine.gateway.connector.mapping.TypeMapping;
import com.google.common.collect.Maps;

import java.util.Map;

/**
 * @Author zdh
 **/
public class VegaTypeMapping implements TypeMapping {
    @Override
    public Map<String, Long> getTypeMapping(TypeConfig targetType, Long columnSize, String connectorName) {
        Map<String, Long> type = Maps.newHashMap();
        if (targetType.getVegaType().equalsIgnoreCase("varchar")) {
            type.put(targetType.getVegaType(), columnSize);
        } else if (targetType.getVegaType().equalsIgnoreCase("decimal")) {
            type.put(targetType.getVegaType(), columnSize);
        } else {
            type.put(targetType.getVegaType(), null);
        }
        return type;
    }
}
