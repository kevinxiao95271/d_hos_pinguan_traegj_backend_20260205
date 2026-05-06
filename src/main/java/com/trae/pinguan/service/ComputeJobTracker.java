package com.trae.pinguan.service;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import lombok.AllArgsConstructor;
import lombok.Data;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 内存级 job 状态追踪，用于异步算分任务的进度查询。
 * 超过 2 小时的已完成任务会自动清理。
 */
@Component
public class ComputeJobTracker {

    public enum JobStatus { RUNNING, SUCCESS, FAILED }

    @Data
    @AllArgsConstructor
    public static class JobInfo {
        private JobStatus status;
        private Integer snapshotCount;
        private String error;
        private LocalDateTime startedAt;
        private LocalDateTime finishedAt;
        /** 0-100，RUNNING 期间实时更新；SUCCESS/FAILED 时固定为 100/当前值 */
        private int progress;
        /** 当前进度描述，如"正在处理基层组…" */
        private String progressMsg;
    }

    private final ConcurrentHashMap<String, JobInfo> jobs = new ConcurrentHashMap<>();

    public void start(String jobId) {
        jobs.put(jobId, new JobInfo(JobStatus.RUNNING, null, null, LocalDateTime.now(), null, 0, "任务已启动"));
    }

    public void progress(String jobId, int percent, String msg) {
        jobs.computeIfPresent(jobId, (k, v) -> {
            v.setProgress(Math.min(percent, 99)); // 100 留给 success
            v.setProgressMsg(msg);
            return v;
        });
    }

    public void success(String jobId, int count) {
        jobs.computeIfPresent(jobId, (k, v) ->
                new JobInfo(JobStatus.SUCCESS, count, null, v.getStartedAt(), LocalDateTime.now(), 100, "计算完成"));
    }

    public void fail(String jobId, String error) {
        jobs.computeIfPresent(jobId, (k, v) ->
                new JobInfo(JobStatus.FAILED, null, error, v.getStartedAt(), LocalDateTime.now(), v.getProgress(), "任务失败"));
    }

    public Optional<JobInfo> get(String jobId) {
        return Optional.ofNullable(jobs.get(jobId));
    }

    /** 每小时清理超过 2 小时的已完成任务，防止内存泄漏 */
    @Scheduled(fixedDelay = 3_600_000)
    public void cleanup() {
        LocalDateTime cutoff = LocalDateTime.now().minusHours(2);
        jobs.entrySet().removeIf(e -> {
            JobInfo info = e.getValue();
            return info.getFinishedAt() != null && info.getFinishedAt().isBefore(cutoff);
        });
    }
}
