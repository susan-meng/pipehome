package com.eisoo.engine.metadata.mapper;

import com.eisoo.engine.metadata.entity.CatalogRuleEntity;
import com.github.yulichang.base.MPJBaseMapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/*
 * @Author paul
 *
 **/
public interface CatalogRuleMapper extends MPJBaseMapper<CatalogRuleEntity> {
    @Select("SELECT catalog_name,datasource_type,pushdown_rule,is_enabled from catalog_rule ")
    List<CatalogRuleEntity> selectAll();
    @Select("SELECT catalog_name,datasource_type,pushdown_rule,is_enabled from catalog_rule WHERE catalog_name = #{catalogName}")
    List<CatalogRuleEntity> selectRuleInfo(@Param("catalogName") String catalogName);
    @Select("SELECT catalog_name,datasource_type,pushdown_rule,is_enabled from catalog_rule WHERE catalog_name = #{catalogName} and pushdown_rule =#{pushdownRule}")
    CatalogRuleEntity selectRuleOperator(@Param("catalogName") String catalogName,@Param("pushdownRule") String pushdownRule);

}
