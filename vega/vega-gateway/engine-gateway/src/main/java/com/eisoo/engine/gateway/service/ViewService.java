package com.eisoo.engine.gateway.service;

import com.eisoo.engine.gateway.domain.dto.ViewDto;
import org.springframework.http.ResponseEntity;

public interface ViewService {

    ResponseEntity<?> createView(ViewDto params, String user, boolean allowCreateExcelView);

    ResponseEntity<?> viewList(Long pageNum,Long pageSize,String catalogName,String schemaName,String viewName);

    ResponseEntity<?> replaceView(ViewDto params,String user);

    ResponseEntity<?> deleteView(ViewDto params,String user, boolean allowCreateExcelView);

}
