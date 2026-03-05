package com.eisoo.engine.utils;

import com.eisoo.engine.utils.exception.AiShuException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.HashMap;
import java.util.Optional;

/**
 * @Author zdh
 **/
public class Results<T> extends Result {
    public static ResponseEntity<Result> internalServerError(AiShuException e) {
        Result r = new Result();
        r.setCode(e.getErrorCode());
        r.setDescription(Optional.ofNullable(e.getDescription()).orElse(""));
        r.setDetail(Optional.ofNullable(e.getErrorDetails()).orElse(new HashMap<>()));
        r.setSolution(Optional.ofNullable(e.getSolution()).orElse(""));
        r.setData(null);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(r);
    }
}
