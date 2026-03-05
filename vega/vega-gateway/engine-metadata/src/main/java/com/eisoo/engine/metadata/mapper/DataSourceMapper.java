package com.eisoo.engine.metadata.mapper;


import com.eisoo.engine.metadata.entity.DataSourceEntity;
import com.github.yulichang.base.MPJBaseMapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

public interface DataSourceMapper extends MPJBaseMapper<DataSourceEntity> {

    @Update("UPDATE t_data_source SET f_delete_code = #{timestamp} WHERE f_id = #{id}")
    int updateDeleteCodeById(@Param("id") Long id, @Param("timestamp") Long timestamp);
}
