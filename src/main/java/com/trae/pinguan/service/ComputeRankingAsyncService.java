package com.trae.pinguan.service;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.entity.ScoringSnapshot;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class ComputeRankingAsyncService {

    private final ReviewService reviewService;
    private final ComputeJobTracker jobTracker;

    @Async("computeRankingExecutor")
    public void compute(String jobId, Long competitionId, ReviewStage stage,
                        GroupType groupType, boolean interviewOnly) {
        log.info("[compute-ranking] job={} start competitionId={} stage={} interviewOnly={}",
                jobId, competitionId, stage, interviewOnly);
        try {
            List<ScoringSnapshot> snapshots = reviewService.computeAndSaveRanking(
                    competitionId, stage, groupType, interviewOnly);
            jobTracker.success(jobId, snapshots.size());
            log.info("[compute-ranking] job={} SUCCESS count={}", jobId, snapshots.size());
        } catch (Exception e) {
            jobTracker.fail(jobId, e.getMessage());
            log.error("[compute-ranking] job={} FAILED", jobId, e);
        }
    }
}
