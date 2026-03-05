package com.eisoo.engine.gateway.connector;

import cn.hutool.core.io.IoUtil;
import com.eisoo.engine.gateway.common.CatalogConstant;
import com.eisoo.engine.utils.common.Detail;
import com.eisoo.engine.utils.common.Message;
import com.eisoo.engine.utils.enums.ErrorCodeEnum;
import com.eisoo.engine.utils.exception.AiShuException;
import com.eisoo.engine.utils.util.StringUtils;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.support.ResourcePatternResolver;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.util.Map;
import java.util.Set;

import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.core.io.Resource;

/**
 * @Author zdh
 **/
@Component
public class ConnectorConfigCache {

    private static final Logger log = LoggerFactory.getLogger(ConnectorConfigCache.class);
    private static final Map<String, ConnectorConfig> connectorConfigMaps = Maps.newConcurrentMap();
    private static final Map<String, OperatorConfig> ruleConfigMaps = Maps.newConcurrentMap();
    private static final Set<String> connectorNames = Sets.newConcurrentHashSet();
    private static final Set<String> ruleNames = Sets.newConcurrentHashSet();
    public static final Set<String> vegaTypes = Sets.newConcurrentHashSet();
    private final String connectorNameList = "clickhouse,dameng,doris,excel,gaussdb,gbase,hive,hologres,inceptor-jdbc,maria,maxcompute,mongodb,mysql,opengauss,opensearch,oracle,postgresql,sqlserver";
    private final String RuleNameList = "FilterNode,ProjectNode,AggregationNode,TopNNode,LimitNode,JoinNode,GroupIdNode,MarkDistinctNode,UnionNode";

    @PostConstruct
    @SuppressWarnings("PMD.UnusedPrivateMethod")
    private void init() {
        setConnectorNames(connectorNameList);
        // 遍历connector配置文件目录
        loadConnectorConfigs(CatalogConstant.CONNECTOR_CONFIG_PATH);
        setRuleNames(RuleNameList);
        ruleNames.stream().forEach(ruleNames -> {
            try {
                String config = getConfigRuleFile();
                if (StringUtils.isNotBlank(config)) {
                    ObjectMapper mapper = new ObjectMapper();
                    RuleConfig ruleConfig = mapper.readValue(config, RuleConfig.class);
                    ruleConfigMaps.put(ruleNames, ruleConfig.getRules().stream().filter(operatorConfig -> operatorConfig.getRuleName().equals(ruleNames)).findFirst().orElse(null));
                }
            } catch (JsonProcessingException e) {
                log.error("catalog rule config cache parse json error");
                throw new AiShuException(ErrorCodeEnum.InternalError, Detail.CATALOG_RULE_CACHE_JSON_ANALYZE_ERROR, Message.MESSAGE_INTERNAL_ERROR);
            }
        });
    }

    private void loadConnectorConfigs(String path) {
        try {
            for (String connectorName : connectorNames) {
                String config = getConfigFile(connectorName);
                if (StringUtils.isNotBlank(config)) {
                    ObjectMapper mapper = new ObjectMapper();
                    ConnectorConfig connectorConfig = mapper.readValue(config, ConnectorConfig.class);
                    connectorConfig.getType().forEach(typeConfig -> {
                        if (!typeConfig.getVegaType().isEmpty()) {
                            vegaTypes.add(typeConfig.getVegaType().toLowerCase());
                        }
                    });
                    connectorConfigMaps.put(connectorName, connectorConfig);
                }
            }
            log.info("-----------------------------------loadConnectorConfigs success---------------------------------------\n{}", connectorConfigMaps);
        } catch (Exception e) {
            log.error("Failed to load connector configs from directory: {}", path, e);
            throw new AiShuException(ErrorCodeEnum.InternalError, e.getMessage(), Message.MESSAGE_INTERNAL_ERROR);
        }
    }


    private String getConfigFile(String connectorName) {
        InputStream config = getFile(CatalogConstant.CONNECTOR_CONFIG_PATH + connectorName + ".json");
        String connectorConfig = null;
        if (StringUtils.isNotNull(config)) {
            connectorConfig = IoUtil.read(config, Charset.defaultCharset());
        }
        return connectorConfig;
    }

    private String getConfigRuleFile() {
        InputStream config = getFile(CatalogConstant.RULE_CONFIG_PATH + ".json");
        String ruleConfig = null;
        if (StringUtils.isNotNull(config)) {
            ruleConfig = IoUtil.read(config, Charset.defaultCharset());
        }
        return ruleConfig;
    }

    public ConnectorConfig getConnectorConfig(String connectorName) {
        if (connectorName.equals(CatalogConstant.HIVE_CATALOG)
                || connectorName.equals(CatalogConstant.HIVE_JDBC_CATALOG)) {
            connectorName = "hive";
        }
        ConnectorConfig connectorConfig = connectorConfigMaps.get(connectorName);
        if (null == connectorConfig) {
            log.warn("connectorName:{};connectorConfigMaps:{}", connectorName, connectorConfigMaps);
        }
        return connectorConfigMaps.get(connectorName);
    }

    public OperatorConfig getRuleConfig(String connectorName) {
        return ruleConfigMaps.get(connectorName);
    }

    public Set<String> getConnectorNames() {
        return connectorNames;
    }

    public Set<String> getRuleNames() {
        return ruleNames;
    }

    private void setRuleNames(String ruleNameList) {
        String[] names = StringUtils.split(ruleNameList, ",");
        for (String name : names) {
            ruleNames.add(name);
        }
    }

    public InputStream getFile(String path) {
        InputStream inputStream = ConnectorConfigCache.class.getResourceAsStream(path);
        return inputStream;
    }

    private void setConnectorNames(String connectorNameList) {
        String[] names = StringUtils.split(connectorNameList, ",");
        for (String name : names) {
            connectorNames.add(name);
        }
    }

}
