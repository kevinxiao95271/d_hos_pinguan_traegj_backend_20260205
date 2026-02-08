#!/bin/bash
# 前端API测试脚本 - 使用真实项目ID 119
# 用于验证Label字段是否正确返回

echo "================================================================================"
echo "前端API测试 - Label字段验证"
echo "================================================================================"
echo ""

BASE_URL="http://localhost:6031"
PROJECT_ID=119

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "步骤1: 登录评委账号"
echo "--------------------------------------------------------------------------------"
echo "请求: POST $BASE_URL/api/auth/login"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13900000001",
    "name": "李明华",
    "role": "REVIEWER"
  }')

echo "$LOGIN_RESPONSE" | python -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# 提取token
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ 登录失败，无法获取token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 登录成功${NC}"
echo "Token: ${TOKEN:0:30}..."
echo ""

echo "步骤2: 获取项目详情（项目ID: $PROJECT_ID）"
echo "--------------------------------------------------------------------------------"
echo "请求: GET $BASE_URL/api/registrations/$PROJECT_ID"
echo ""

DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/api/registrations/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$DETAIL_RESPONSE" | python -m json.tool 2>/dev/null || echo "$DETAIL_RESPONSE"
echo ""

echo "================================================================================"
echo "Label字段检查"
echo "================================================================================"
echo ""

# 提取Label字段
SUBJECT_TYPE_LABEL=$(echo "$DETAIL_RESPONSE" | grep -o '"subjectTypeLabel":"[^"]*' | cut -d'"' -f4)
METHOD_LABEL=$(echo "$DETAIL_RESPONSE" | grep -o '"methodLabel":"[^"]*' | cut -d'"' -f4)
EXPERIENCE_IMPROVE_LABEL=$(echo "$DETAIL_RESPONSE" | grep -o '"experienceImproveLabel":"[^"]*' | cut -d'"' -f4)
QUALITY_TOPIC_LABEL=$(echo "$DETAIL_RESPONSE" | grep -o '"qualityTopicLabel":"[^"]*' | cut -d'"' -f4)

echo "【主题类型】"
if [ -n "$SUBJECT_TYPE_LABEL" ]; then
    echo -e "  ${GREEN}✅ subjectTypeLabel: $SUBJECT_TYPE_LABEL${NC}"
else
    echo -e "  ${RED}❌ subjectTypeLabel: 缺失${NC}"
fi
echo ""

echo "【运用手法】"
if [ -n "$METHOD_LABEL" ]; then
    echo -e "  ${GREEN}✅ methodLabel: $METHOD_LABEL${NC}"
else
    echo -e "  ${RED}❌ methodLabel: 缺失${NC}"
fi
echo ""

echo "【改善就医环境】"
if [ -n "$EXPERIENCE_IMPROVE_LABEL" ]; then
    echo -e "  ${GREEN}✅ experienceImproveLabel: $EXPERIENCE_IMPROVE_LABEL${NC}"
    echo -e "  ${YELLOW}📝 前端应该显示: $EXPERIENCE_IMPROVE_LABEL${NC}"
else
    echo -e "  ${RED}❌ experienceImproveLabel: 缺失${NC}"
fi
echo ""

echo "【医疗质量相关主题】"
if [ -n "$QUALITY_TOPIC_LABEL" ]; then
    echo -e "  ${GREEN}✅ qualityTopicLabel: $QUALITY_TOPIC_LABEL${NC}"
    echo -e "  ${YELLOW}📝 前端应该显示: $QUALITY_TOPIC_LABEL${NC}"
else
    echo -e "  ${RED}❌ qualityTopicLabel: 缺失${NC}"
fi
echo ""

echo "================================================================================"
echo "前端代码示例"
echo "================================================================================"
echo ""

echo -e "${RED}❌ 错误的前端代码（会显示Code）:${NC}"
echo '```vue'
echo '<div>{{ activityInfo.experienceImproveCode }}</div>'
echo '<div>{{ activityInfo.qualityTopicCode }}</div>'
echo '```'
echo ""

echo -e "${GREEN}✅ 正确的前端代码（会显示Label）:${NC}"
echo '```vue'
echo '<div>{{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode }}</div>'
echo '<div>{{ activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode }}</div>'
echo '```'
echo ""

echo "================================================================================"
echo "测试完成"
echo "================================================================================"

if [ -n "$EXPERIENCE_IMPROVE_LABEL" ] && [ -n "$QUALITY_TOPIC_LABEL" ]; then
    echo -e "${GREEN}✅ 后端API正确返回了所有Label字段${NC}"
    echo -e "${GREEN}✅ 前端可以直接使用Label字段${NC}"
    echo ""
    echo -e "${YELLOW}如果前端显示的是Code（如 experience_1），说明前端代码有问题！${NC}"
else
    echo -e "${RED}❌ 部分Label字段缺失，请联系后端开发人员${NC}"
fi
