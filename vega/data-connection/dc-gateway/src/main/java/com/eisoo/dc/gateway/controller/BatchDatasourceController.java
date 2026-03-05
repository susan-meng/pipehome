package com.eisoo.dc.gateway.controller;

import org.springframework.web.bind.annotation.*;
import com.eisoo.dc.gateway.domain.vo.HttpResInfo;
import java.util.List;

/**
 * 批量数据源管理控制器
 * 用于批量操作数据源
 */
@RestController
@RequestMapping("/api/data-connection/v1/datasource")
public class BatchDatasourceController {

    /**
     * 批量删除数据源
     */
    @PostMapping("/batch-delete")
    public HttpResInfo batchDeleteDatasources(@RequestBody BatchDeleteRequest request) {
        // 批量删除逻辑
        return HttpResInfo.success();
    }

    /**
     * 批量启用/禁用数据源
     */
    @PostMapping("/batch-status")
    public HttpResInfo batchUpdateStatus(@RequestBody BatchStatusRequest request) {
        // 批量状态更新逻辑
        return HttpResInfo.success();
    }

    /**
     * 批量测试数据源连接
     */
    @PostMapping("/batch-test")
    public HttpResInfo batchTestConnection(@RequestBody BatchTestRequest request) {
        // 批量测试连接逻辑
        return HttpResInfo.success();
    }
}

class BatchDeleteRequest {
    private List<Long> ids;
    private Boolean forceDelete;  // 是否强制删除
    private String reason;        // 删除原因
    // getters and setters
}

class BatchStatusRequest {
    private List<Long> ids;
    private String status;  // ENABLED / DISABLED
    // getters and setters
}

class BatchTestRequest {
    private List<Long> ids;
    private Integer timeout;  // 超时时间(秒)
    // getters and setters
}
