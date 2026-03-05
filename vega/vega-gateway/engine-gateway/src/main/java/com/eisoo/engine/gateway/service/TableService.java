package com.eisoo.engine.gateway.service;

import org.springframework.http.ResponseEntity;

public interface TableService {

    ResponseEntity<?> CatalogSchemaList(String catalog,String user);

    ResponseEntity<?> SchemaTableList(String catalog, String schema,String user);

    ResponseEntity<?> CollectSchemaTableList(String collector, String catalog, String schema, String taskId,String user, String datasourceId, Long schemaId);

    ResponseEntity<?> SchemaTableColumns(String catalog, String schema,String tables,String user);

    ResponseEntity<?> SchemaTableColumnsFast(String catalog, String schema, String table, String user);
}
