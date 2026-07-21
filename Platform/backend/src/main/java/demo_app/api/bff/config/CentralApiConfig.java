package demo_app.api.bff.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class CentralApiConfig {

    @Bean
    public RestClient centralRestClient(@Value("${central.api.url}") String baseUrl) {
        return RestClient.builder().baseUrl(baseUrl).build();
    }
}
