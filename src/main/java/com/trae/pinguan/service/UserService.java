package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.web.dto.*;
import java.time.LocalDateTime;
import java.util.Random;
import javax.persistence.criteria.Predicate;
import java.util.ArrayList;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserAccountRepository userAccountRepository;
    private final InstitutionRepository institutionRepository;
    private final com.trae.pinguan.service.ConstInitInstitutionService constInitInstitutionService;
    private final PasswordService passwordService;
    private final SmsService smsService;

    @Transactional
    public UserAccount loginOrCreate(LoginRequest request) {
        UserAccount existing = userAccountRepository.findByPhone(request.getPhone()).orElse(null);
        Institution institution = null;
        if (request.getInstitutionId() != null) {
            institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        }
        if (existing == null) {
            return userAccountRepository.save(UserAccount.builder()
                    .phone(request.getPhone())
                    .name(request.getName())
                    .title(request.getTitle())
                    .role(request.getRole())
                    .institution(institution)
                    .reviewerGroupCode(request.getReviewerGroupCode())
                    .interviewGroupCode(request.getInterviewGroupCode())
                    .expertBackground(request.getExpertBackground())
                    .createdAt(LocalDateTime.now())
                    .build());
        }
        if (request.getName() != null) {
            existing.setName(request.getName());
        }
        if (request.getTitle() != null) {
            existing.setTitle(request.getTitle());
        }
        if (request.getRole() != null) {
            existing.setRole(request.getRole());
        }
        if (institution != null) {
            existing.setInstitution(institution);
        }
        if (request.getReviewerGroupCode() != null) {
            existing.setReviewerGroupCode(request.getReviewerGroupCode());
        }
        if (request.getInterviewGroupCode() != null) {
            existing.setInterviewGroupCode(request.getInterviewGroupCode());
        }
        if (request.getExpertBackground() != null) {
            existing.setExpertBackground(request.getExpertBackground());
        }
        UserAccount saved = userAccountRepository.save(existing);
        // 强制加载institution以避免LazyInitializationException
        if (saved.getInstitution() != null) {
            saved.getInstitution().getName();
        }
        return saved;
    }
    
    /**
     * 用户注册（带密码）
     */
    @Transactional
    public UserAccount register(RegisterRequest request) {
        // 1. 验证手机号是否已注册
        if (userAccountRepository.findByPhone(request.getPhone()).isPresent()) {
            throw new IllegalArgumentException("该手机号已注册");
        }
        
        // 2. 验证两次密码是否一致
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("两次输入的密码不一致");
        }
        
        // 3. 激活机构（从 const_init_institutions 同步到 institutions）
        // request.getInstitutionId() 现在是 const_init_institutions 的 ID
        Long activeInstitutionId = constInitInstitutionService.activateInstitution(request.getInstitutionId());
        
        Institution institution = institutionRepository.findById(activeInstitutionId)
                .orElseThrow(() -> new IllegalArgumentException("机构激活失败"));
        
        // 4. 加密密码
        String encodedPassword = passwordService.encode(request.getPassword());
        
        // 5. 创建用户
        UserAccount user = UserAccount.builder()
                .phone(request.getPhone())
                .password(encodedPassword)
                .name(request.getName())
                .title(request.getTitle())
                .role(request.getRole())
                .institution(institution)
                .reviewerGroupCode(request.getReviewerGroupCode())
                .interviewGroupCode(request.getInterviewGroupCode())
                .expertBackground(request.getExpertBackground())
                .createdAt(LocalDateTime.now())
                .build();
        
        UserAccount saved = userAccountRepository.save(user);
        
        // 强制加载institution
        if (saved.getInstitution() != null) {
            saved.getInstitution().getName();
        }
        
        return saved;
    }
    
    /**
     * 用户登录（验证密码）
     */
    @Transactional
    public UserAccount login(LoginWithPasswordRequest request) {
        // 1. 查找用户
        UserAccount user = userAccountRepository.findByPhone(request.getPhone())
                .orElseThrow(() -> new IllegalArgumentException("手机号或密码错误"));
        
        // 2. 检查账号是否被禁用
        if (Boolean.FALSE.equals(user.getEnabled())) {
            throw new IllegalArgumentException("该账号已被禁用，请联系管理员");
        }
        
        // 3. 验证密码
        if (user.getPassword() == null) {
            throw new IllegalArgumentException("该账号尚未设置密码，请联系管理员");
        }
        
        if (!passwordService.matches(request.getPassword(), user.getPassword())) {
            throw new IllegalArgumentException("手机号或密码错误");
        }
        
        // 4. 更新最后登录时间
        user.setLastLoginAt(LocalDateTime.now());
        userAccountRepository.save(user);
        
        // 5. 强制加载institution
        if (user.getInstitution() != null) {
            user.getInstitution().getName();
        }
        
        return user;
    }
    
    /**
     * 修改密码
     */
    @Transactional
    public void changePassword(Long userId, ChangePasswordRequest request) {
        // 1. 验证新密码和确认密码是否一致
        if (!request.getNewPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("两次输入的新密码不一致");
        }
        
        // 2. 查找用户
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        
        // 3. 验证旧密码
        if (user.getPassword() == null) {
            throw new IllegalArgumentException("该账号尚未设置密码");
        }
        
        if (!passwordService.matches(request.getOldPassword(), user.getPassword())) {
            throw new IllegalArgumentException("旧密码错误");
        }
        
        // 4. 更新密码
        String encodedPassword = passwordService.encode(request.getNewPassword());
        user.setPassword(encodedPassword);
        userAccountRepository.save(user);
    }
    
    /**
     * 用户注册（短信验证码方式）
     */
    @Transactional
    public UserAccount registerWithSms(RegisterWithSmsRequest request) {
        // 1. 验证短信验证码
        if (!smsService.verifyCode(request.getPhone(), request.getSmsCode())) {
            throw new IllegalArgumentException("验证码错误或已过期");
        }
        
        // 2. 验证手机号是否已注册
        if (userAccountRepository.findByPhone(request.getPhone()).isPresent()) {
            throw new IllegalArgumentException("该手机号已注册");
        }
        
        // 3. 验证两次密码是否一致
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("两次输入的密码不一致");
        }
        
        // 4. 验证机构是否存在
        Institution institution = institutionRepository.findById(request.getInstitutionId())
                .orElseThrow(() -> new IllegalArgumentException("所选机构不存在"));
        
        // 5. 加密密码
        String encodedPassword = passwordService.encode(request.getPassword());
        
        // 6. 创建用户
        UserAccount user = UserAccount.builder()
                .phone(request.getPhone())
                .password(encodedPassword)
                .name(request.getName())
                .title(request.getTitle())
                .role(request.getRole())
                .institution(institution)
                .reviewerGroupCode(request.getReviewerGroupCode())
                .interviewGroupCode(request.getInterviewGroupCode())
                .expertBackground(request.getExpertBackground())
                .createdAt(LocalDateTime.now())
                .build();
        
        UserAccount saved = userAccountRepository.save(user);
        
        // 强制加载institution
        if (saved.getInstitution() != null) {
            saved.getInstitution().getName();
        }
        
        return saved;
    }
    
    /**
     * 管理员创建评委账号
     */
    @Transactional
    public CreateReviewerResponse createReviewer(CreateReviewerRequest request) {
        // 1. 验证手机号是否已注册
        if (userAccountRepository.findByPhone(request.getPhone()).isPresent()) {
            throw new IllegalArgumentException("该手机号已注册");
        }
        
        // 2. 验证机构是否存在
        Institution institution = institutionRepository.findById(request.getInstitutionId())
                .orElseThrow(() -> new IllegalArgumentException("所选机构不存在"));
        
        // 3. 生成初始密码（6位随机数字）
        String initialPassword = generateInitialPassword();
        String encodedPassword = passwordService.encode(initialPassword);
        
        // 4. 创建评委账号
        UserAccount reviewer = UserAccount.builder()
                .phone(request.getPhone())
                .password(encodedPassword)
                .name(request.getName())
                .title(request.getTitle())
                .role(RoleType.REVIEWER)
                .institution(institution)
                .reviewerGroupCode(request.getReviewerGroupCode())
                .interviewGroupCode(request.getInterviewGroupCode())
                .expertBackground(request.getExpertBackground())
                .enabled(true)
                .createdAt(LocalDateTime.now())
                .build();
        
        UserAccount saved = userAccountRepository.save(reviewer);
        
        return CreateReviewerResponse.builder()
                .userId(saved.getId())
                .phone(saved.getPhone())
                .name(saved.getName())
                .initialPassword(initialPassword)
                .institutionName(institution.getName())
                .build();
    }
    
    /**
     * 查询用户列表（支持多条件筛选）
     */
    @Transactional(readOnly = true)
    public Page<UserDTO> queryUsers(UserQueryRequest request) {
        Specification<UserAccount> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            // 手机号模糊搜索
            if (request.getPhone() != null && !request.getPhone().trim().isEmpty()) {
                predicates.add(cb.like(root.get("phone"), "%" + request.getPhone() + "%"));
            }
            
            // 姓名模糊搜索
            if (request.getName() != null && !request.getName().trim().isEmpty()) {
                predicates.add(cb.like(root.get("name"), "%" + request.getName() + "%"));
            }
            
            // 角色筛选
            if (request.getRole() != null) {
                predicates.add(cb.equal(root.get("role"), request.getRole()));
            }
            
            // 机构筛选
            if (request.getInstitutionId() != null) {
                predicates.add(cb.equal(root.get("institution").get("id"), request.getInstitutionId()));
            }
            
            // 启用状态筛选
            if (request.getEnabled() != null) {
                predicates.add(cb.equal(root.get("enabled"), request.getEnabled()));
            }
            
            return cb.and(predicates.toArray(new Predicate[0]));
        };
        
        Pageable pageable = PageRequest.of(
            request.getPage(), 
            request.getSize(),
            Sort.by(Sort.Direction.DESC, "createdAt")
        );
        
        Page<UserAccount> users = userAccountRepository.findAll(spec, pageable);
        
        // 转换为DTO
        return users.map(user -> {
            // 强制加载institution
            if (user.getInstitution() != null) {
                user.getInstitution().getName();
            }
            return UserDTO.from(user);
        });
    }
    
    /**
     * 禁用用户
     */
    @Transactional
    public void disableUser(Long userId) {
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        
        if (Boolean.FALSE.equals(user.getEnabled())) {
            throw new IllegalArgumentException("该用户已被禁用");
        }
        
        user.setEnabled(false);
        userAccountRepository.save(user);
    }
    
    /**
     * 启用用户
     */
    @Transactional
    public void enableUser(Long userId) {
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        
        if (Boolean.TRUE.equals(user.getEnabled())) {
            throw new IllegalArgumentException("该用户已是启用状态");
        }
        
        user.setEnabled(true);
        userAccountRepository.save(user);
    }
    
    /**
     * 获取用户详情
     */
    @Transactional(readOnly = true)
    public UserDTO getUserDetail(Long userId) {
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        
        // 强制加载institution
        if (user.getInstitution() != null) {
            user.getInstitution().getName();
        }
        
        return UserDTO.from(user);
    }
    
    /**
     * 统计用户数量
     */
    @Transactional(readOnly = true)
    public long countUsers(RoleType role, Boolean enabled) {
        return userAccountRepository.countByRoleAndEnabled(role, enabled);
    }
    
    /**
     * 根据手机号查找用户
     */
    @Transactional(readOnly = true)
    public UserAccount findByPhone(String phone) {
        return userAccountRepository.findByPhone(phone).orElse(null);
    }
    
    /**
     * OPS重置用户密码（直接重置，无需旧密码）
     */
    @Transactional
    public String resetPassword(Long userId) {
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        String newPassword = generateInitialPassword();
        user.setPassword(passwordService.encode(newPassword));
        userAccountRepository.save(user);
        return newPassword;
    }

    /**
     * OPS重置用户手机号
     */
    @Transactional
    public void resetPhone(Long userId, String newPhone) {
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        if (userAccountRepository.findByPhone(newPhone).isPresent()) {
            throw new IllegalArgumentException("该手机号已被其他用户使用");
        }
        user.setPhone(newPhone);
        userAccountRepository.save(user);
    }

    /**
     * 生成6位随机初始密码
     */
    private String generateInitialPassword() {
        Random random = new Random();
        return String.format("%06d", random.nextInt(1000000));
    }

    @Transactional
    public void confirmNotice(Long userId) {
        UserAccount user = userAccountRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        if (user.getNoticeConfirmedAt() == null) {
            user.setNoticeConfirmedAt(LocalDateTime.now());
            userAccountRepository.save(user);
        }
    }
}
