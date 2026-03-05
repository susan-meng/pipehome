package com.eisoo.engine.gateway.enums;

import com.baomidou.mybatisplus.annotation.EnumValue;

/**
 * @Author zdh
 **/
public enum ConnectorEnums {

    CLICKHOUSE("clickhouse", "ClickHouse"),
    DORIS("doris", "Apache Doris"),
    HIVE_HADOOP2("hive-hadoop2", "Apache Hive(hadoop2)"),
    HIVE_JDBC("hive-jdbc", "Apache Hive"),
    HOLOGRES("hologres","Hologres"),
    OPENGAUSS("opengauss","OpenGauss"),
    GAUSSDB("gaussdb","GaussDB"),
    INCEPTOR("inceptor-jdbc","TDH inceptor"),
    MARIA("maria", "MariaDB"),
    MYSQL("mysql", "MySQL"),
    ORACLE("oracle", "Oracle"),
    POSTGRESQL("postgresql", "PostgreSQL"),
    SQLSERVER("sqlserver", "SQL Server"),
    MONGODB("mongodb", "MongoDB"),
    EXCEL("excel", "Excel"),
    DAMENG("dameng", "DM");

    ConnectorEnums(String connector,String mapping) {
        this.connector = connector;
        this.mapping = mapping;
    }

    @EnumValue
    private final String connector;
    private final String mapping;

    public String getConnector() {
        return connector;
    }

    public String getMapping() {
        return mapping;
    }

}
