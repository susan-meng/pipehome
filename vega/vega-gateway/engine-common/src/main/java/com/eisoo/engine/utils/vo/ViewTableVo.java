package com.eisoo.engine.utils.vo;

import lombok.Data;

/**
 * @Author zdh
 **/
@Data
public class ViewTableVo {
    private String catalogName;
    private String viewName;
    private String schema;
    private String connectorName;
}
