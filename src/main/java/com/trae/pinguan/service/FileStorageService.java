package com.trae.pinguan.service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class FileStorageService {
    private final Path root = Paths.get("data", "uploads");

    public String store(Long registrationId, MultipartFile file) {
        return store(String.valueOf(registrationId), file);
    }

    public String store(String directory, MultipartFile file) {
        try {
            Path targetDir = root.resolve(directory);
            Files.createDirectories(targetDir);
            String filename = UUID.randomUUID() + "-" + file.getOriginalFilename();
            Path targetFile = targetDir.resolve(filename);
            Files.copy(file.getInputStream(), targetFile);
            return targetFile.toAbsolutePath().toString();
        } catch (IOException ex) {
            throw new IllegalStateException("文件保存失败");
        }
    }

    public void delete(String fileUrl) {
        try {
            if (fileUrl == null) {
                return;
            }
            Files.deleteIfExists(Paths.get(fileUrl));
        } catch (IOException ex) {
            throw new IllegalStateException("文件删除失败");
        }
    }
}
