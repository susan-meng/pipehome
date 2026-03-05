package com.eisoo.engine.metadata.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * 
 * 
 * @author aishu.cn
 * @email xxxx@aishu.cn
 * @date 2023-02-23 17:12:30
 */
@Data
@TableName("t_data_source")
public class DataSourceEntity extends BaseEntity implements Serializable {
	private static final long serialVersionUID = 1L;
	/**
	 * 唯一id，雪花算法
	 */
	@TableId(value = "f_id", type = IdType.ASSIGN_ID)
    private Long id;

	/**
	 * 数据源名称
	 */
	@TableField(value = "f_name")
	private String name;

	/**
	 * 类型，关联字典表f_dict_type为1时的f_dict_key
	 */
	@TableField(value = "f_data_source_type")
	private Integer dataSourceType;

	/**
	 * 类型名称，对应字典表f_dict_type为1时的f_dict_value
	 */
	@TableField(value = "f_data_source_type_name")
	private String dataSourceTypeName;

	/**
	 * 用户名
	 */
	@TableField(value = "f_user_name")
	private String userName;

	/**
	 * 密码
	 */
	@TableField(value = "f_password")
	private String password;

	/**
	 * 描述
	 */
	@TableField(value = "f_description")
	private String description;

	/**
	 * 扩展属性，默认为空字符串
	 */
	@TableField(value = "f_extend_property")
	private String extendProperty;

	/**
	 * HOST
	 */
	@TableField(value = "f_host")
	private String host;

	/**
	 * 端口
	 */
	@TableField(value = "f_port")
	private Integer port;

	/**
	 * 禁用/启用状态，1 启用，2 停用，默认为启用
	 */
	@TableField(value = "f_enable_status")
	private Integer enableStatus;

	/**
	 * 连接状态，1 成功，2 失败，默认为成功
	 */
	@TableField(value = "f_connect_status")
	private Integer connectStatus;

	/**
	 * 权限域（目前为预留字段），默认0
	 */
	@TableField(value = "f_authority_id")
	private String authorityId;

	/**
	 * 创建时间
	 */
	@TableField(value = "f_create_time")
	@JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
	private Date createTime;

	/**
	 * 创建用户（ID），默认空字符串
	 */
	@TableField(value = "f_create_user")
	private String createUser;

	/**
	 * 修改时间，默认当前时间
	 */
	@TableField(value = "f_update_time")
	@JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
	private Date updateTime;

	/**
	 * 修改用户（ID），默认空字符串
	 */
	@TableField(value = "f_update_user")
	private String updateUser;

	/**
	 * 数据源的数据库
	 */
	@TableField(value = "f_database")
	private String databaseName;

	/**
	 * 数据源的信息系统id
	 */
	@TableField(value = "f_info_system_id")
	private String infoSystemId;

	/**
	 * 数据源的dolphin平台id
	 */
	@TableField(value = "f_dolphin_id")
	private Long dolphinId;

	@TableField(value = "f_live_update_status")
	private Integer liveUpdateStatus;

	@TableField(value = "f_live_update_benchmark")
	private String liveUpdateBenchmark;

	@TableField(value = "f_live_update_time")
	private Date liveUpdateTime;


}
