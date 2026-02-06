package com.trae.pinguan.config;

import java.util.concurrent.atomic.AtomicReference;

public class DataSourceContext {
    private static final AtomicReference<String> CURRENT = new AtomicReference<>("ds1");

    public static String getCurrent() {
        return CURRENT.get();
    }

    public static void setCurrent(String key) {
        CURRENT.set(key);
    }
}
