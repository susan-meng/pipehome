package com.eisoo.engine.gateway.domain.vo;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

/**
 * table schema json domain
 */
public class SchemaTables {
    private List<Data> data;
    private int total_count;

    public List<Data> getData() {
        return data;
    }

    public void setData(List<Data> data) {
        this.data = data;
    }

    public int getTotal_count() {
        return total_count;
    }

    public void setTotal_count(int total_count) {
        this.total_count = total_count;
    }

    public static class Data {
        private String catalog;
        private String schema;
        private String table;

        private String comment;
        private String fqn;
        @JsonProperty(value = "tableType")
        private String tableType;
        private Object params;


        public String getCatalog() {
            return catalog;
        }

        public void setCatalog(String catalog) {
            this.catalog = catalog;
        }

        public String getSchema() {
            return schema;
        }

        public void setSchema(String schema) {
            this.schema = schema;
        }

        public String getTable() {
            return table;
        }

        public void setTable(String table) {
            this.table = table;
        }

        public String getComment() {
            return comment;
        }

        public void setComment(String comment) {
            this.comment = comment;
        }

        public String getFqn() {
            return fqn;
        }

        public void setFqn(String fqn) {
            this.fqn = fqn;
        }

        public String getTableType() {
            return tableType;
        }

        public void setTableType(String tableType) {
            this.tableType = tableType;
        }

        public Object getParams() {
            return params;
        }

        public void setParams(Object params) {
            this.params = params;
        }
    }
}
