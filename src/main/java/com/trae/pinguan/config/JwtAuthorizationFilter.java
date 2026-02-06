package com.trae.pinguan.config;

import com.trae.pinguan.service.JwtService;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import java.io.IOException;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
@RequiredArgsConstructor
public class JwtAuthorizationFilter extends OncePerRequestFilter {
    private final JwtService jwtService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String path = request.getRequestURI();
        // 只有认证接口、Swagger和actuator可以跳过JWT验证
        if (path.startsWith("/api/auth/")
                || path.startsWith("/swagger")
                || path.startsWith("/v3/api-docs")
                || path.startsWith("/actuator")) {
            filterChain.doFilter(request, response);
            return;
        }
        String token = null;
        String header = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (header != null && !header.trim().isEmpty()) {
            String normalized = header.trim();
            if (normalized.length() >= 6 && normalized.toLowerCase().startsWith("bearer")) {
                token = normalized.substring(6).trim();
            } else {
                token = normalized;
            }
        }
        if (token == null || token.trim().isEmpty()) {
            String altHeader = request.getHeader("token");
            if (altHeader != null && !altHeader.trim().isEmpty()) {
                token = altHeader;
            }
        }
        if (token == null || token.trim().isEmpty()) {
            String paramToken = request.getParameter("token");
            if (paramToken == null || paramToken.trim().isEmpty()) {
                paramToken = request.getParameter("accessToken");
            }
            if (paramToken != null && !paramToken.trim().isEmpty()) {
                token = paramToken;
            }
        }
        if (token == null || token.trim().isEmpty()) {
            String query = request.getQueryString();
            if (query != null && !query.trim().isEmpty()) {
                String[] parts = query.split("&");
                for (String part : parts) {
                    int idx = part.indexOf('=');
                    if (idx <= 0) {
                        continue;
                    }
                    String key = part.substring(0, idx);
                    if (!"token".equals(key) && !"accessToken".equals(key)) {
                        continue;
                    }
                    String value = java.net.URLDecoder.decode(part.substring(idx + 1), java.nio.charset.StandardCharsets.UTF_8.name());
                    if (value != null && !value.trim().isEmpty()) {
                        token = value;
                        break;
                    }
                }
            }
        }
        if (token == null || token.trim().isEmpty()) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
        // 只在JWT解析时catch，不要catch filterChain的异常
        Jws<Claims> claims;
        try {
            claims = jwtService.parse(token);
        } catch (Exception ex) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
        String userId = claims.getBody().getSubject();
        String role = claims.getBody().get("role", String.class);
        request.setAttribute("userId", userId);
        request.setAttribute("role", role);
        filterChain.doFilter(request, response);
    }
}
