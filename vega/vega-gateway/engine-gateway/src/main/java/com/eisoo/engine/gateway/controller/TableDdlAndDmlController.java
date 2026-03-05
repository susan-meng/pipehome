package com.eisoo.engine.gateway.controller;

import com.eisoo.engine.gateway.service.TableDdlAndDmlService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * @Author zdh
 **/
@Api(tags = "虚拟化引擎创建表、插入数据、清空数据管理")
@RestController
@RequestMapping("/api/virtual_engine_service/v1/table")
public class TableDdlAndDmlController {


    @Autowired(required = false)
    TableDdlAndDmlService tableDdlAndDmlService;


    @ApiOperation(value = "create", notes = "虚拟化引擎创建表接口")
    @PostMapping("create")
    public ResponseEntity<?> create(String statement, @RequestHeader(name="X-Presto-User",required = false) String user){
        return tableDdlAndDmlService.createTableSql(statement,user);
    }

    @ApiOperation(value = "insert", notes = "虚拟化引擎插入数据接口")
    @PostMapping("insert")
    public ResponseEntity<?> insert(String statement, @RequestHeader(name="X-Presto-User",required = false) String user){
        return tableDdlAndDmlService.insertTableSql(statement,user);
    }
    @ApiOperation(value = "truncate", notes = "虚拟化引擎清空数据接口")
    @PostMapping("truncate")
    public ResponseEntity<?> truncate(String statement, @RequestHeader(name="X-Presto-User",required = false) String user){
        return tableDdlAndDmlService.truncateTableSql(statement,user);
    }

}
