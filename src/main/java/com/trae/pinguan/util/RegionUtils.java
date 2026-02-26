package com.trae.pinguan.util;

import java.util.*;

/**
 * 地区工具类 - 处理市级和区县级的映射关系
 */
public class RegionUtils {
    
    /**
     * 城市到区县的映射
     */
    private static final Map<String, List<String>> CITY_TO_DISTRICTS = new HashMap<>();
    
    static {
        // 丽水市 - 9个区县, 1,849家机构
        CITY_TO_DISTRICTS.put("丽水市", Arrays.asList(
            "莲都区", "青田县", "缙云县", "遂昌县", "松阳县", "云和县",
            "庆元县", "景宁畲族自治县", "龙泉市"
        ));
        
        // 台州市 - 9个区县, 3,728家机构
        CITY_TO_DISTRICTS.put("台州市", Arrays.asList(
            "椒江区", "黄岩区", "路桥区", "三门县", "天台县", "仙居县",
            "温岭市", "临海市", "玉环市"
        ));
        
        // 嘉兴市 - 7个区县, 1,651家机构
        CITY_TO_DISTRICTS.put("嘉兴市", Arrays.asList(
            "南湖区", "秀洲区", "嘉善县", "海盐县", "海宁市", "平湖市", "桐乡市"
        ));
        
        // 宁波市 - 10个区县, 4,563家机构
        CITY_TO_DISTRICTS.put("宁波市", Arrays.asList(
            "海曙区", "江北区", "北仑区", "镇海区", "鄞州区", "奉化区",
            "象山县", "宁海县", "余姚市", "慈溪市"
        ));
        
        // 杭州市 - 13个区县, 6,298家机构
        // 注意: 原有的"下城区"、"江干区"已撤并，新增"临平区"、"钱塘区"
        CITY_TO_DISTRICTS.put("杭州市", Arrays.asList(
            "上城区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区",
            "临平区", "钱塘区", "富阳区", "临安区", "桐庐县", "淳安县", "建德市"
        ));
        
        // 温州市 - 12个区县, 6,118家机构
        // 注意: 包含新设立的"龙港市"（原为龙港镇，2019年撤镇设市）
        CITY_TO_DISTRICTS.put("温州市", Arrays.asList(
            "鹿城区", "龙湾区", "瓯海区", "洞头区", "永嘉县", "平阳县",
            "苍南县", "文成县", "泰顺县", "瑞安市", "乐清市", "龙港市"
        ));
        
        // 湖州市 - 5个区县, 1,174家机构
        CITY_TO_DISTRICTS.put("湖州市", Arrays.asList(
            "吴兴区", "南浔区", "德清县", "长兴县", "安吉县"
        ));
        
        // 绍兴市 - 6个区县, 2,935家机构
        CITY_TO_DISTRICTS.put("绍兴市", Arrays.asList(
            "越城区", "柯桥区", "上虞区", "新昌县", "诸暨市", "嵊州市"
        ));
        
        // 舟山市 - 4个区县, 585家机构
        CITY_TO_DISTRICTS.put("舟山市", Arrays.asList(
            "定海区", "普陀区", "岱山县", "嵊泗县"
        ));
        
        // 衢州市 - 6个区县, 1,766家机构
        CITY_TO_DISTRICTS.put("衢州市", Arrays.asList(
            "柯城区", "衢江区", "常山县", "开化县", "龙游县", "江山市"
        ));
        
        // 金华市 - 9个区县, 4,864家机构
        CITY_TO_DISTRICTS.put("金华市", Arrays.asList(
            "婺城区", "金东区", "武义县", "浦江县", "磐安县", "兰溪市",
            "义乌市", "东阳市", "永康市"
        ));
    }
    
    /**
     * 将市级名称扩展为包含的所有区县
     * 例如：expandCityToDistricts("杭州市") 
     *   -> ["上城区", "下城区", "江干区", ...]
     * 
     * @param city 市级名称（如"杭州市"）
     * @return 包含的所有区县列表，如果不是市级或未配置则返回包含原值的列表
     */
    public static List<String> expandCityToDistricts(String city) {
        if (city == null || city.trim().isEmpty()) {
            return Collections.emptyList();
        }
        
        // 如果是已配置的城市，返回其区县
        if (CITY_TO_DISTRICTS.containsKey(city)) {
            return new ArrayList<>(CITY_TO_DISTRICTS.get(city));
        }
        
        // 如果不是配置的城市，返回原值（可能本身就是区县或其他市）
        return Collections.singletonList(city);
    }
    
    /**
     * 智能扩展地区查询
     * 支持：市级（扩展为区县）、区县级（直接返回）、模糊匹配（包含关键词的市）
     * 
     * @param regionInput 用户输入的地区（如"杭州"、"杭州市"、"上城区"）
     * @return 应该查询的地区列表
     */
    public static List<String> expandRegionQuery(String regionInput) {
        if (regionInput == null || regionInput.trim().isEmpty()) {
            return Collections.emptyList();
        }
        
        String input = regionInput.trim();
        
        // 1. 精确匹配市级
        if (CITY_TO_DISTRICTS.containsKey(input)) {
            return new ArrayList<>(CITY_TO_DISTRICTS.get(input));
        }
        
        // 2. 模糊匹配市级（如"杭州" -> "杭州市"）
        if (!input.endsWith("市") && !input.endsWith("区") && !input.endsWith("县")) {
            String cityKey = input + "市";
            if (CITY_TO_DISTRICTS.containsKey(cityKey)) {
                return new ArrayList<>(CITY_TO_DISTRICTS.get(cityKey));
            }
        }
        
        // 3. 不是市级，直接返回原值（可能是区县）
        return Collections.singletonList(input);
    }
    
    /**
     * 获取所有市级列表
     */
    public static List<String> getAllCities() {
        List<String> cities = new ArrayList<>(CITY_TO_DISTRICTS.keySet());
        Collections.sort(cities);
        return cities;
    }
    
    /**
     * 获取指定市的所有区县
     */
    public static List<String> getDistrictsByCity(String city) {
        return CITY_TO_DISTRICTS.getOrDefault(city, Collections.emptyList());
    }
    
    /**
     * 检查是否为市级
     */
    public static boolean isCity(String region) {
        return CITY_TO_DISTRICTS.containsKey(region);
    }
    
    /**
     * 从区县名推断所属城市
     * 例如："上城区" -> "杭州市"
     */
    public static String getCityFromRegion(String region) {
        if (region == null || region.trim().isEmpty()) {
            return null;
        }
        
        // 遍历所有城市的区县列表
        for (Map.Entry<String, List<String>> entry : CITY_TO_DISTRICTS.entrySet()) {
            if (entry.getValue().contains(region)) {
                return entry.getKey();
            }
        }
        
        return null;
    }
}
