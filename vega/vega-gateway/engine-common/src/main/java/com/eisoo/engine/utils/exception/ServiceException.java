package com.eisoo.engine.utils.exception;

import lombok.Getter;

@Getter
public class ServiceException extends RuntimeException {
    private final int httpStatus;
    private final String result;

    public ServiceException(int httpStatus, String result) {
        super(result);
        this.httpStatus = httpStatus;
        this.result = result;
    }
}