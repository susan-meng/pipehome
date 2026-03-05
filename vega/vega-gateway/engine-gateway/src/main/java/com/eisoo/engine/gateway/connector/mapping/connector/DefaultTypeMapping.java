package com.eisoo.engine.gateway.connector.mapping.connector;

import com.eisoo.engine.gateway.connector.TypeConfig;
import com.eisoo.engine.gateway.connector.mapping.TypeMapping;
import com.eisoo.engine.utils.util.StringUtils;
import com.google.common.collect.Maps;

import java.util.Map;

/**
 * @Author zdh
 **/
public class DefaultTypeMapping implements TypeMapping {
    @Override
    public Map<String, Long> getTypeMapping(TypeConfig targetType, Long columnSize, String connectorName) {
        Map<String, Long> type = Maps.newHashMap();
        if (targetType.getTargetType().contains("varchar")) {
            type.put(targetType.getTargetType(), columnSize);
        } else if (targetType.getTargetType().equals("decimal")) {
            type.put(targetType.getTargetType(), columnSize);
        }else if (targetType.getTargetType().contains("binary")) {
            type.put(targetType.getTargetType(), columnSize);
        } else {
            type.put(targetType.getTargetType(), null);
        }
        return type;
    }
}
