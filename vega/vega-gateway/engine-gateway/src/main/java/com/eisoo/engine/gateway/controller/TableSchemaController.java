package com.eisoo.engine.gateway.controller;

import com.eisoo.engine.gateway.service.TableService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@Api(tags = "表信息管理")
@RestController
@RequestMapping("/api/virtual_engine_service")
@Validated
public class TableSchemaController {

    @Autowired(required = false)
    private TableService tableService;

    @ApiOperation(value = "查询catalog所有schema", notes = "表信息接口")
    @GetMapping("/v1/metadata/schemas/{catalog}")
    public ResponseEntity<?> getSchemasFromCatalog(@PathVariable("catalog") String catalog
            , @RequestHeader(name = "X-Presto-User", required = false) String user) {
        return tableService.CatalogSchemaList(catalog, user);
    }

    @ApiOperation(value = "查询schema下所有表", notes = "表信息接口")
    @GetMapping("/v1/metadata/tables/{catalog}/{schema}")
    public ResponseEntity<?> getTables(@PathVariable("catalog") String catalog, @PathVariable("schema") String schema
            , @RequestHeader(name = "X-Presto-User", required = false) String user) {
        return tableService.SchemaTableList(catalog, schema, user);
    }
    @ApiOperation(value = "采集schema下所有字段元数据", notes = "表信息接口")
    @GetMapping("/v1/metadata/tables/{collector}/{catalog}/{schema}")
    public ResponseEntity<?> collectTables(@PathVariable("collector") String collector, @PathVariable("catalog") String catalog, @PathVariable("schema") String schema,
                                           @RequestParam(value = "datasourceId") String datasourceId,
                                           @RequestParam(value = "schemaId") Long schemaId,
                                           @RequestParam("taskId") String taskId,
                                           @RequestHeader(name = "X-Presto-User", required = false) String user) {
        return tableService.CollectSchemaTableList(collector, catalog, schema, taskId, user, datasourceId, schemaId);
    }

    @ApiOperation(value = "查询table详情", notes = "表信息接口")
    @GetMapping("/v1/metadata/columns/{catalog}/{schema}/{table}")
    public ResponseEntity<?> getTableColumns(@PathVariable("catalog") String catalog, @PathVariable("schema") String schema, @PathVariable("table") String table
            , @RequestHeader(name = "X-Presto-User", required = false) String user) {
        return tableService.SchemaTableColumns(catalog, schema, table, user);
    }

    @ApiOperation(value = "快速查询table详情", notes = "表信息接口")
    @GetMapping("/v1/metadata/columns/fast/{catalog}/{schema}/{table}")
    public ResponseEntity<?> getTableColumnsFast(@PathVariable("catalog") String catalog, @PathVariable("schema") String schema, @PathVariable("table") String table
            , @RequestHeader(name = "X-Presto-User", required = false) String user) {
        return tableService.SchemaTableColumnsFast(catalog, schema, table, user);
    }
}
