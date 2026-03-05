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
@TableName("excel_column_type")
public class ExcelColumnTypeEntity implements Serializable {
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
     * 数据源
     */
    @TableField(value = "vdm_catalog")
    private String vdmCatalog;

    /**
     * 库名
     */
    @TableField(value = "schema_name")
    private String schemaName;

    /**
     * 表名
     */
    @TableField(value = "table_name")
    private String tableName;

    /**
     * 列名
     */
    @TableField(value = "column_name")
    private String columnName;

    /**
     * 列注释
     */
    @TableField(value = "column_comment", updateStrategy = FieldStrategy.IGNORED)
    private String columnComment;

    /**
     * 字段类型
     */
    @TableField(value = "type")
    private String type;

    /**
     * 列序号
     */
    @TableField(value = "order_no")
    private Integer orderNo;

    /**
     * 创建时间
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
        return "ExcelColumnTypeEntity{" +
                "id=" + id +
                ", catalog='" + catalog + '\'' +
                ", schemaName='" + schemaName + '\'' +
                ", tableName='" + tableName + '\'' +
                ", columnName='" + columnName + '\'' +
                ", columnComment='" + columnComment + '\'' +
                ", type='" + type + '\'' +
                ", orderNo=" + orderNo +
                ", createTime=" + createTime +
                ", updateTime=" + updateTime +
                '}';
    }
}
