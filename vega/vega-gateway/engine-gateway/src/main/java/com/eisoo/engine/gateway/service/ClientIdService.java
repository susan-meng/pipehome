package com.eisoo.engine.gateway.service;

import com.eisoo.engine.metadata.entity.ClientIdEntity;
import com.github.yulichang.base.MPJBaseService;

public interface ClientIdService extends MPJBaseService<ClientIdEntity> {
    ClientIdEntity getClientIdAndSecret();

    ClientIdEntity reRegistClient();
}
