package com.eisoo.dc.gateway.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/data-connection/v1")
public class NewDataSourceController {
    
    /**
     * 新增数据源配置API
     */
    @PostMapping("/datasource/config")
    public ResponseMessage createDataSourceConfig(@RequestBody DatasourceConfigDto dto) {
        // 新增逻辑
        return ResponseMessage.success();
    }
    
    /**
     * 批量更新数据源状态
     */
    @PutMapping("/datasource/batch-status")
    public ResponseMessage batchUpdateStatus(@RequestBody BatchStatusDto dto) {
        // 新增逻辑
        return ResponseMessage.success();
    }
}
