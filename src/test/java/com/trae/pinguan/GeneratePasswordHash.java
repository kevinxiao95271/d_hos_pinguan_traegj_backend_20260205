package com.trae.pinguan;

import org.mindrot.jbcrypt.BCrypt;

/**
 * 生成密码哈希的工具类
 */
public class GeneratePasswordHash {
    
    public static void main(String[] args) {
        System.out.println("====================================");
        System.out.println("生成管理员密码哈希");
        System.out.println("====================================");
        
        // 组委会账号
        String committeePassword = "committee2026";
        String committeeHash = BCrypt.hashpw(committeePassword, BCrypt.gensalt());
        
        System.out.println("\n[组委会]");
        System.out.println("  密码: " + committeePassword);
        System.out.println("  哈希: " + committeeHash);
        System.out.println("  验证: " + BCrypt.checkpw(committeePassword, committeeHash));
        
        // 运维账号
        String opsPassword = "ops2026";
        String opsHash = BCrypt.hashpw(opsPassword, BCrypt.gensalt());
        
        System.out.println("\n[系统运维]");
        System.out.println("  密码: " + opsPassword);
        System.out.println("  哈希: " + opsHash);
        System.out.println("  验证: " + BCrypt.checkpw(opsPassword, opsHash));
        
        System.out.println("\n====================================");
        System.out.println("SQL更新语句:");
        System.out.println("====================================");
        
        System.out.println("\n-- 组委会 (13800000127)");
        System.out.println("UPDATE user_accounts SET password = '" + committeeHash + "' WHERE phone = '13800000127';");
        
        System.out.println("\n-- 运维 (13800000005)");
        System.out.println("UPDATE user_accounts SET password = '" + opsHash + "' WHERE phone = '13800000005';");
        
        System.out.println("\n====================================");
    }
}
