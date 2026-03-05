package com.eisoo.engine.gateway.service;

import com.eisoo.engine.gateway.domain.dto.ExcelTableConfigDto;
import org.springframework.http.ResponseEntity;

import javax.servlet.http.HttpServletRequest;

public interface ExcelService {

    ResponseEntity<?> files(HttpServletRequest request, String catalog);

    ResponseEntity<?> sheet(HttpServletRequest request, String catalog, String fileName);

    ResponseEntity<?> columns(HttpServletRequest request, ExcelTableConfigDto excelTableConfigDto);

    ResponseEntity<?> createView(HttpServletRequest request, ExcelTableConfigDto excelTableConfigDto);

    ResponseEntity<?> deleteView(String catalog, String schema, String view);

}
