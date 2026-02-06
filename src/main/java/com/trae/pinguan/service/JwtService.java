package com.trae.pinguan.service;

import com.trae.pinguan.config.JwtProperties;
import com.trae.pinguan.domain.entity.UserAccount;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class JwtService {
    private final JwtProperties jwtProperties;

    public String generateToken(UserAccount user) {
        Instant now = Instant.now();
        return Jwts.builder()
                .setSubject(String.valueOf(user.getId()))
                .claim("role", user.getRole().name())
                .setIssuedAt(Date.from(now))
                .setExpiration(Date.from(now.plus(jwtProperties.getExpireMinutes(), ChronoUnit.MINUTES)))
                .signWith(key(), SignatureAlgorithm.HS256)
                .compact();
    }

    public Jws<Claims> parse(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key())
                .build()
                .parseClaimsJws(token);
    }

    private Key key() {
        String secret = jwtProperties.getSecret();
        if (secret == null || secret.trim().isEmpty()) {
            throw new IllegalArgumentException("JWT_SECRET 未配置");
        }
        byte[] bytes = secret.getBytes(StandardCharsets.UTF_8);
        if (bytes.length < 32) {
            throw new IllegalArgumentException("JWT_SECRET 长度不足 32");
        }
        return Keys.hmacShaKeyFor(bytes);
    }
}
