package com.eisoo.engine.gateway.controller;

import com.eisoo.engine.gateway.domain.dto.DownloadDto;
import com.eisoo.engine.gateway.service.QueryService;
import com.eisoo.engine.utils.common.Constants;
import com.fasterxml.jackson.core.JsonProcessingException;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.constraints.Max;
import javax.validation.constraints.Min;

/**
 * paul.yan
 */
@Api(tags = "查询管理")
@RestController
@RequestMapping({"/api/virtual_engine_service", "/api/internal/virtual_engine_service"})
@Validated
public class FetchController {
    @Autowired(required = false)
    private QueryService queryService;

    @ApiOperation(value = "数据查询", notes = "数据查询接口")
    @PostMapping("/v1/fetch")
    public ResponseEntity<?> fetch(@Validated @RequestBody String statement,
                                   @RequestHeader(name="X-Presto-User",required = false) String user,
                                   @RequestHeader(name="x-user",required = false) String userId,
                                   @RequestHeader(name="X-Presto-Session",required = false) String xPrestoSession,
                                   @RequestParam(name="action",required = false) String action,
                                   @RequestParam(name="maxWaitResultTime",required = false)
                                       @Min(value = 1, message = "maxWaitResultTime must be greater than or equal to 1")
                                       @Max(value = 1800, message = "maxWaitResultTime must be less than or equal to 1800")
                                       Integer maxWaitResultTime,
                                   @RequestParam(name="batchSize",required = false)
                                       @Min(value = 1, message = "batchSize must be greater than or equal to 1")
                                       @Max(value = 100000, message = "batchSize must be less than or equal to 100000")
                                       Integer batchSize,
                                   @RequestParam(value = "type", required = false, defaultValue = "0") int type) throws Exception {
        if (maxWaitResultTime == null) {
            maxWaitResultTime = -1;
        }
        if (batchSize == null) {
            batchSize = -1;
        }
        return queryService.statement(statement,user,type,maxWaitResultTime,batchSize,"",action, xPrestoSession);
    }

    @ApiOperation(value = "阶段查询", notes = "流式查询接口")
    @GetMapping("/v1/statement/executing/{queryId}/{slug}/{token}")
    public ResponseEntity<?> nextFetch(@PathVariable("queryId") String queryId,
                                       @RequestHeader(name="x-user",required = false) String userId,
                                       @PathVariable("slug") String slug,
                                       @PathVariable("token") long token,
                                       @RequestParam(name="batchSize",required = false)
                                           @Min(value = 1, message = "batchSize must be greater than or equal to 1")
                                           @Max(value = 100000, message = "batchSize must be less than or equal to 100000")
                                           Integer batchSize,
                                       @RequestHeader(name="X-Presto-User",required = false) String user) throws JsonProcessingException{

        if (batchSize == null) {
            batchSize = -1;
        }
        return queryService.statement(queryId,slug,token,user,-1,-1,batchSize);
    }


    @ApiOperation(value = "样例数据查询", notes = "样例数据查询接口")
    @GetMapping("/v1/preview/{catalog}/{schema}/{table}")
    public ResponseEntity<?> fetch(@PathVariable("catalog") String catalog,
                                   @PathVariable("schema") String schema,
                                   @PathVariable("table") String table,
                                   @RequestParam(value = "columns", required = false) String columns,
                                   @RequestParam(value = "limit", required = false, defaultValue = "100") Long limit,
                                   @RequestParam(value = "type", required = false, defaultValue = "0") int type,
                                   @RequestParam(name="action",required = false) String action,
                                   @RequestHeader(name="x-user",required = false) String userId,
                                   @RequestHeader(name="X-Presto-User",required = false) String user) throws Exception {
        return queryService.statement(catalog,schema,table,columns,limit,type,user,"",action);
    }

    @ApiOperation(value = "数据下载", notes = "数据下载接口")
    @PostMapping("/v1/download")
    public ResponseEntity<?> download(@RequestHeader(name="X-Presto-User",required = false) String user,
                                      @RequestHeader(name="x-user",required = false) String userId,
                                      @RequestParam(name="action",required = false) String action,
                                      @Validated @RequestBody DownloadDto downloadDto) throws JsonProcessingException {
        return queryService.statement(downloadDto, Constants.DEFAULT_ASYNC_TASK_USER, "", action);
    }

    @ApiOperation(value = "数据分页查询", notes = "数据分页查询接口")
    @PostMapping("/v1/query")
    public ResponseEntity<?> query(@Validated @RequestBody String statement,
                                   @RequestHeader(name="X-Presto-User",required = false) String user,
                                   @RequestHeader(name="x-user",required = false) String userId,
                                   @RequestParam(name="action",required = false) String action) throws Exception {
        return queryService.statement(statement,user,"",action);
    }

}
