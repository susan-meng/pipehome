package com.eisoo.engine.gateway.controller;

import com.eisoo.engine.gateway.domain.dto.CatalogRuleDto;
import com.eisoo.engine.gateway.service.CatalogRuleService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * @Author paul
 **/
@Api(tags = "数据源下推规则管理")
@RestController
@RequestMapping("/api/virtual_engine_service")
public class CatalogRuleController {
    @Autowired(required = false)
    private CatalogRuleService catalogRuleService;

    @ApiOperation(value = "获取下推规则算子列表", notes = "算子下推规则列表接口")
    @GetMapping("/v1/rule")
    public ResponseEntity<?> getRuleList(){
        return catalogRuleService.QueryOperatorList();
    }

    @ApiOperation(value = "配置下推规则", notes = "数据源下推规则配置接口")
    @PostMapping("/v1/rule")
    public ResponseEntity<?> configRule(@Validated @RequestBody CatalogRuleDto req,@RequestHeader(name="X-Presto-User",required = false) String user){
        return catalogRuleService.configRule(req,user);
    }

    @ApiOperation(value = "获取规则算子", notes = "获取当前下推规则所有算子接口")
    @GetMapping("/v1/rule/{operator}")
    public ResponseEntity<?> getCatalogRule(@PathVariable("operator") String operator){
        return catalogRuleService.OperatorList(operator);
    }
    @ApiOperation(value = "获取所有规则", notes = "获取规则列表")
    @GetMapping("/v1/rule/all")
    public ResponseEntity<?> getCatalogRuleList(){
        return catalogRuleService.RuleList();
    }
}
