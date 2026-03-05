package com.eisoo.engine.gateway.controller;

import com.eisoo.engine.gateway.domain.dto.ExcelTableConfigDto;
import com.eisoo.engine.gateway.service.ExcelService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;

/**
 * @Author exx
 **/
@Api(tags = "Excel表管理")
@RestController
@RequestMapping("/api/vega-data-source/v1/excel")
@Validated
public class ExcelController {

    @Autowired(required = false)
    private ExcelService excelService;

    @ApiOperation(value = "查询Excel文件列表", notes = "查询Excel文件列表接口")
    @GetMapping("/files/{catalog}")
    public ResponseEntity<?> files(HttpServletRequest request, @PathVariable String catalog) {
        return excelService.files(request, catalog);
    }

    @ApiOperation(value = "查询Excel文件sheet列表", notes = "查询Excel文件sheet列表接口")
    @GetMapping("/sheet")
    public ResponseEntity<?> sheet(HttpServletRequest request, @Validated @RequestParam("catalog") String catalog, @RequestParam("file_name") String fileName) {
        return excelService.sheet(request, catalog, fileName);
    }

    @ApiOperation(value = "查询Excel字段列表", notes = "查询Excel字段列表接口")
    @PostMapping("/columns")
    public ResponseEntity<?> columns(HttpServletRequest request, @Validated @RequestBody ExcelTableConfigDto excelTableConfigDto) {
        return excelService.columns(request, excelTableConfigDto);
    }

    @ApiOperation(value = "新增Excel视图", notes = "新增Excel视图接口")
    @PostMapping("/view")
    public ResponseEntity<?> createView(HttpServletRequest request,
                                        @Validated @RequestBody ExcelTableConfigDto excelTableConfigDto) {
        return excelService.createView(request, excelTableConfigDto);
    }

    @ApiOperation(value = "删除Excel视图", notes = "删除Excel视图接口")
    @DeleteMapping("/view/{catalog}/{schema}/{view}")
    public ResponseEntity<?> deleteView(
            @PathVariable("catalog") String catalog,
            @PathVariable("schema") String schema, @PathVariable("view") String view) {
        return excelService.deleteView(catalog, schema, view);
    }
}
