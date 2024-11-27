package com.example.demo1.controller;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

@CrossOrigin(origins = "*", allowedHeaders = "*")
@RestController
public class FileUploadController {

    // 上传文件接口
    @PostMapping("/upload")
    public ResponseEntity<String> uploadImage(@RequestParam("image") MultipartFile imageFile) {
        if (imageFile.isEmpty()) {
            return ResponseEntity.badRequest().body("没有文件上传");
        }

        String uploadDir = "F:/Desktop/JavaDemo/zhuayizhua/houduan/";
        String fileName = imageFile.getOriginalFilename();
        File fileToSave = new File(uploadDir + fileName);

        try {
            imageFile.transferTo(fileToSave);
            return ResponseEntity.ok("上传成功: " + fileName);
        } catch (IOException e) {
            return ResponseEntity.status(500).body("上传失败: " + e.getMessage());
        }
    }

    // 允许预检请求
    @CrossOrigin(origins = "https://127.0.0.1:8443", allowedHeaders = "*")
    @RequestMapping(value = "/image/recent", method = RequestMethod.OPTIONS)
    public ResponseEntity<Void> handlePreflight() {
        return ResponseEntity.ok().build();
    }


    @GetMapping("/image/recent")
    public ResponseEntity<byte[]> getRecentImage() {
        String uploadDir = "F:/Desktop/JavaDemo/zhuayizhua/houduan/";
        File dir = new File(uploadDir);

        // 获取目录下所有的图片文件
        File[] imageFiles = dir.listFiles((dir1, name) -> name.toLowerCase().endsWith(".jpg")
                || name.toLowerCase().endsWith(".jpeg") || name.toLowerCase().endsWith(".png")
                || name.toLowerCase().endsWith(".gif") || name.toLowerCase().endsWith(".bmp")
                || name.toLowerCase().endsWith(".webp")); // 添加更多图片格式支持

        if (imageFiles == null || imageFiles.length == 0) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
        }

        // 按照修改时间排序，获取最新的文件
        File recentFile = null;
        long lastModified = Long.MIN_VALUE;

        for (File file : imageFiles) {
            if (file.lastModified() > lastModified) {
                lastModified = file.lastModified();
                recentFile = file;
            }
        }

        try {
            byte[] imageBytes = Files.readAllBytes(recentFile.toPath());
            HttpHeaders headers = new HttpHeaders();

            // 动态获取文件的MIME类型
            String mimeType = Files.probeContentType(recentFile.toPath());
            if (mimeType != null) {
                headers.setContentType(MediaType.parseMediaType(mimeType)); // 根据MIME类型设置响应头
            } else {
                headers.setContentType(MediaType.APPLICATION_OCTET_STREAM); // 默认二进制流
            }

            return new ResponseEntity<>(imageBytes, headers, HttpStatus.OK);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }

}