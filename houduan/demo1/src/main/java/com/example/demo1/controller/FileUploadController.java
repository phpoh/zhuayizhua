package com.example.demo1.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;

@RestController
public class FileUploadController {

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
}