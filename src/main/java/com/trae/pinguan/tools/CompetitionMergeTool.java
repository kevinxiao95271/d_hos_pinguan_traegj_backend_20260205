package com.trae.pinguan.tools;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class CompetitionMergeTool {
    public static void main(String[] args) throws Exception {
        String url = System.getenv("PINGUAN_DS1_URL");
        String user = System.getenv("PINGUAN_DS1_USER");
        String password = System.getenv("PINGUAN_DS1_PASSWORD");
        if (url == null || user == null || password == null) {
            throw new IllegalStateException("Missing datasource env");
        }
        long targetId = args.length > 0 ? Long.parseLong(args[0]) : 21L;
        String keepArg = args.length > 1 ? args[1] : "1,21";
        Set<Long> keepIds = new HashSet<>();
        for (String part : keepArg.split(",")) {
            String trimmed = part.trim();
            if (!trimmed.isEmpty()) {
                keepIds.add(Long.parseLong(trimmed));
            }
        }
        keepIds.add(targetId);
        List<Long> keepList = new ArrayList<>(keepIds);

        Class.forName("com.mysql.cj.jdbc.Driver");
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            conn.setAutoCommit(false);
            int moved;
            try (PreparedStatement update = conn.prepareStatement(
                    "UPDATE registrations SET competition_id = ? WHERE competition_id <> ?")) {
                update.setLong(1, targetId);
                update.setLong(2, targetId);
                moved = update.executeUpdate();
            }
            try (PreparedStatement update = conn.prepareStatement(
                    "UPDATE competition_templates SET competition_id = ? WHERE competition_id <> ?")) {
                update.setLong(1, targetId);
                update.setLong(2, targetId);
                update.executeUpdate();
            }
            StringBuilder deleteSql = new StringBuilder("DELETE FROM competitions WHERE id NOT IN (");
            for (int i = 0; i < keepList.size(); i++) {
                if (i > 0) {
                    deleteSql.append(",");
                }
                deleteSql.append("?");
            }
            deleteSql.append(")");
            int deleted;
            try (PreparedStatement delete = conn.prepareStatement(deleteSql.toString())) {
                for (int i = 0; i < keepList.size(); i++) {
                    delete.setLong(i + 1, keepList.get(i));
                }
                deleted = delete.executeUpdate();
            }
            conn.commit();
            System.out.println("movedRegistrations=" + moved);
            System.out.println("deletedCompetitions=" + deleted);
        }
    }
}
