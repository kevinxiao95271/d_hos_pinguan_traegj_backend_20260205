-- competitions 初始化（导出自当前环境）
START TRANSACTION;

INSERT INTO competitions (
  id, name, stage,
  register_start, register_end,
  book_review_start, book_review_end,
  interview_start, interview_end,
  final_start, final_end,
  created_at
) VALUES
(1, '2026浙江省品管大赛', 'REGISTER', '2026-01-26 19:36:53', '2026-03-27 19:36:53', NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-25 19:36:53')
ON DUPLICATE KEY UPDATE
name = VALUES(name),
stage = VALUES(stage),
register_start = VALUES(register_start),
register_end = VALUES(register_end),
book_review_start = VALUES(book_review_start),
book_review_end = VALUES(book_review_end),
interview_start = VALUES(interview_start),
interview_end = VALUES(interview_end),
final_start = VALUES(final_start),
final_end = VALUES(final_end);

COMMIT;

-- summary: competitions=1