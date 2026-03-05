package com.eisoo.engine.gateway.service.impl;

import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.eisoo.engine.gateway.common.CatalogConstant;
import com.eisoo.engine.gateway.domain.dto.ExcelTableConfigDto;
import com.eisoo.engine.gateway.service.CatalogService;
import com.eisoo.engine.gateway.service.ExcelService;
import com.eisoo.engine.gateway.service.ViewService;
import com.eisoo.engine.gateway.util.ASUtil;
import com.eisoo.engine.gateway.util.CheckUtil;
import com.eisoo.engine.gateway.util.CommonUtil;
import com.eisoo.engine.gateway.util.ExcelUtil;
import com.eisoo.engine.metadata.entity.ExcelColumnTypeEntity;
import com.eisoo.engine.metadata.entity.ExcelTableConfigEntity;
import com.eisoo.engine.metadata.mapper.ExcelColumnTypeMapper;
import com.eisoo.engine.metadata.mapper.ExcelTableConfigMapper;
import com.eisoo.engine.utils.common.Detail;
import com.eisoo.engine.utils.common.Message;
import com.eisoo.engine.utils.enums.ErrorCodeEnum;
import com.eisoo.engine.utils.exception.AiShuException;
import com.eisoo.engine.utils.util.TokenUtil;
import com.monitorjbl.xlsx.StreamingReader;
import com.monitorjbl.xlsx.exceptions.MissingSheetException;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.servlet.http.HttpServletRequest;
import java.io.InputStream;
import java.net.URLDecoder;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.apache.poi.ss.usermodel.CellType.STRING;

/**
 * @Author exx
 **/
@Service
public class ExcelServiceImpl implements ExcelService {

    private static final Logger log = LoggerFactory.getLogger(ExcelServiceImpl.class);

    private static final String SCHEMA_DEFAULT = "default";
    private static final String CELL_PATTERN_REG = "^[A-Z]+[1-9][0-9]*$";
    private static final Pattern CELL_PATTERN = Pattern.compile(CELL_PATTERN_REG);
    private static final String[] COLUMN_TYPE = {"bigint", "varchar", "timestamp", "boolean", "double"};

    @Autowired(required = false)
    CatalogService catalogService;

    @Autowired(required = false)
    ViewService viewService;

    @Autowired(required = false)
    ASUtil asUtil;

    @Autowired(required = false)
    ExcelUtil excelUtil;

    @Autowired(required = false)
    ExcelTableConfigMapper excelTableConfigMapper;

    @Autowired(required = false)
    ExcelColumnTypeMapper excelColumnTypeMapper;


    @Value(value = "${services.efast-public}")
    private String efastPublic;

    @Override
    public ResponseEntity<?> files(HttpServletRequest request, String catalog) {
        JSONObject files = getFiles(TokenUtil.getBearerToken(request), catalog);
        JSONObject filesJSONObject = files.getJSONObject("data");
        JSONArray data = new JSONArray();
        data.addAll(filesJSONObject.keySet());
        JSONObject result = new JSONObject();
        result.put("data", data);
        result.put("total", files.getIntValue("total"));
        return ResponseEntity.ok(result);
    }

    public JSONObject getFiles(String token, String catalog) {
        String catalogStr = CheckUtil.checkCatalog(catalogService, catalog);
        JSONObject catalogJson = JSONObject.parseObject(catalogStr);
        if (!catalogJson.getString("connector.name").equals(CatalogConstant.EXCEL_CATALOG)
                && !catalogJson.containsKey("excel.password")) {
            log.error("数据源类型错误:{}", catalogJson.getString("connector.name"));
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, String.format(Detail.CATALOG_TYPE_ERROR, catalogJson.getString("connector.name")));
        }
        String base = catalogJson.getString("excel.base");
        String protocol = catalogJson.getString("excel.protocol");
        String url = "";
        String path = "";
        if (protocol.equals(CatalogConstant.STORAGE_PROTOCOL_DOCLIB)){
            url = efastPublic;
            path = ASUtil.getItemPath(url, token, base);
        }else{
            String host = catalogJson.getString("excel.host");
            String port = catalogJson.getString("excel.port");
            String username = catalogJson.getString("excel.username");
            String password = catalogJson.getString("excel.password");
            url = CommonUtil.getUrl("https", host, port);
            token =  ASUtil.getToken(host, port, username, password);
            path = base;
        }

        String catalogFileName = null;
        if (excelUtil.isExcelFile(path)) {
            catalogFileName = path.substring(path.lastIndexOf("/") + 1);
            base = base.substring(0, base.lastIndexOf("/"));
        }
        String docId = "";
        if (protocol.equals(CatalogConstant.STORAGE_PROTOCOL_DOCLIB)){
            docId = base;
        }else{
            docId = ASUtil.getDocid(url, token, base);
        }
        JSONObject dirJson = ASUtil.loadDir(url, token, docId);
        JSONArray files = dirJson.getJSONArray("files");

        JSONObject result = new JSONObject();
        JSONObject data = new JSONObject();
        int total = 0;
        for (int i = 0; i < files.size(); i++) {
            JSONObject file = files.getJSONObject(i);
            String docid = file.getString("docid");
            String fileName = file.getString("name");
            if (excelUtil.isExcelFile(fileName) && (StringUtils.isEmpty(catalogFileName) || fileName.equals(catalogFileName))) {
                data.put(fileName,docid);
                total++;
            }
        }
        result.put("data", data);
        result.put("total", total);
        return result;
    }

    @Override
    public ResponseEntity<?> sheet(HttpServletRequest request, String catalog, String fileName) {
        fileName = decodeFileName(fileName);
        String token = TokenUtil.getBearerToken(request);
        String docid = checkFileName(token, catalog, fileName);
        String catalogStr = CheckUtil.checkCatalog(catalogService, catalog);
        JSONObject catalogJson = JSONObject.parseObject(catalogStr);
        String protocol = catalogJson.getString("excel.protocol");
        String url = "";
        if (protocol.equals(CatalogConstant.STORAGE_PROTOCOL_DOCLIB)){
            url = efastPublic;
        }else{
            String host = catalogJson.getString("excel.host");
            String port = catalogJson.getString("excel.port");
            String username = catalogJson.getString("excel.username");
            String password = catalogJson.getString("excel.password");
            url = CommonUtil.getUrl("https", host, port);
            token =  ASUtil.getToken(host, port, username, password);
        }

        JSONObject result = new JSONObject();
        JSONArray data = new JSONArray();
        result.put("data", data);

        try {
            InputStream inputStream = ASUtil.getInputStream(url, token, docid);
            Workbook workbook = StreamingReader.builder().bufferSize(4096).open(inputStream);
            Iterator<Sheet> it = workbook.sheetIterator();
            while (it.hasNext()) {
                data.add(it.next().getSheetName());
            }
            result.put("total", workbook.getNumberOfSheets());
        } catch (AiShuException aiShuException) {
            throw aiShuException;
        } catch (Exception e) {
            log.error("excel sheet error", e);
            throw new AiShuException(ErrorCodeEnum.ReadExcelFail, String.format(Detail.READ_FILE_ERROR, fileName), Message.MESSAGE_DATANOTEXIST_ERROR_SOLUTION);
        }
        return ResponseEntity.ok(result);
    }

    @Override
    public ResponseEntity<?> columns(HttpServletRequest request, ExcelTableConfigDto excelTableConfigDto) {
        String token = TokenUtil.getBearerToken(request);
        String docid = checkFileName(token, excelTableConfigDto.getCatalog(), excelTableConfigDto.getFileName());
        String catalogStr = CheckUtil.checkCatalog(catalogService, excelTableConfigDto.getCatalog());
        JSONObject catalogJson = JSONObject.parseObject(catalogStr);
        String protocol = catalogJson.getString("excel.protocol");
        String url = "";
        if (protocol.equals(CatalogConstant.STORAGE_PROTOCOL_DOCLIB)){
            url = efastPublic;
        }else{
            String host = catalogJson.getString("excel.host");
            String port = catalogJson.getString("excel.port");
            String username = catalogJson.getString("excel.username");
            String password = catalogJson.getString("excel.password");
            url = CommonUtil.getUrl("https", host, port);
            token =  ASUtil.getToken(host, port, username, password);
        }

        JSONObject result = new JSONObject();
        JSONArray data = new JSONArray();
        result.put("data", data);

        try {
            InputStream inputStream = ASUtil.getInputStream(url, token, docid);
            Workbook workbook = new XSSFWorkbook(inputStream);
            Sheet sheet;
            if (StringUtils.isEmpty(excelTableConfigDto.getSheet()) || excelTableConfigDto.isAllSheet()) {
                sheet = workbook.getSheetAt(0);
            } else {
                String sheetName = excelTableConfigDto.getSheet().split(",")[0];
                sheet = workbook.getSheet(sheetName);
                if (sheet == null) {
                    throw new AiShuException(ErrorCodeEnum.SheetNotExist, String.format(Detail.READ_SHEET_ERROR, sheetName), Message.MESSAGE_DATANOTEXIST_ERROR_SOLUTION);
                }
            }

            int[][] rowCells = checkCellRange(excelTableConfigDto);
            int[] startRowCol = rowCells[0];
            int[] endRowCol = rowCells[1];

            boolean sheetNameExist = false;
            // sheet.getRow() is not supported in excel-streaming-reader
            Row row = sheet.getRow(startRowCol[0] - 1);
            Row dataRow;
            if (excelTableConfigDto.isHasHeaders()){
                dataRow = sheet.getRow(startRowCol[0]);
            }else{
                dataRow = row;
            }
            int number = 1;
            if (row != null && excelTableConfigDto.isHasHeaders()) {
                for (int i = startRowCol[1] - 1; i < endRowCol[1]; i++) {
                    Cell cell = row.getCell(i);
                    JSONObject columnJson = new JSONObject();
                    if (cell == null || cell.getCellType() != STRING) {
                        columnJson.put("column", "column_" + number++);
                    }else{
                        columnJson.put("column", cell.getStringCellValue());
                        if (Objects.equals(cell.getStringCellValue(), "sheet_name")){
                            sheetNameExist = true;
                        }
                    }
                    Cell dataCell = dataRow!=null?dataRow.getCell(i):null;
                    columnJson.put("type", excelUtil.guessColumnType(dataCell, workbook));
                    data.add(columnJson);
                }
            } else {
                for (int i = startRowCol[1] - 1; i < endRowCol[1]; i++) {
                    JSONObject columnJson = new JSONObject();
                    columnJson.put("column", "column_" + number++);
                    Cell dataCell = dataRow!=null?dataRow.getCell(i):null;
                    columnJson.put("type", excelUtil.guessColumnType(dataCell, workbook));
                    data.add(columnJson);
                }
            }

            if (excelTableConfigDto.isSheetAsNewColumn()) {
                String sheetName = "sheet_name";
                if (sheetNameExist) {
                    sheetName += "_1";
                }
                JSONObject columnJson = new JSONObject();
                columnJson.put("column", sheetName);
                columnJson.put("type", "varchar");
                data.add(columnJson);
            }

            result.put("total", data.size());
        } catch (AiShuException aiShuException) {
            throw aiShuException;
        }  catch (MissingSheetException e) {
            throw new AiShuException(ErrorCodeEnum.SheetNotExist, String.format(Detail.READ_SHEET_ERROR, e.getMessage()), Message.MESSAGE_DATANOTEXIST_ERROR_SOLUTION);
        } catch (Exception e) {
            log.error("excel sheet log column --> filename{}", excelTableConfigDto.getFileName());
            throw new AiShuException(ErrorCodeEnum.ReadExcelFail, String.format(Detail.READ_FILE_ERROR, excelTableConfigDto.getFileName()), Message.MESSAGE_DATANOTEXIST_ERROR_SOLUTION);
        }
        return ResponseEntity.ok(result);
    }

    @Override
    public ResponseEntity<?> createView(HttpServletRequest request, ExcelTableConfigDto excelTableConfigDto) {
        // 去掉参数首尾空格
        CheckUtil.excelTableConfigDtoTrim(excelTableConfigDto);
        if (StringUtils.isEmpty(excelTableConfigDto.getTableName())) {
            log.error("tableName不能为空");
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.TABLE_NAME_NOT_NULL);
        }
        List<ExcelTableConfigEntity> tableConfigList = selectTableConfig(excelTableConfigDto.getVdmCatalog(), SCHEMA_DEFAULT, excelTableConfigDto.getTableName());
        if (tableConfigList != null && tableConfigList.size() > 0) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.TABLE_NAME_EXIST);
        }
        // excel表不再与视图同时创建
//        CheckUtil.checkVdmCatalog(catalogService, excelTableConfigDto.getVdmCatalog());
        checkTableConfig(request, excelTableConfigDto);
        createTable(excelTableConfigDto);

//        ViewDto viewDto = new ViewDto();
        String tableName = excelTableConfigDto.getCatalog() + "." + SCHEMA_DEFAULT + "." + excelTableConfigDto.getTableName();
//        viewDto.setCatalogName(excelTableConfigDto.getVdmCatalog() + "." + SCHEMA_DEFAULT);
//        viewDto.setViewName(excelTableConfigDto.getTableName());
//        viewDto.setQuery("select * from " + tableName);
//        viewService.createView(viewDto, "admin", true);

        JSONObject obj = new JSONObject();
        obj.put("tableName", tableName);
//        obj.put("viewName", excelTableConfigDto.getVdmCatalog() + "." + SCHEMA_DEFAULT + "." + excelTableConfigDto.getTableName());
        return ResponseEntity.ok(obj);
    }

    @Override
    @Transactional
    public ResponseEntity<?> deleteView(String catalog, String schema, String view) {
//        CheckUtil.checkVdmCatalog(catalogService, vdmCatalog);
        List<ExcelTableConfigEntity> tableConfigList = selectTableConfig(catalog, schema, view);
        if (tableConfigList == null || tableConfigList.size() == 0) {
            throw new AiShuException(ErrorCodeEnum.TableNotExist, catalog + "." + schema + "." + view, Message.MESSAGE_DATANOTEXIST_ERROR_SOLUTION);
        }

        deleteTable(catalog, schema, view);

//        ViewDto viewDto = new ViewDto();
//        viewDto.setCatalogName(vdmCatalog + "." + schema);
//        viewDto.setViewName(view);
//        ResponseEntity<?> del = viewService.deleteView(viewDto, "admin", true);
//        log.info("删除视图:{}", del.toString());

        JSONObject result = new JSONObject();
        result.put("tableName", catalog + "." + schema + "." + view);
        return ResponseEntity.ok(result);
    }

    public String decodeFileName(String fileName) {
        try {
            return URLDecoder.decode(fileName, "UTF-8");
        } catch (Exception e) {
            log.warn("decode fileName error: {}", fileName);
        }
        return fileName;
    }

    public List<ExcelTableConfigEntity> selectTableConfig(String catalog, String schema, String tableName) {
        QueryWrapper<ExcelTableConfigEntity> wrapper = new QueryWrapper<>();
        wrapper.eq("catalog", catalog)
                .eq("schema_name", schema)
                .eq("table_name", tableName);
        List<ExcelTableConfigEntity> list = excelTableConfigMapper.selectList(wrapper);
        return list;
    }

    @Transactional
    public void deleteTable(String catalog, String schema, String tableName) {
        QueryWrapper<ExcelTableConfigEntity> tableWrapper = new QueryWrapper<>();
        tableWrapper.eq("catalog", catalog)
                .eq("schema_name", schema)
                .eq("table_name", tableName);
        excelTableConfigMapper.delete(tableWrapper);

        QueryWrapper<ExcelColumnTypeEntity> columnWrapper = new QueryWrapper<>();
        columnWrapper.eq("catalog", catalog)
                .eq("schema_name", schema)
                .eq("table_name", tableName);
        excelColumnTypeMapper.delete(columnWrapper);

        log.info("删除Excel表成功:{}", catalog + "." + schema + "." + tableName);
    }

    @Transactional
    public void createTable(ExcelTableConfigDto excelTableConfigDto) {
        ExcelTableConfigEntity entity = new ExcelTableConfigEntity();
        entity.setCatalog(excelTableConfigDto.getCatalog());
//        entity.setVdmCatalog(excelTableConfigDto.getVdmCatalog());
        entity.setSchemaName(SCHEMA_DEFAULT);
        entity.setFileName(excelTableConfigDto.getFileName());
        entity.setTableName(excelTableConfigDto.getTableName());
        entity.setSheet(excelTableConfigDto.getSheet());
        entity.setAllSheet(excelTableConfigDto.isAllSheet());
        entity.setSheetAsNewColumn(excelTableConfigDto.isSheetAsNewColumn());
        entity.setStartCell(excelTableConfigDto.getStartCell());
        entity.setEndCell(excelTableConfigDto.getEndCell());
        entity.setHasHeaders(excelTableConfigDto.isHasHeaders());
        excelTableConfigMapper.insert(entity);

        for (int i = 0; i < excelTableConfigDto.getColumns().size(); i++) {
            ExcelColumnTypeEntity columnTypeEntity = new ExcelColumnTypeEntity();
            columnTypeEntity.setCatalog(excelTableConfigDto.getCatalog());
//            columnTypeEntity.setVdmCatalog(excelTableConfigDto.getVdmCatalog());
            columnTypeEntity.setSchemaName(SCHEMA_DEFAULT);
            columnTypeEntity.setTableName(excelTableConfigDto.getTableName());
            columnTypeEntity.setColumnName(excelTableConfigDto.getColumns().get(i).getColumn());
            columnTypeEntity.setType(excelTableConfigDto.getColumns().get(i).getType());
            columnTypeEntity.setOrderNo(i);
            excelColumnTypeMapper.insert(columnTypeEntity);
        }

        log.info("创建Excel视图成功:" + entity);
    }

    public String checkFileName(String token, String catalog, String fileName) {
        if (!excelUtil.isExcelFile(fileName)) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, String.format(Detail.FILE_TYPE_ERROR, fileName));
        }
        JSONObject filesResponseEntity = getFiles(token, catalog);
        JSONObject files = filesResponseEntity.getJSONObject("data");
        String docid = files.getString(fileName);
        if (StringUtils.isEmpty(docid)) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, String.format(Detail.FILE_NOT_EXIST, fileName));
        }
        return docid;
    }

    public int[][] checkCellRange(ExcelTableConfigDto excelTableConfigDto) {
        Matcher matcher = CELL_PATTERN.matcher(excelTableConfigDto.getStartCell());
        if (!matcher.matches()) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.START_CELL_ERROR);
        }

        matcher = CELL_PATTERN.matcher(excelTableConfigDto.getEndCell());
        if (!matcher.matches()) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.END_CELL_ERROR);
        }

        int[] startRowCol = excelTableConfigDto.getRowAndCloumnIndex(excelTableConfigDto.getStartCell());
        if (startRowCol[0] > 1048576 || startRowCol[1] > 16384) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.START_CELL_RANGE_ERROR, Message.MESSAGE_CELL_RANGE_SOLUTION);
        }
        int[] endRowCol = excelTableConfigDto.getRowAndCloumnIndex(excelTableConfigDto.getEndCell());
        if (endRowCol[0] > 1048576 || endRowCol[1] > 16384) {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.END_CELL_RANGE_ERROR, Message.MESSAGE_CELL_RANGE_SOLUTION);
        }

        if (endRowCol[0] < startRowCol[0] || endRowCol[1] < startRowCol[1]){
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.CELL_RANGE_ERROR);
        }

        return new int[][]{startRowCol, endRowCol};
    }

    public void checkTableConfig(HttpServletRequest request, ExcelTableConfigDto excelTableConfigDto) {
        CheckUtil.checkCatalog(catalogService, excelTableConfigDto.getCatalog());

        checkFileName(TokenUtil.getBearerToken(request), excelTableConfigDto.getCatalog(), excelTableConfigDto.getFileName());

        if (StringUtils.isNotEmpty(excelTableConfigDto.getTableName())
                && !CheckUtil.checkViewName(excelTableConfigDto.getTableName())) {
                throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.TABLE_NAME_ERROR, Message.MESSAGE_VIEW_NAME_SOLUTION);
        }

        if (StringUtils.isNotEmpty(excelTableConfigDto.getSheet())) {
            String[] sheetParams = excelTableConfigDto.getSheet().split(",");
            ResponseEntity<?> sheetResponseEntity = sheet(request, excelTableConfigDto.getCatalog(), excelTableConfigDto.getFileName());
            JSONArray sheetArr = JSONObject.parseObject(sheetResponseEntity.getBody().toString()).getJSONArray("data");
            for (String sheetParam : sheetParams) {
                if (!sheetArr.stream().anyMatch(sheetParam::equals)) {
                    throw new AiShuException(ErrorCodeEnum.SheetNotExist, String.format(Detail.READ_SHEET_ERROR, excelTableConfigDto.getFileName()), Message.MESSAGE_DATANOTEXIST_ERROR_SOLUTION);
                }
            }
        }

        int[][] rowCells = checkCellRange(excelTableConfigDto);
        int[] startRowCol = rowCells[0];
        int[] endRowCol = rowCells[1];

        if (excelTableConfigDto.getColumns() != null && excelTableConfigDto.getColumns().size() > 0) {
            int colCount;
            colCount = endRowCol[1] - startRowCol[1] + 1;
            if (excelTableConfigDto.isSheetAsNewColumn()){
                colCount += 1;
            }
            if (excelTableConfigDto.getColumns().size() != colCount) {
                throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.CELL_RANGE_AND_COLUMNS_INCONSISTENT);
            }

            Set<String> columnNameSet = new HashSet<>();
            for (ExcelTableConfigDto.ColumnType columnType : excelTableConfigDto.getColumns()) {
                if (StringUtils.isEmpty(columnType.getColumn())) {
                    throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.COLUMN_NOT_NULL);
                } else {
                    if (!CheckUtil.checkExcelColumnName(columnType.getColumn())) {
                        throw new AiShuException(ErrorCodeEnum.InvalidParameter, columnType.getColumn() + ":" + Detail.COLUMN_NAME_FORMAT_ERROR, Message.MESSAGE_COLUMN_NAME_SOLUTION);
                    }
                }

                if (columnNameSet.contains(columnType.getColumn().toLowerCase())) {
                    throw new AiShuException(ErrorCodeEnum.InvalidParameter, String.format(Detail.COLUMN_NAME_ERROR, columnType.getColumn()));
                } else {
                    columnNameSet.add(columnType.getColumn().toLowerCase());
                }

                if (StringUtils.isEmpty(columnType.getType())) {
                    throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.COLUMN_TYPE_NOT_NULL);
                } else {
                    columnType.setType(columnType.getType().toLowerCase());
                    if (!ArrayUtils.contains(COLUMN_TYPE, columnType.getType())) {
                        throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.COLUMN_TYPE_UNSUPPORTED, Message.MESSAGE_COLUMN_TYPE_SOLUTION);
                    }
                }
            }
            columnNameSet.clear();
        } else {
            throw new AiShuException(ErrorCodeEnum.InvalidParameter, Detail.COLUMN_TYPE_NOT_NULL);
        }

    }
}
