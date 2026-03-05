package com.eisoo.engine.metadata.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.Getter;

import java.io.Serializable;
import java.time.LocalDateTime;

/*
 * @Author exx
 *
 **/
@Data
@Getter
@TableName("excel_table_config")
public class ExcelTableConfigEntity implements Serializable {
    /**
     * 唯一id，雪花算法
     */
    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;

    /**
     * 数据源
     */
    @TableField(value = "catalog")
    private String catalog;

    /**
     * vdm数据源
     */
    @TableField(value = "vdm_catalog")
    private String vdmCatalog;

    /**
     * 库名
     */
    @TableField(value = "schema_name")
    private String schemaName;

    /**
     * excel文件名
     */
    @TableField(value = "file_name", updateStrategy = FieldStrategy.IGNORED)
    private String fileName;

    /**
     * 表名
     */
    @TableField(value = "table_name")
    private String tableName;

    /**
     * 表注释
     */
    @TableField(value = "table_comment", updateStrategy = FieldStrategy.IGNORED)
    private String tableComment;

    /**
     * sheet名称
     */
    @TableField(value = "sheet", updateStrategy = FieldStrategy.IGNORED)
    private String sheet;

    /**
     * 加载所有sheet
     */
    @TableField(value = "all_sheet")
    private boolean allSheet;

    /**
     * 把sheet作为一列
     */
    @TableField(value = "sheet_as_new_column")
    private boolean sheetAsNewColumn;

    /**
     * 起始单元格
     */
    @TableField(value = "start_cell", updateStrategy = FieldStrategy.IGNORED)
    private String startCell;

    /**
     * 结束单元格
     */
    @TableField(value = "end_cell", updateStrategy = FieldStrategy.IGNORED)
    private String endCell;

    /**
     * 结束单元格
     */
    @TableField(value = "has_headers")
    private boolean hasHeaders;

    /**
     * 创建时间，默认当前时间
     */
    @TableField(value = "create_time")
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;

    /**
     * 修改时间，默认当前时间
     */
    @TableField(value = "update_time")
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;

    @Override
    public String toString() {
        return "ExcelTableConfigEntity{" +
                "id=" + id +
                ", catalog='" + catalog + '\'' +
                ", vdmCatalog='" + vdmCatalog + '\'' +
                ", schemaName='" + schemaName + '\'' +
                ", fileName='" + fileName + '\'' +
                ", tableName='" + tableName + '\'' +
                ", tableComment='" + tableComment + '\'' +
                ", sheet='" + sheet + '\'' +
                ", allSheet=" + allSheet +
                ", sheetAsNewColumn=" + sheetAsNewColumn +
                ", startCell='" + startCell + '\'' +
                ", endCell='" + endCell + '\'' +
                ", hasHeaders=" + hasHeaders +
                ", createTime=" + createTime +
                ", updateTime=" + updateTime +
                '}';
    }
}
