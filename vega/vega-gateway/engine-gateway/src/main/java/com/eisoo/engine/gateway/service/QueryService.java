package com.eisoo.engine.gateway.service;

import com.eisoo.engine.gateway.domain.dto.DownloadDto;
import com.fasterxml.jackson.core.JsonProcessingException;
import org.springframework.http.ResponseEntity;

public interface QueryService {
    ResponseEntity<?> statement(String statement,String user,int type,int maxWaitResultTime,int batchSize,String userId,String action, String xPrestoSession) throws Exception;
    ResponseEntity<?> statement(String catalog,String schema,String table,String columns,long limit,int type,String user,String userId,String action) throws Exception;

    ResponseEntity<?> statement(String queryId,String slug,long token,String user,long startTime,int maxWaitResultTime,int batchSize) throws JsonProcessingException;

    ResponseEntity<?> statement(DownloadDto downloadDto, String user, String userId, String action) throws JsonProcessingException;

    ResponseEntity<?> statement(String statement,String user,String userId,String action) throws Exception;
}
