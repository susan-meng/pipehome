package com.eisoo.engine.gateway.connector.mapping;

import com.eisoo.engine.gateway.common.CatalogConstant;
import com.eisoo.engine.gateway.connector.mapping.connector.DefaultTypeMapping;

import com.eisoo.engine.gateway.connector.mapping.connector.VegaTypeMapping;
import org.springframework.stereotype.Component;

/**
 * @Author zdh
 **/
@Component
public class TypeMappingFactory {

    public TypeMapping getConnector(String connectorName) {
        switch (connectorName) {
            case CatalogConstant.CONNECTOR_VEGA:
                return new VegaTypeMapping();
            default:
                return new DefaultTypeMapping();
        }
    }
}
