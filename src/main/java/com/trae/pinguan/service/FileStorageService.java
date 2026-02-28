package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import io.minio.*;
import io.minio.http.Method;
import java.io.InputStream;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class FileStorageService {
    private final MinioClient minioClient;
    private final MinioProperties minioProperties;
    
    /**
     * 存储报名材料（原有方法，使用 registration-files bucket）
     */
    public String store(Long registrationId, MultipartFile file) {
        return store(String.valueOf(registrationId), file, minioProperties.getBucket().getRegistrationFiles());
    }
    
    /**
     * 存储报名材料（原有方法，使用 registration-files bucket）
     */
    public String store(String directory, MultipartFile file) {
        return store(directory, file, minioProperties.getBucket().getRegistrationFiles());
    }
    
    /**
     * 存储系统模版（新方法，使用 system-templates bucket）
     */
    public String storeSystemTemplate(String templateType, MultipartFile file) {
        String bucketName = minioProperties.getBucket().getSystemTemplates();
        ensureBucketExists(bucketName);
        
        String objectName = templateType + "/" + UUID.randomUUID() + "-" + file.getOriginalFilename();
        
        try (InputStream inputStream = file.getInputStream()) {
            minioClient.putObject(
                PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .stream(inputStream, file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build()
            );
            return objectName;
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件上传失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 通用存储方法
     */
    private String store(String directory, MultipartFile file, String bucketName) {
        ensureBucketExists(bucketName);
        
        String objectName = directory + "/" + UUID.randomUUID() + "-" + file.getOriginalFilename();
        
        try (InputStream inputStream = file.getInputStream()) {
            minioClient.putObject(
                PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .stream(inputStream, file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build()
            );
            return objectName;
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件上传失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 生成预签名下载 URL（7天有效期，但主要用于流式下载，此方法备用）
     */
    public String getPresignedUrl(String objectName, String bucketName) {
        try {
            return minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                    .method(Method.GET)
                    .bucket(bucketName)
                    .object(objectName)
                    .expiry(7, TimeUnit.DAYS)
                    .build()
            );
        } catch (Exception ex) {
            throw new IllegalStateException("生成预签名 URL 失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 获取文件流（用于后端代理下载，永久有效）
     */
    public InputStream getInputStream(String objectName, String bucketName) {
        try {
            return minioClient.getObject(
                GetObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .build()
            );
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件读取失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 删除报名材料文件
     */
    public void delete(String objectName) {
        delete(objectName, minioProperties.getBucket().getRegistrationFiles());
    }
    
    /**
     * 删除系统模版文件
     */
    public void deleteSystemTemplate(String objectName) {
        delete(objectName, minioProperties.getBucket().getSystemTemplates());
    }
    
    /**
     * 通用删除方法
     */
    private void delete(String objectName, String bucketName) {
        try {
            if (objectName == null || objectName.trim().isEmpty()) {
                return;
            }
            minioClient.removeObject(
                RemoveObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .build()
            );
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件删除失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 确保 Bucket 存在
     */
    private void ensureBucketExists(String bucketName) {
        try {
            boolean exists = minioClient.bucketExists(
                BucketExistsArgs.builder().bucket(bucketName).build()
            );
            if (!exists) {
                minioClient.makeBucket(
                    MakeBucketArgs.builder().bucket(bucketName).build()
                );
            }
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO Bucket 检查/创建失败: " + ex.getMessage(), ex);
        }
    }
}
