package com.iotserver.global.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.io.File;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${app.upload.dir:uploads}")
    private String uploadDir;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        File dir = new File(uploadDir);
        String absolutePath = dir.getAbsolutePath();

        // ResourceLocations must end with a trailing slash
        String resourceLocation = "file:" + absolutePath + File.separator;

        registry.addResourceHandler("/uploads/**")
                .addResourceLocations(resourceLocation);
    }
}
