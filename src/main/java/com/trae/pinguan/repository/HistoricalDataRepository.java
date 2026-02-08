package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.HistoricalData;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

/**
 * 历史数据仓储
 */
@Repository
public interface HistoricalDataRepository extends JpaRepository<HistoricalData, Integer>, 
        JpaSpecificationExecutor<HistoricalData> {
}
