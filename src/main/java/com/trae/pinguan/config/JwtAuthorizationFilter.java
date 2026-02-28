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
        String method = request.getMethod();
        
        // 白名单：无需JWT验证的接口
        // 1. 认证接口、Swagger和actuator
        if (path.startsWith("/api/auth/")
                || path.startsWith("/swagger")
                || path.startsWith("/v3/api-docs")
                || path.startsWith("/actuator")) {
            filterChain.doFilter(request, response);
            return;
        }
        
        // 2. 机构查询公开接口（注册时需要）
        if (isPublicInstitutionEndpoint(path, method)) {
            filterChain.doFilter(request, response);
            return;
        }
        
        // 3. 字典查询接口（注册和报名时需要）- GET方法公开
        if ("GET".equalsIgnoreCase(method) && path.startsWith("/api/dictionaries")) {
            filterChain.doFilter(request, response);
            return;
        }
        
        // 4. 赛事查询公开接口（获取赛事列表和最新赛事）
        if ("GET".equalsIgnoreCase(method) && 
            (path.equals("/api/competitions") || path.equals("/api/competitions/latest"))) {
            filterChain.doFilter(request, response);
            return;
        }
        
        // 5. 系统模版下载接口（公开）
        if ("GET".equalsIgnoreCase(method) && 
            (path.equals("/api/system-templates/active") || 
             path.matches("^/api/system-templates/\\d+/download$"))) {
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
    
    /**
     * 判断是否为公开的机构接口（注册时需要，无需token）
     */
    private boolean isPublicInstitutionEndpoint(String path, String method) {
        // GET方法的查询接口（公开）
        if ("GET".equalsIgnoreCase(method)) {
            return path.equals("/api/institutions/search")           // 搜索（GET版本）
                || path.equals("/api/institutions/autocomplete")     // 自动完成
                || path.equals("/api/institutions/hot-regions")      // 热门地区
                || path.equals("/api/institutions/cities")           // 城市列表
                || path.equals("/api/institutions/regions")          // 地区列表
                || path.equals("/api/institutions/districts")        // 区县列表
                || path.equals("/api/institutions/levels")           // 等级列表
                || path.equals("/api/institutions/region-stats")     // 地区统计
                || path.matches("^/api/institutions/\\d+$")          // 机构详情 /api/institutions/{id}
                || path.matches("^/api/institutions/by-uscc/.*$");   // 根据USCC查询
        }
        
        // POST方法的搜索接口（公开）
        if ("POST".equalsIgnoreCase(method)) {
            return path.equals("/api/institutions/search");          // 高性能搜索
        }
        
        // 其他方法（PUT, DELETE, POST创建/导入）需要认证
        return false;
    }
}
