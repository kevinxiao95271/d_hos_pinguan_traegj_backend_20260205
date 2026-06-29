-- 决赛评委任务分配 review_tasks INSERT
-- 生成时间: 2026-05-31
-- 在生产库执行，registration_id 通过子查询动态获取
-- 执行前请确认 review_tasks 中 stage='FINAL' 无历史数据

-- ── 2026基层组1组  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 683, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 1543, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 453, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 674, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组1组';

-- ── 2026基层组2组  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 773, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 745, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 779, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 792, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组2组';

-- ── 2026基层组3组  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 731, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 718, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 761, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 770, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组3组';

-- ── 2026基层组4组  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 664, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组4组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 752, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组4组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 747, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组4组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 687, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026基层组4组';

-- ── 2026综合组PDCA专场1  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 670, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 663, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 907, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 798, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场1';

-- ── 2026综合组PDCA专场2  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 707, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 768, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 764, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 777, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场2';

-- ── 2026综合组PDCA专场3  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 679, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 800, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 778, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 669, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组PDCA专场3';

-- ── 2026综合组QFD、课题达成型专场1  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 690, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 684, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 782, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 769, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场1';

-- ── 2026综合组QFD、课题达成型专场2  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 681, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 662, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 804, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 704, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场2';

-- ── 2026综合组QFD、课题达成型专场3  (5 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 732, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 685, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 772, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 774, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 710, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场3';

-- ── 2026综合组十大安全目标专场1  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 711, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 720, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 794, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 809, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场1';

-- ── 2026综合组十大安全目标专场2  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 791, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 785, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 802, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 758, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组十大安全目标专场2';

-- ── 2026综合组综合工具专场1  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 748, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 727, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 694, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 765, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场1';

-- ── 2026综合组综合工具专场2  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 729, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 666, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 776, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 806, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组综合工具专场2';

-- ── 2026综合组问题解决型专场1  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 672, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 717, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 737, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场1';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 702, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场1';

-- ── 2026综合组问题解决型专场2  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 705, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 757, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 771, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场2';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 695, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场2';

-- ── 2026综合组问题解决型专场3  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 719, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 756, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 743, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场3';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 736, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场3';

-- ── 2026综合组问题解决型专场4  (4 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 455, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场4';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 789, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场4';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 799, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场4';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 734, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026综合组问题解决型专场4';

-- ── 2026进阶组1组  (5 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 691, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 783, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 767, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 700, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组1组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 740, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组1组';

-- ── 2026进阶组2组  (5 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 680, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 741, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 760, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 733, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组2组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 722, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组2组';

-- ── 2026进阶组3组  (5 位评委) ──────────────
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 786, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 698, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 723, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 803, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组3组';
INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
  SELECT 'FINAL', r.id, 676, 'PENDING', NOW()
  FROM registrations r
  WHERE r.final_session_code = '2026进阶组3组';
