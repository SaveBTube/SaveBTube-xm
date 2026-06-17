<template>
  <div class="settings-page">
    <!-- 设置标签页 -->
    <div class="settings-tabs">
      <button 
        v-for="tab in visibleTabs" 
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.name }}
      </button>
    </div>
    
    <!-- 账户信息 -->
    <div v-if="activeTab === 'account'" class="settings-content card">
      <h3 class="section-title">👤 账户信息</h3>
      
      <div class="avatar-section">
        <div class="avatar-preview">
          <img v-if="userInfo?.avatar" :src="userInfo.avatar" class="avatar-img" />
          <div v-else class="avatar-circle">{{ userInfo?.username?.charAt(0)?.toUpperCase() || 'A' }}</div>
        </div>
        <div class="avatar-actions">
          <input ref="avatarInput" type="file" accept="image/png, image/jpeg" style="display:none" @change="onAvatarSelected" />
          <button class="btn btn-primary btn-sm" @click="$refs.avatarInput.click()">选择图片</button>
          <p class="avatar-hint">支持 JPG/PNG 格式，最大 1.5MB</p>
        </div>
      </div>
      
      <div class="info-grid">
        <div class="info-item">
          <label>用户名</label>
          <input type="text" class="input" :value="userInfo?.username" readonly />
        </div>
        <div class="info-item">
          <label>角色</label>
          <input type="text" class="input" :value="userInfo?.role === 'admin' ? '管理员' : '普通用户'" readonly />
        </div>
      </div>
    </div>
    
    <!-- 用户管理 -->
    <div v-if="activeTab === 'users'" class="settings-content card">
      <div class="settings-header">
        <h3 class="section-title">👥 用户列表</h3>
        <button class="btn btn-primary btn-sm" @click="openCreateUserModal">➕ 添加用户</button>
      </div>
      
      <table class="table">
        <thead>
          <tr>
            <th>用户</th>
            <th>角色</th>
            <th>注册时间</th>
            <th>下载次数</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>
              <div class="user-cell">
                <div class="user-avatar-sm">{{ user.username.charAt(0).toUpperCase() }}</div>
                <span>{{ user.username }}</span>
              </div>
            </td>
            <td>
              <span class="badge" :class="user.role === 'admin' ? 'badge-info' : 'badge-success'">
                {{ user.role === 'admin' ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>{{ user.download_count || 0 }}</td>
            <td>
              <span class="badge" :class="user.is_active ? 'badge-success' : 'badge-danger'">
                {{ user.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>
              <div class="action-btns">
                <button class="btn btn-sm btn-gray" @click="editUser(user)">编辑</button>
                <button class="btn btn-sm btn-warning" @click="toggleUserStatus(user)">
                  {{ user.is_active ? '禁用' : '启用' }}
                </button>
                <button v-if="user.id !== 1" class="btn btn-sm btn-danger" @click="deleteUser(user)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
        <div class="modal-card">
          <div class="modal-header">
            <h3>{{ isEditUser ? '编辑用户' : '添加用户' }}</h3>
            <button class="btn btn-gray btn-sm" @click="closeUserModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-item">
              <label>用户名</label>
              <input v-model="userForm.username" type="text" class="input" :readonly="isEditUser" placeholder="输入用户名" />
            </div>
            <div class="form-item" v-if="!isEditUser">
              <label>密码</label>
              <input v-model="userForm.password" type="password" class="input" placeholder="输入密码" />
            </div>
            <div class="form-item">
              <label>角色</label>
              <select v-model="userForm.role" class="input">
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            <div class="form-item">
              <label>状态</label>
              <select v-model="userForm.is_active" class="input">
                <option :value="1">启用</option>
                <option :value="0">禁用</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-gray" @click="closeUserModal">取消</button>
            <button class="btn btn-primary" @click="saveUser">{{ isEditUser ? '保存' : '添加' }}</button>
          </div>
        </div>
      </div>

      <!-- 邀请码管理 -->
      <div class="invite-section mt-3">
        <h4>🎫 邀请码管理</h4>
        <div class="invite-actions">
          <button class="btn btn-primary btn-sm" @click="generateInviteCode">➕ 生成邀请码</button>
        </div>
        <table class="table mt-2">
          <thead>
            <tr>
              <th>邀请码</th>
              <th>创建者</th>
              <th>状态</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="code in inviteCodes" :key="code.id">
              <td><code>{{ code.code }}</code></td>
              <td>{{ code.created_by_username }}</td>
              <td>
                <span class="badge" :class="code.used_by ? 'badge-warning' : 'badge-success'">
                  {{ code.used_by ? '已使用' : '未使用' }}
                </span>
              </td>
              <td>{{ formatDate(code.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 安全配置 -->
    <div v-if="activeTab === 'security'" class="settings-content card">
      <h3 class="section-title">🔒 安全配置</h3>
      
      <div class="security-section">
        <h4>修改密码</h4>
        <div class="form-grid">
          <div class="form-item">
            <label>当前密码</label>
            <input v-model="passwordForm.old_password" type="password" class="input" />
          </div>
          <div class="form-item">
            <label>新密码</label>
            <input v-model="passwordForm.new_password" type="password" class="input" />
          </div>
          <div class="form-item">
            <label>确认密码</label>
            <input v-model="passwordForm.confirm_password" type="password" class="input" />
          </div>
        </div>
        <button class="btn btn-primary" @click="changePassword">保存更改</button>
      </div>
      
      <div class="security-section mt-3">
        <div class="section-header">
          <div>
            <h4>双因子认证</h4>
            <p class="section-desc">启用后登录时需要输入 Authenticator App 生成的 6 位验证码</p>
          </div>
          <span class="badge badge-warning">未启用</span>
        </div>
        <button class="btn btn-primary mt-2">开启双因子认证</button>
      </div>
    </div>

    <!-- ==================== 插件管理（新增） ==================== -->
    <div v-if="activeTab === 'plugins'" class="settings-content card">
      <h3 class="section-title">🧩 浏览器插件管理</h3>

      <!-- 插件信息卡片 -->
      <div class="plugin-hero">
        <div class="plugin-icon-wrap">
          <span class="plugin-icon">⚡</span>
        </div>
        <div class="plugin-info-text">
          <h4 class="plugin-name">{{ pluginInfo.name || 'Bosco Tsang 快速下载' }}</h4>
          <p class="plugin-desc">{{ pluginInfo.description || '将当前页面链接发送到 Bosco Tsang 下载系统' }}</p>
          <div class="plugin-meta">
            <span class="meta-tag">v{{ pluginInfo.version || '1.2.0' }}</span>
            <span class="meta-tag" v-for="b in (pluginInfo.supports || ['Chrome','Edge'])" :key="b">{{ b }}</span>
          </div>
        </div>
        <div class="plugin-action">
          <button class="btn-download-plugin" @click="downloadPlugin" :disabled="pluginDownloading">
            <span v-if="pluginDownloading" class="spinner"></span>
            {{ pluginDownloading ? '打包中...' : '📦 下载插件' }}
          </button>
        </div>
      </div>

      <!-- 功能特性 -->
      <div class="feature-grid">
        <div class="feature-card" v-for="(feat, idx) in (pluginInfo.features || defaultFeatures)" :key="idx">
          <span class="feat-icon">{{ featureIcons[idx] || '✨' }}</span>
          <span class="feat-text">{{ feat }}</span>
        </div>
      </div>

      <!-- 安装步骤 -->
      <div class="install-guide">
        <h4 class="guide-title">📖 安装指南</h4>
        <div class="steps">
          <div class="step" v-for="(step, i) in installSteps" :key="i">
            <div class="step-num">{{ i + 1 }}</div>
            <div class="step-body">
              <strong>{{ step.title }}</strong>
              <p>{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 配置说明 -->
      <div class="config-guide">
        <h4 class="guide-title">🔧 配置说明</h4>
        <div class="config-cards">
          <div class="config-card">
            <code class="config-label">服务地址</code>
            <span class="config-value">{{ currentServerUrl || window.location.origin }}</span>
            <p class="config-hint">填写您部署的 Bosco Tsang 服务地址</p>
          </div>
          <div class="config-card">
            <code class="config-label">API Key</code>
            <span class="config-value">访问密钥 → 创建</span>
            <p class="config-hint">在本页「🔑 访问密钥」标签创建并复制完整 Key</p>
          </div>
        </div>
      </div>
      
      <!-- iOS 快捷指令 -->
      <div class="shortcut-section">
        <div class="shortcut-header">
          <div class="shortcut-icon-wrap">
            <span class="shortcut-icon">📱</span>
          </div>
          <div class="shortcut-info">
            <h4 class="shortcut-name">iOS 快捷指令</h4>
            <p class="shortcut-desc">在 iPhone/iPad 上通过分享菜单一键下载</p>
            <div class="shortcut-tags">
              <span class="tag">iOS 13+</span>
              <span class="tag">分享菜单</span>
              <span class="tag">3000+ 平台</span>
            </div>
          </div>
        </div>
        
        <div class="shortcut-features">
          <div class="shortcut-feature">
            <span class="feat-icon">📲</span>
            <span>分享菜单集成</span>
          </div>
          <div class="shortcut-feature">
            <span class="feat-icon">🎬</span>
            <span>支持 3000+ 平台</span>
          </div>
          <div class="shortcut-feature">
            <span class="feat-icon">🔔</span>
            <span>实时下载通知</span>
          </div>
          <div class="shortcut-feature">
            <span class="feat-icon">🔒</span>
            <span>API Key 安全认证</span>
          </div>
        </div>
        
        <div class="shortcut-actions">
          <button class="btn-install-shortcut" @click="installShortcut">
            📲 安装快捷指令
          </button>
          <button class="btn-view-guide" @click="viewShortcutGuide">
            📖 查看指南
          </button>
        </div>
        
        <div class="shortcut-steps">
          <h5 class="steps-title">📝 安装步骤</h5>
          <div class="step-list">
            <div class="step-item">
              <span class="step-number">1</span>
              <span>点击“安装快捷指令”按钮</span>
            </div>
            <div class="step-item">
              <span class="step-number">2</span>
              <span>在弹出窗口中点击“添加快捷指令”</span>
            </div>
            <div class="step-item">
              <span class="step-number">3</span>
              <span>修改服务器地址为您的服务地址</span>
            </div>
            <div class="step-item">
              <span class="step-number">4</span>
              <span>首次使用时输入 API Key</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ==================== 代理与下载（全新设计） ==================== -->
    <div v-if="activeTab === 'proxy'" class="settings-content card">
      <h3 class="section-title">🌐 代理与网络</h3>

      <!-- 代理控制面板 - 高大上设计 -->
      <div class="proxy-panel" :class="{ 'proxy-enabled': settingsForm.proxy_enabled }">
        
        <!-- 顶部：开关 + 状态指示 -->
        <div class="proxy-header">
          <div class="proxy-status-area">
            <div class="proxy-toggle-wrap" @click="toggleProxy">
              <div class="proxy-toggle-track" :class="{ active: settingsForm.proxy_enabled }">
                <div class="proxy-toggle-thumb"></div>
              </div>
            </div>
            <div class="proxy-status-info">
              <span class="status-label">{{ settingsForm.proxy_enabled ? '代理已开启' : '代理已关闭' }}</span>
              <div class="status-dots">
                <span class="dot" :class="{ active: settingsForm.proxy_enabled }"></span>
                <span class="pulse-ring" v-if="settingsForm.proxy_enabled"></span>
              </div>
            </div>
          </div>
          
          <!-- 当前代理地址预览（仅展开时显示） -->
          <transition name="slide-fade">
            <div class="proxy-preview" v-if="settingsForm.proxy_enabled">
              <div class="preview-chip" v-if="settingsForm.http_proxy">
                <span class="chip-label">HTTP</span>
                <span class="chip-val">{{ settingsForm.http_proxy }}</span>
              </div>
              <div class="preview-chip" v-if="settingsForm.https_proxy">
                <span class="chip-label https">HTTPS</span>
                <span class="chip-val">{{ settingsForm.https_proxy }}</span>
              </div>
              <div class="preview-chip empty" v-if="!settingsForm.http_proxy && !settingsForm.https_proxy">
                <span class="chip-val">未配置代理地址</span>
              </div>
            </div>
          </transition>
        </div>

        <!-- 展开的配置区域 -->
        <transition name="expand">
          <div class="proxy-config-body" v-show="settingsForm.proxy_enabled">
            <div class="config-divider">
              <span>代理配置</span>
            </div>
            
            <div class="proxy-input-group">
              <div class="input-field">
                <label class="field-label">
                  <span class="field-icon">🔗</span> HTTP 代理
                </label>
                <div class="input-with-prefix">
                  <span class="input-prefix">http://</span>
                  <input 
                    v-model="httpProxyRaw" 
                    type="text" 
                    class="input proxy-input" 
                    placeholder="127.0.0.1:7890"
                  />
                </div>
                <p class="field-hint">用于普通 HTTP 请求的代理服务器</p>
              </div>

              <div class="input-field">
                <label class="field-label">
                  <span class="field-icon">🔒</span> HTTPS 代理
                </label>
                <div class="input-with-prefix">
                  <span class="input-prefix">http://</span>
                  <input 
                    v-model="httpsProxyRaw" 
                    type="text" 
                    class="input proxy-input" 
                    placeholder="127.0.0.1:7890"
                  />
                </div>
                <p class="field-hint">用于 HTTPS 加密连接的代理（留空则复用 HTTP 代理）</p>
              </div>
            </div>

            <!-- 操作按钮区 -->
            <div class="proxy-actions-bar">
              <button class="btn btn-primary" @click="saveProxySettings" :disabled="!isAdmin">
                <span class="btn-icon">💾</span> 保存配置
              </button>
              <button class="btn btn-outline" @click="testProxyConnection" v-if="isAdmin">
                <span class="btn-icon">🔌</span> 连接测试
              </button>
            </div>
          </div>
        </transition>

        <!-- 收起状态提示 -->
        <div class="proxy-collapsed-hint" v-if="!settingsForm.proxy_enabled">
          <span class="hint-icon">💤</span>
          <span>关闭时代理功能将不会生效，所有请求直连目标服务器</span>
        </div>
      </div>
    </div>

    <!-- 平台设置 -->
    <div v-if="activeTab === 'platforms'" class="settings-content card">
      <div class="settings-header">
        <h3 class="section-title">🧩 平台设置</h3>
      </div>
      <div class="platform-tabs">
        <button
          v-for="service in platformTabs"
          :key="service.id"
          class="tab-btn platform-tab"
          :class="{ active: activeServiceTab === service.id }"
          @click="activeServiceTab = service.id"
        >
          {{ service.name }}
        </button>
      </div>
      <div class="platform-panel">
        <div v-if="activeServiceTab === 'telegram'">
          <h4>Telegram 配置</h4>
          <div class="form-grid-2">
            <div class="form-item">
              <label>Bot Token</label>
              <input v-model="settingsForm.telegram_bot_token" type="text" class="input" placeholder="请输入 Telegram Bot Token" />
            </div>
            <div class="form-item">
              <label>允许的用户 ID</label>
              <input v-model="settingsForm.telegram_allowed_user_ids" type="text" class="input" placeholder="多个 ID 用英文逗号分隔" />
            </div>
            <div class="form-item">
              <label>API ID</label>
              <input v-model="settingsForm.telegram_api_id" type="text" class="input" placeholder="Telegram API ID" />
            </div>
            <div class="form-item">
              <label>API Hash</label>
              <input v-model="settingsForm.telegram_api_hash" type="text" class="input" placeholder="Telegram API Hash" />
            </div>
            <div class="form-item full-width">
              <label>会话 Session</label>
              <textarea v-model="settingsForm.telegram_session" class="input" rows="4" placeholder="Telegram 会话字符串"></textarea>
            </div>
          </div>
          
          <!-- Telegram 登录设置 -->
          <div class="telegram-login-section">
            <h5>🔐 Telegram 登录设置</h5>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-info">
                  <label class="toggle-label">启用 Telegram 登录</label>
                  <p class="toggle-desc">允许用户使用 Telegram 账号登录系统</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settingsForm.telegram_login_enabled" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <label class="toggle-label">允许下载功能</label>
                  <p class="toggle-desc">关闭后，Telegram 登录用户只能查看，不能下载</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settingsForm.telegram_login_download_enabled" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <button class="btn btn-primary" @click="savePlatformSettings">保存平台设置</button>
        </div>
        <div v-else-if="activeServiceTab === 'xtwitter'">
          <h4>🐦 X/Twitter 配置</h4>
          
          <div class="platform-info-banner">
            <p>📹 支持下载：视频、GIF、图片</p>
            <p>🔐 需要配置 Cookies 才能下载私密内容</p>
          </div>
          
          <div class="form-item">
            <label>Cookies 配置</label>
            <textarea 
              v-model="settingsForm.xtwitter_cookies" 
              class="input" 
              rows="8" 
              placeholder="粘贴 Netscape HTTP Cookie 格式或浏览器导出的 Cookies..."
            ></textarea>
            <p class="help-text">
              💡 <strong>如何获取 Cookies：</strong><br>
              1. 在浏览器中登录 X/Twitter<br>
              2. 使用浏览器扩展（如 EditThisCookie）导出 Cookies<br>
              3. 或使用 yt-dlp 格式：域名\tFALSE\t路径\tFALSE\t过期时间\t名称\t值
            </p>
          </div>
          
          <div class="twitter-download-options">
            <h5>下载选项</h5>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-info">
                  <label class="toggle-label">下载视频</label>
                  <p class="toggle-desc">自动下载推文中的视频和 GIF</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settingsForm.xtwitter_download_video" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <label class="toggle-label">下载图片</label>
                  <p class="toggle-desc">自动下载推文中的图片</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settingsForm.xtwitter_download_images" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <label class="toggle-label">最高画质</label>
                  <p class="toggle-desc">优先下载最高分辨率的视频</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settingsForm.xtwitter_best_quality" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <div class="form-item">
            <label>下载质量</label>
            <select v-model="settingsForm.xtwitter_quality" class="input">
              <option value="best">最佳质量</option>
              <option value="1080p">1080p</option>
              <option value="720p">720p</option>
              <option value="480p">480p</option>
              <option value="360p">360p</option>
            </select>
          </div>
          
          <button class="btn btn-primary" @click="savePlatformSettings">保存 X/Twitter 设置</button>
        </div>
        <div v-else-if="activeServiceTab === 'qqbot'">
          <h4>🤖 QQ 机器人配置</h4>
          <div class="platform-info-banner">
            <p>📡 基于 OneBot v11 协议（Lagrange / NapCat / go-cqhttp）</p>
            <p>🔗 需要先部署 OneBot 实现，然后配置 API 地址</p>
          </div>
          <div class="form-grid-2">
            <div class="form-item full-width">
              <label>OneBot HTTP API 地址</label>
              <input v-model="settingsForm.qq_bot_api_url" type="text" class="input" placeholder="http://localhost:3000" />
              <p class="form-hint">Lagrange/NapCat 的 HTTP API 地址，Docker 部署时使用容器名: http://bosco-qq-bot:8080</p>
            </div>
          </div>
          <div class="bot-status-card" v-if="botStatus.qq">
            <span class="status-dot" :class="botStatus.qq.enabled ? 'green' : 'gray'"></span>
            <span>{{ botStatus.qq.enabled ? '已启用' : '未启用' }}</span>
          </div>
          <button class="btn btn-primary" @click="savePlatformSettings">保存 QQ Bot 设置</button>
        </div>
        <div v-else-if="activeServiceTab === 'wechatbot'">
          <h4>💬 微信 ClawBot 配置</h4>
          <div class="platform-info-banner">
            <p>🔗 通过 Webhook 与 OpenClaw/ClawBot 集成</p>
            <p>📡 ClawBot 将消息转发到本系统，下载完成后自动回复</p>
          </div>
          <div class="form-grid-2">
            <div class="form-item full-width">
              <label>ClawBot 回调 URL</label>
              <input v-model="settingsForm.wechat_clawbot_callback_url" type="text" class="input" placeholder="https://your-clawbot-server/callback" />
              <p class="form-hint">ClawBot 接收消息的回调地址，用于主动发送下载完成通知</p>
            </div>
          </div>
          <div class="bot-status-card" v-if="botStatus.wechat">
            <span class="status-dot" :class="botStatus.wechat.enabled ? 'green' : 'gray'"></span>
            <span>{{ botStatus.wechat.enabled ? '已启用' : '未启用' }}</span>
          </div>
          <button class="btn btn-primary" @click="savePlatformSettings">保存微信 Bot 设置</button>
        </div>
        <div v-else class="platform-placeholder">
          <h4>{{ platformTabs.find(tab => tab.id === activeServiceTab)?.name }}</h4>
          <p>当前平台暂无可配置项。您可以在此处查看平台支持状态与说明。</p>
          <p>支持的平台包括：YouTube、B站、抖音、快手、QQ音乐、网易云音乐、Instagram 等。</p>
        </div>
      </div>
    </div>

    <!-- API密钥 -->
    <div v-if="activeTab === 'apikeys'" class="settings-content card">
      <h3 class="section-title">🔑 访问密钥</h3>
      
      <div class="api-key-create">
        <input v-model="newKeyNote" type="text" class="input" placeholder="备注名称（可选）" />
        <button class="btn btn-primary" @click="createApiKey">➕ 创建API Key</button>
      </div>
      
      <div v-if="createdKey" class="key-created-alert">
        <p><strong>⚠️ 请立即复制密钥，关闭后将无法再次查看完整密钥！</strong></p>
        <code class="key-display">{{ createdKey }}</code>
        <button class="btn btn-sm btn-primary mt-2" @click="copyKey">复制密钥</button>
      </div>
      
      <table class="table mt-3">
        <thead>
          <tr>
            <th>Key</th>
            <th>备注</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>最后使用</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="key in apiKeys" :key="key.id">
            <td><code>{{ key.key_prefix }}</code></td>
            <td>{{ key.note || '-' }}</td>
            <td>
              <span class="badge" :class="key.status === 'active' ? 'badge-success' : 'badge-warning'">
                {{ key.status === 'active' ? '已启用' : '已禁用' }}
              </span>
            </td>
            <td>{{ formatDate(key.created_at) }}</td>
            <td>{{ key.last_used ? formatDate(key.last_used) : '-' }}</td>
            <td>
              <div class="action-btns">
                <button class="btn btn-sm" :class="key.status === 'active' ? 'btn-warning' : 'btn-success'" @click="toggleKeyStatus(key)">
                  {{ key.status === 'active' ? '禁用' : '启用' }}
                </button>
                <button class="btn btn-sm btn-danger" @click="deleteKey(key)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { auth, users as usersApi, apiKeys as apiKeysApi, inviteCodes as inviteCodesApi, settings as settingsApi, plugin as pluginApi } from '@/utils/api.js'

const activeTab = ref('account')
const tabs = [
  { id: 'account', name: '账户信息', icon: '👤' },
  { id: 'plugins', name: '插件管理', icon: '🧩' },
  { id: 'users', name: '用户管理', icon: '👥' },
  { id: 'security', name: '安全配置', icon: '🔒' },
  { id: 'platforms', name: '平台设置', icon: '📦' },
  { id: 'proxy', name: '网络代理', icon: '🌐' },
  { id: 'apikeys', name: '访问密钥', icon: '🔑' }
]

const userInfo = ref({})
const users = ref([])
const isAdmin = computed(() => userInfo.value?.role === 'admin')
const visibleTabs = computed(() => tabs.filter(tab => ((tab.id !== 'proxy' && tab.id !== 'users' && tab.id !== 'platforms') || isAdmin.value)))
const apiKeys = ref([])
const inviteCodes = ref([])
const newKeyNote = ref('')
const createdKey = ref('')

// ==================== 插件管理状态 ====================
const pluginInfo = ref({})
const pluginDownloading = ref(false)
const currentServerUrl = ref('')
const defaultFeatures = [
  '右键快捷下载当前页面/链接',
  '自动填充当前标签页 URL',
  '支持自定义服务地址和 API Key',
  '多画质选择（最佳/720p/1080p/音频/图片）'
]
const featureIcons = ['⚡', '🔗', '🎯', '🎬']
const installSteps = [
  { title: '下载插件', desc: '点击上方「下载插件」按钮获取 .zip 压缩包' },
  { title: '解压文件', desc: '将下载的 zip 文件解压到本地文件夹' },
  { title: '加载插件', desc: '打开浏览器 chrome://extensions → 开启开发者模式 → 加载已解压的扩展程序' },
  { title: '配置使用', desc: '点击浏览器工具栏插件图标，填入服务地址与 API Key 即可使用' }
]

// ==================== 代理增强状态 ====================
const httpProxyRaw = ref('')
const httpsProxyRaw = ref('')

// 从完整URL中提取出不含协议前缀的部分
function stripProtocol(url) {
  if (!url) return ''
  return url.replace(/^https?:\/\//i, '')
}
function addProtocol(raw) {
  if (!raw) return ''
  const s = raw.trim()
  if (s.match(/^https?:\/\//i)) return s
  return 'http://' + s
}

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const settingsForm = ref({
  telegram_bot_token: '',
  telegram_allowed_user_ids: '',
  telegram_api_id: '',
  telegram_api_hash: '',
  telegram_session: '',
  telegram_login_enabled: false,
  telegram_login_download_enabled: false,
  xtwitter_cookies: '',
  xtwitter_download_video: true,
  xtwitter_download_images: true,
  xtwitter_best_quality: true,
  xtwitter_quality: 'best',
  proxy_enabled: false,
  http_proxy: '',
  https_proxy: '',
  // QQ Bot
  qq_bot_api_url: '',
  // 微信 ClawBot
  wechat_clawbot_callback_url: ''
})
const platformTabs = ref([
  { id: 'telegram', name: 'Telegram' },
  { id: 'netease', name: '网易云音乐' },
  { id: 'qqmusic', name: 'QQ音乐' },
  { id: 'applemusic', name: 'Apple Music' },
  { id: 'bilibili', name: 'B站' },
  { id: 'youtube', name: 'YouTube' },
  { id: 'xtwitter', name: 'X/Twitter' },
  { id: 'douyin', name: '抖音' },
  { id: 'kuaishou', name: '快手' },
  { id: 'instagram', name: 'Instagram' },
  { id: 'wechat', name: '微信视频号' },
  { id: 'qqbot', name: 'QQ 机器人' },
  { id: 'wechatbot', name: '微信 ClawBot' }
])
const activeServiceTab = ref('telegram')
const botStatus = ref({})
const showUserModal = ref(false)
const isEditUser = ref(false)
const userForm = ref({ username: '', password: '', role: 'user', is_active: 1, id: null })

async function loadUserInfo() {
  try {
    userInfo.value = await auth.getCurrentUser()
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

async function loadUsers() {
  try {
    const data = await usersApi.list()
    users.value = data.users || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

async function loadApiKeys() {
  try {
    const data = await apiKeysApi.list()
    apiKeys.value = data.keys || []
  } catch (error) {
    console.error('加载API密钥失败:', error)
  }
}

async function loadInviteCodes() {
  try {
    const data = await inviteCodesApi.list()
    inviteCodes.value = data.codes || []
  } catch (error) {
    console.error('加载邀请码失败:', error)
  }
}

async function loadSettings() {
  try {
    const data = await settingsApi.get()
    const proxyEnabled = data.proxy_enabled === true || data.proxy_enabled === '1'
    const httpProxy = data.http_proxy || ''
    const httpsProxy = data.https_proxy || ''

    settingsForm.value = {
      telegram_bot_token: data.telegram_bot_token || '',
      telegram_allowed_user_ids: data.telegram_allowed_user_ids || '',
      telegram_api_id: data.telegram_api_id || '',
      telegram_api_hash: data.telegram_api_hash || '',
      telegram_session: data.telegram_session || '',
      telegram_login_enabled: data.telegram_login_enabled || false,
      telegram_login_download_enabled: data.telegram_login_download_enabled || false,
      xtwitter_cookies: data.xtwitter_cookies || '',
      xtwitter_download_video: data.xtwitter_download_video !== false,
      xtwitter_download_images: data.xtwitter_download_images !== false,
      xtwitter_best_quality: data.xtwitter_best_quality !== false,
      xtwitter_quality: data.xtwitter_quality || 'best',
      proxy_enabled: proxyEnabled,
      http_proxy: httpProxy,
      https_proxy: httpsProxy,
      // QQ Bot
      qq_bot_api_url: data.qq_bot_api_url || '',
      // 微信 ClawBot
      wechat_clawbot_callback_url: data.wechat_clawbot_callback_url || ''
    }

    // 填充代理原始输入（去掉协议前缀方便编辑）
    httpProxyRaw.value = stripProtocol(httpProxy)
    httpsProxyRaw.value = stripProtocol(httpsProxy)

    // 记录当前服务地址
    currentServerUrl.value = window.location.origin
  } catch (error) {
    console.error('加载系统设置失败:', error)
  }
}

async function saveProxySettings() {
  // 组合完整代理地址
  const fullHttp = addProtocol(httpProxyRaw.value)
  const fullHttps = addProtocol(httpsProxyRaw.value)

  // 更新 settingsForm
  settingsForm.value.http_proxy = fullHttp
  settingsForm.value.https_proxy = fullHttps

  try {
    await settingsApi.save({
      proxy_enabled: settingsForm.value.proxy_enabled,
      http_proxy: fullHttp,
      https_proxy: fullHttps
    })
    alert('✅ 代理配置已保存')
  } catch (error) {
    alert('保存失败: ' + error.message)
  }
}

async function toggleProxy() {
  settingsForm.value.proxy_enabled = !settingsForm.value.proxy_enabled
  // 立即保存代理开关状态
  try {
    await settingsApi.save({
      proxy_enabled: settingsForm.value.proxy_enabled,
      http_proxy: settingsForm.value.http_proxy,
      https_proxy: settingsForm.value.https_proxy
    })
  } catch (error) {
    // 如果保存失败，恢复原状态
    settingsForm.value.proxy_enabled = !settingsForm.value.proxy_enabled
    alert('保存失败: ' + error.message)
  }
}

async function testProxyConnection() {
  const httpProxy = addProtocol(httpProxyRaw.value)
  if (!httpProxy) {
    alert('请先填写 HTTP 代理地址')
    return
  }
  try {
    const res = await fetch('/api/settings/test-proxy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ proxy_url: httpProxy })
    })
    const data = await res.json()
    if (data.success) {
      alert('✅ ' + data.detail)
    } else {
      alert('❌ 连接失败：' + data.detail)
    }
  } catch (e) {
    alert('❌ 测试请求失败：' + e.message)
  }
}

async function savePlatformSettings() {
  try {
    // 检查 token
    const token = localStorage.getItem('token')
    if (!token) {
      alert('未授权，请先登录')
      window.location.href = '/login'
      return
    }
    
    await settingsApi.savePlatform({
      telegram_bot_token: settingsForm.value.telegram_bot_token,
      telegram_allowed_user_ids: settingsForm.value.telegram_allowed_user_ids,
      telegram_api_id: settingsForm.value.telegram_api_id,
      telegram_api_hash: settingsForm.value.telegram_api_hash,
      telegram_session: settingsForm.value.telegram_session,
      telegram_login_enabled: settingsForm.value.telegram_login_enabled,
      telegram_login_download_enabled: settingsForm.value.telegram_login_download_enabled,
      xtwitter_cookies: settingsForm.value.xtwitter_cookies,
      xtwitter_download_video: settingsForm.value.xtwitter_download_video,
      xtwitter_download_images: settingsForm.value.xtwitter_download_images,
      xtwitter_best_quality: settingsForm.value.xtwitter_best_quality,
      xtwitter_quality: settingsForm.value.xtwitter_quality,
      // QQ Bot
      qq_bot_api_url: settingsForm.value.qq_bot_api_url,
      // 微信 ClawBot
      wechat_clawbot_callback_url: settingsForm.value.wechat_clawbot_callback_url
    })
    alert('✅ 平台设置已保存')
  } catch (error) {
    if (error.message.includes('未授权')) {
      alert('❌ ' + error.message)
      window.location.href = '/login'
    } else {
      alert('❌ 保存失败: ' + error.message)
    }
  }
}

async function onAvatarSelected(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  const allowed = ['image/png', 'image/jpeg']
  if (!allowed.includes(file.type)) {
    alert('只支持 JPG/PNG 格式')
    e.target.value = ''
    return
  }
  const maxSize = 1.5 * 1024 * 1024 // 1.5MB
  if (file.size > maxSize) {
    alert('图片过大，最大 1.5MB')
    e.target.value = ''
    return
  }
  try {
    const res = await auth.uploadAvatar(file)
    if (!res.ok) {
      let err = '上传失败'
      try {
        const data = await res.json()
        err = data.detail || err
      } catch (_) {}
      throw new Error(err)
    }
    await loadUserInfo()
    alert('头像上传成功')
  } catch (error) {
    alert('上传失败: ' + (error.message || error))
  } finally {
    e.target.value = ''
  }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    alert('两次输入的密码不一致')
    return
  }
  try {
    await auth.changePassword(passwordForm.value.old_password, passwordForm.value.new_password)
    alert('密码修改成功')
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (error) {
    alert('修改失败: ' + error.message)
  }
}

async function createApiKey() {
  try {
    const data = await apiKeysApi.create(newKeyNote.value)
    createdKey.value = data.full_key
    newKeyNote.value = ''
    await loadApiKeys()
  } catch (error) {
    alert('创建失败: ' + error.message)
  }
}

function copyKey() {
  navigator.clipboard.writeText(createdKey.value)
  alert('已复制到剪贴板')
}

async function toggleKeyStatus(key) {
  try {
    await apiKeysApi.toggle(key.key_id, key.status === 'active' ? 'disabled' : 'active')
    await loadApiKeys()
  } catch (error) {
    alert('更新失败: ' + error.message)
  }
}

async function deleteKey(key) {
  if (!confirm('确定删除该API密钥？')) return
  try {
    await apiKeysApi.delete(key.key_id)
    await loadApiKeys()
  } catch (error) {
    alert('删除失败: ' + error.message)
  }
}

async function generateInviteCode() {
  try {
    await inviteCodesApi.create()
    await loadInviteCodes()
    alert('邀请码已生成')
  } catch (error) {
    alert('生成失败: ' + error.message)
  }
}

// ==================== 插件管理方法 ====================
async function loadPluginInfo() {
  try {
    pluginInfo.value = await pluginApi.info()
  } catch (e) {
    console.warn('加载插件信息失败:', e)
  }
}

async function downloadPlugin() {
  pluginDownloading.value = true
  try {
    const blob = await pluginApi.download()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'bosco-tsang-plugin.zip'
    document.body.appendChild(a)
    a.click()
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }, 200)
  } catch (err) {
    alert('插件打包下载失败: ' + err.message)
  } finally {
    pluginDownloading.value = false
  }
}

function installShortcut() {
  // 在新窗口打开快捷指令下载页面
  const downloadUrl = `${window.location.origin}/shortcuts/download`
  window.open(downloadUrl, '_blank')
}

function viewShortcutGuide() {
  // 打开快捷指令使用指南
  window.open('/docs/IOS_SHORTCUTS_GUIDE.html', '_blank')
}

function openCreateUserModal() {
  isEditUser.value = false
  userForm.value = { username: '', password: '', role: 'user', is_active: 1, id: null }
  showUserModal.value = true
}

function editUser(user) {
  isEditUser.value = true
  userForm.value = {
    id: user.id,
    username: user.username,
    password: '',
    role: user.role,
    is_active: user.is_active ? 1 : 0
  }
  showUserModal.value = true
}

function closeUserModal() {
  showUserModal.value = false
}

async function saveUser() {
  try {
    if (!userForm.value.username) {
      alert('请输入用户名')
      return
    }
    if (!isEditUser.value && !userForm.value.password) {
      alert('请输入密码')
      return
    }

    if (isEditUser.value) {
      const updateData = {
        role: userForm.value.role,
        is_active: userForm.value.is_active
      }
      await usersApi.update(userForm.value.id, updateData)
      alert('用户信息已更新')
    } else {
      await usersApi.create(
        userForm.value.username,
        userForm.value.password,
        userForm.value.role,
        userForm.value.is_active
      )
      alert('用户已添加')
    }
    showUserModal.value = false
    await loadUsers()
  } catch (error) {
    alert('保存失败: ' + error.message)
  }
}

async function toggleUserStatus(user) {
  try {
    await usersApi.update(user.id, { is_active: user.is_active ? 0 : 1 })
    await loadUsers()
  } catch (error) {
    alert('更新失败: ' + error.message)
  }
}

async function deleteUser(user) {
  if (!confirm('确定删除该用户吗？')) return
  try {
    await usersApi.delete(user.id)
    await loadUsers()
  } catch (error) {
    alert('删除失败: ' + error.message)
  }
}

function formatDate(date) {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

onMounted(async () => {
  await loadUserInfo()
  if (isAdmin.value) {
    await loadUsers()
    await loadInviteCodes()
    await loadSettings()
  }
  await loadApiKeys()
  await loadPluginInfo()
  await loadBotStatus()
})

async function loadBotStatus() {
  try {
    const resp = await fetch('/api/bot/status', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (resp.ok) {
      botStatus.value = await resp.json()
    }
  } catch (e) {
    console.error('加载 Bot 状态失败:', e)
  }
}
</script>

<style scoped>
/* ==================== 基础布局 ==================== */
.settings-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: white;
  padding: 12px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow-x: auto;
}

.tab-btn {
  padding: 10px 18px;
  border: none;
  background: transparent;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.25s ease;
  white-space: nowrap;
  position: relative;
}

.tab-btn:hover { background: var(--bg-primary); }

.tab-btn.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  box-shadow: 0 4px 12px rgba(37,99,235,.3);
}

.settings-content { padding: 24px; }
.card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); }

.section-title {
  font-size: 18px; font-weight: 700; margin-bottom: 24px;
  padding-bottom: 14px; border-bottom: 2px solid var(--border);
  letter-spacing: -.3px;
}

/* ==================== 账户信息 ==================== */
.avatar-section {
  display: flex; align-items: center; gap: 24px; margin-bottom: 28px;
}
.avatar-preview { width: 88px; height: 88px; flex-shrink: 0; }
.avatar-img { width: 88px; height: 88px; border-radius: 50%; object-fit: cover; }
.avatar-circle {
  width: 88px; height: 88px; border-radius: 50%;
  background: linear-gradient(135deg,#667eea,#764ba2); color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 34px; font-weight: 700; box-shadow: 0 8px 24px rgba(102,126,234,.35);
}
.avatar-hint { font-size: 12px; color: var(--text-muted); margin-top: 8px; }
.info-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 18px; }
.info-item label { display: block; margin-bottom: 6px; font-size: 13px; color: var(--text-secondary); font-weight: 500; }

/* ==================== 用户管理 ==================== */
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar-sm {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg,#2563eb,#1d4ed8);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600; flex-shrink: 0;
}
.action-btns { display: flex; gap: 6px; }

/* 安全/通用 */
.security-section { padding: 22px; background: var(--bg-primary); border-radius: var(--radius); }
.security-section h4 { margin-bottom: 16px; font-size: 15px; font-weight: 600; }
.section-desc { font-size: 13px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5; }
.checkbox-label { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; }
.form-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 16px; }

/* ==================== 插件管理（新增） ==================== */
.plugin-hero {
  display: flex; align-items: center; gap: 22px;
  padding: 28px; background: linear-gradient(135deg,#f0f5ff,#e8f0fe);
  border-radius: 16px; border: 1px solid #d4e3ff; margin-bottom: 28px;
  position: relative; overflow: hidden;
}
.plugin-hero::before {
  content:''; position: absolute; top: -40px; right: -40px;
  width: 160px; height: 160px; border-radius: 50%;
  background: radial-gradient(circle, rgba(99,102,241,.12) 0%, transparent 70%);
}
.plugin-icon-wrap {
  width: 68px; height: 68px; border-radius: 18px; flex-shrink: 0;
  background: linear-gradient(135deg,#6366f1,#4f46e5);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(79,70,229,.3);
}
.plugin-icon { font-size: 30px; }
.plugin-info-text { flex: 1; }
.plugin-name { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 6px; }
.plugin-desc { font-size: 14px; color: #64748b; margin: 0 0 10px; line-height: 1.5; }
.plugin-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.meta-tag {
  padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
  background: white; color: #4f46e5; border: 1px solid #c7d2fe;
}
.btn-download-plugin {
  display: inline-flex; align-items: center; gap: 8px; padding: 12px 26px;
  border: none; border-radius: 12px; background: linear-gradient(135deg,#6366f1,#4f46e5);
  color: white; font-size: 15px; font-weight: 600; cursor: pointer;
  box-shadow: 0 6px 20px rgba(79,70,229,.35); transition: all .25s;
  white-space: nowrap; flex-shrink: 0;
}
.btn-download-plugin:hover:not(:disabled) {
  transform: translateY(-2px); box-shadow: 0 8px 28px rgba(79,70,229,.45);
}
.btn-download-plugin:disabled { opacity: .65; cursor: not-allowed; }

.feature-grid {
  display: grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap: 14px;
  margin-bottom: 28px;
}
.feature-card {
  display: flex; align-items: center; gap: 12px; padding: 16px 18px;
  background: white; border: 1px solid #e8ecf1; border-radius: 12px;
  transition: all .2s;
}
.feature-card:hover { border-color:#c7d2fe; box-shadow: 0 4px 14px rgba(0,0,0,.05); transform: translateY(-1px); }
.feat-icon { font-size: 22px; flex-shrink: 0; }
.feat-text { font-size: 14px; color: #334155; font-weight: 500; }

.install-guide, .config-guide { margin-top: 28px; }
.guide-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #1e293b; }

.steps { display: flex; flex-direction: column; gap: 14px; }
.step { display: flex; gap: 16px; align-items: flex-start; }
.step-num {
  width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg,#2563eb,#1d4ed8); color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
}
.step-body strong { display: block; font-size: 14px; color: #1e293b; margin-bottom: 2px; }
.step-body p { font-size: 13px; color: #64748b; margin: 0; line-height: 1.5; }

.config-cards { display: grid; grid-template-columns: repeat(auto-fill,minmax(300px,1fr)); gap: 16px; }
.config-card {
  padding: 20px; background: var(--bg-primary); border-radius: 12px; border: 1px solid var(--border);
}
.config-label {
  display: inline-block; padding: 3px 10px; border-radius: 6px;
  background: #dbeafe; color: #1d4ed8; font-size: 12px; font-weight: 600; margin-bottom: 8px;
}
.config-value { display: block; font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px; word-break: break-all; }
.config-hint { font-size: 12px; color: #94a3b8; margin: 0; }

.spinner {
  width: 16px; height: 16px; border: 2px solid transparent; border-top-color: currentColor;
  border-radius: 50%; animation: spin .6s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ==================== 代理面板（全新设计） ==================== */
.proxy-panel {
  border: 2px solid #e8ecf1; border-radius: 16px; padding: 28px;
  background: linear-gradient(180deg, #fafbff 0%, #f5f7fa 100%);
  transition: all .35s cubic-bezier(.4,0,.2,1); position: relative; overflow: hidden;
}
.proxy-panel.proxy-enabled {
  border-color: #93c5fd; background: linear-gradient(180deg, #eff6ff 0%, #f0f7ff 100%);
  box-shadow: 0 4px 24px rgba(59,130,246,.08);
}

.proxy-header { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 0; }
.proxy-status-area { display: flex; align-items: center; gap: 16px; }

/* 自定义 Toggle 开关 */
.proxy-toggle-wrap { cursor: pointer; user-select: none; }
.proxy-toggle-track {
  width: 52px; height: 28px; border-radius: 14px; background: #cbd5e1;
  position: relative; transition: all .3s; box-shadow: inset 0 2px 4px rgba(0,0,0,.08);
}
.proxy-toggle-track.active { background: linear-gradient(135deg,#3b82f6,#2563eb); box-shadow: 0 2px 10px rgba(59,130,246,.4); }
.proxy-toggle-thumb {
  width: 22px; height: 22px; border-radius: 11px; background: white;
  position: absolute; top: 3px; left: 3px;
  box-shadow: 0 2px 5px rgba(0,0,0,.15);
  transition: all .3s cubic-bezier(.68,-.55,.265,1.55);
}
.proxy-toggle-track.active .proxy-toggle-thumb { left: 27px; }

.proxy-status-info { display: flex; flex-direction: column; gap: 2px; }
.status-label { font-size: 15px; font-weight: 600; color: #475569; }
.proxy-enabled .status-label { color: #1d4ed8; }

.status-dots { display: flex; align-items: center; gap: 6px; position: relative; width: 12px; height: 12px; margin-top: 2px; }
.dot {
  width: 10px; height: 10px; border-radius: 50%; background: #cbd5e1;
  transition: all .3s; position: relative; z-index: 1;
}
.dot.active { background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,.5); }
.pulse-ring {
  position: absolute; top: 0; left: 0; width: 10px; height: 10px; border-radius: 50%;
  border: 2px solid #22c55e; animation: pulse-ring 1.5s ease-out infinite;
}
@keyframes pulse-ring {
  0% { transform: scale(1); opacity: .8; }
  100% { transform: scale(2.2); opacity: 0; }
}

/* 代理地址预览芯片 */
.proxy-preview { display: flex; gap: 8px; flex-wrap: wrap; }
.preview-chip {
  display: flex; align-items: center; gap: 6px; padding: 6px 12px;
  background: white; border: 1px solid #bfdbfe; border-radius: 20px;
}
.chip-label {
  padding: 2px 7px; border-radius: 6px; font-size: 11px; font-weight: 700;
  background: #dbeafe; color: #1d4ed8;
}
.chip-label.https { background: #fef3c7; color: #d97706; }
.chip-val { font-size: 12px; color: #334155; font-family: 'SF Mono','Cascadia Mono',Consolas,monospace; }
.preview-chip.empty { background: #f1f5f9; border-color: #e2e8f0; }
.preview-chip.empty .chip-val { color: #94a3b8; }

/* 配置展开区域 */
.config-divider {
  text-align: center; margin: 24px 0 20px; position: relative;
}
.config-divider::before {
  content:''; position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #e2e8f0;
}
.config-divider span {
  display: inline-block; padding: 0 16px; background: linear-gradient(180deg,#eff6ff 0%,#f0f7ff 100%);
  font-size: 13px; font-weight: 600; color: #64748b; position: relative;
}
.proxy-panel:not(.proxy-enabled) .config-divider span {
  background: linear-gradient(180deg,#fafbff 0%,#f5f7fa 100%);
}

.proxy-config-body { animation: expandIn .3s ease-out; }
@keyframes expandIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }

.proxy-input-group { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.input-field { display: flex; flex-direction: column; gap: 8px; }
.field-label { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: #334155; }
.field-icon { font-size: 16px; }
.input-with-prefix {
  display: flex; align-items: stretch; background: white;
  border: 2px solid #e2e8f0; border-radius: 10px; overflow: hidden;
  transition: border-color .2s; }
.input-with-prefix:focus-within { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.1); }
.input-prefix {
  display: flex; align-items: center; padding: 0 12px;
  background: #f1f5f9; color: #64748b; font-size: 13px; font-weight: 500;
  border-right: 1px solid #e2e8f0; user-select: none;
  font-family: 'SF Mono','Cascadia Mono',Consolas,monospace;
}
.proxy-input {
  border: none !important; border-radius: 0 !important;
  font-family: 'SF Mono','Cascadia Mono',Consolas,monospace !important;
  font-size: 13px !important;
}
.proxy-input:focus { box-shadow: none !important; }
.field-hint { font-size: 12px; color: #94a3b8; margin: 0; line-height: 1.5; }

.proxy-actions-bar { display: flex; gap: 12px; margin-top: 22px; padding-top: 18px; border-top: 1px solid #e8ecf1; }
.btn-icon { margin-right: 4px; }
.btn-outline {
  padding: 10px 20px; border: 2px solid #e2e8f0; border-radius: 10px;
  background: white; color: #475569; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all .2s; display: inline-flex; align-items: center;
}
.btn-outline:hover { border-color: #94a3b8; background: #f8fafc; }

/* 收起状态提示 */
.proxy-collapsed-hint {
  display: flex; align-items: center; gap: 10px; padding: 16px 20px; margin-top: 20px;
  background: #f1f5f9; border-radius: 10px; border: 1px solid #e2e8f0;
}
.hint-icon { font-size: 20px; }
.proxy-collapsed-hint span:last-child { font-size: 13px; color: #64748b; line-height: 1.5; }

/* 过渡动画 */
.slide-fade-enter-active, .slide-fade-leave-active { transition: all .25s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-8px); }
.expand-enter-active, .expand-leave-active { transition: all .3s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to, .expand-leave-from { max-height: 600px; opacity: 1; }

/* ==================== API 密钥 ==================== */
.api-key-create { display: flex; gap: 12px; }
.api-key-create .input { flex: 1; }
.key-created-alert {
  padding: 16px; background: linear-gradient(135deg,#fef3c7,#fde68a);
  border-radius: 12px; margin-top: 16px; border: 1px solid #fcd34d;
}

/* ==================== 平台设置 ==================== */
.platform-info-banner { background: #e8f4fd; border: 1px solid #b3d9f2; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 14px; color: #1a73e8; }
.platform-info-banner p { margin: 4px 0; }
.bot-status-card { display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #f5f5f7; border-radius: 8px; margin: 12px 0; font-size: 14px; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.status-dot.green { background: #34c759; }
.status-dot.gray { background: #8e8e93; }
.form-hint { font-size: 12px; color: #86868b; margin-top: 4px; }
.platform-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.platform-tab {
  padding: 8px 14px; border-radius: var(--radius); background: var(--bg-primary);
  color: var(--text-secondary); border: 1px solid var(--border); transition: all .2s;
}
.platform-tab:hover { border-color: #93c5fd; }
.platform-tab.active { background: var(--primary); color: white; border-color: transparent; }
.platform-panel { padding: 20px; background: var(--bg-primary); border-radius: var(--radius); }
.platform-placeholder { color: var(--text-secondary); }
.form-grid-2 { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 16px; margin-bottom: 16px; }
.form-grid-2 .full-width { grid-column: 1 / -1; }

.key-display {
  display: block; padding: 12px; background: white; border-radius: 8px;
  margin-top: 8px; word-break: break-all; font-size: 13px;
  font-family: 'SF Mono','Cascadia Code',Consolas,monospace;
  border: 1px solid #e2e8f0;
}

.invite-section { padding-top: 20px; border-top: 1px solid var(--border); }
.invite-section h4 { margin-bottom: 12px; }
.invite-actions { display: flex; gap: 12px; }

/* ==================== 弹窗 ==================== */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(15,23,42,.5); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal-card {
  width: 440px; background: white; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,.2); overflow: hidden;
}
.modal-header, .modal-footer {
  padding: 18px 22px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border);
}
.modal-header h3 { font-size: 17px; font-weight: 700; }
.modal-footer { border-top: 1px solid var(--border); border-bottom: none; }
.modal-body { padding: 22px; }
.modal-body .form-item { margin-bottom: 16px; }
.modal-body label { display: block; margin-bottom: 6px; color: var(--text-secondary); font-weight: 500; }
.modal-footer button { min-width: 110px; border-radius: 10px; font-weight: 600; }

/* ==================== 表格 ==================== */
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 14px; text-align: left; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
.table th { font-weight: 600; color: #475569; font-size: 13px; background: #f8fafc; }
.badge {
  display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
}
.badge-success { background: #dcfce7; color: #166534; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-danger { background: #fee2e2; color: #991b1b; }
.badge-info { background: #dbeafe; color: #1e40af; }

/* ==================== 按钮/输入框基础 ==================== */
.input {
  width: 100%; padding: 10px 14px; border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; outline: none; transition: all .2s; background: white; color: #1e293b;
}
.input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.1); }
.input:disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; }
textarea.input { resize: vertical; }

.btn {
  padding: 10px 20px; border: none; border-radius: 10px; font-size: 14px;
  font-weight: 600; cursor: pointer; transition: all .2s;
}
.btn-primary { background: linear-gradient(135deg,#2563eb,#1d4ed8); color: white; }
.btn-primary:hover { box-shadow: 0 4px 14px rgba(37,99,235,.35); }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; }
.btn-gray { background: #f1f5f9; color: #475569; }
.btn-gray:hover { background: #e2e8f0; }
.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover { background: #dc2626; }
.btn-warning { background: #f59e0b; color: white; }
.btn-success { background: #22c55e; color: white; }
.btn-sm { padding: 6px 14px; font-size: 12px; }

.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 16px; }

.settings-header { display: flex; align-items: center; justify-content: space-between; }
.form-item { margin-bottom: 0; } /* override for modal context */

@media (max-width: 768px) {
  .proxy-input-group { grid-template-columns: 1fr; }
  .plugin-hero { flex-direction: column; text-align: center; }
  .feature-grid { grid-template-columns: 1fr; }
  .info-grid { grid-template-columns: 1fr; }
  .proxy-header { flex-direction: column; align-items: flex-start; gap: 14px; }
}

/* Telegram 登录设置样式 */
.telegram-login-section {
  margin: 24px 0;
  padding: 20px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
}

.telegram-login-section h5 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #1e293b;
}

.toggle-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.toggle-info {
  flex: 1;
}

.toggle-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.toggle-desc {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 28px;
  flex-shrink: 0;
  margin-left: 16px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* iOS 快捷指令区域样式 */
.shortcut-section {
  margin-top: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 16px;
  border: 2px solid #bae6fd;
}

.shortcut-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.shortcut-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #007AFF, #5856D6);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.3);
  flex-shrink: 0;
}

.shortcut-icon {
  font-size: 32px;
}

.shortcut-info {
  flex: 1;
}

.shortcut-name {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.shortcut-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 12px;
  line-height: 1.5;
}

.shortcut-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.shortcut-tags .tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: white;
  color: #007AFF;
  border: 1px solid #bae6fd;
}

.shortcut-features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.shortcut-feature {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: white;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.shortcut-feature .feat-icon {
  font-size: 20px;
}

.shortcut-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.btn-install-shortcut {
  flex: 1;
  min-width: 180px;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #007AFF, #5856D6);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.35);
  transition: all 0.25s;
}

.btn-install-shortcut:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0, 122, 255, 0.45);
}

.btn-view-guide {
  padding: 14px 24px;
  border: 2px solid #007AFF;
  border-radius: 12px;
  background: white;
  color: #007AFF;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-view-guide:hover {
  background: #f0f9ff;
  transform: translateY(-2px);
}

.shortcut-steps {
  background: white;
  padding: 20px;
  border-radius: 12px;
}

.steps-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 16px;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #475569;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007AFF, #5856D6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .shortcut-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .shortcut-tags {
    justify-content: center;
  }
  
  .shortcut-features {
    grid-template-columns: 1fr;
  }
  
  .shortcut-actions {
    flex-direction: column;
  }
  
  .btn-install-shortcut,
  .btn-view-guide {
    width: 100%;
  }
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: 0.3s;
  border-radius: 28px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

input:checked + .toggle-slider {
  background-color: #3b82f6;
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

/* X/Twitter 配置样式 */
.platform-info-banner {
  padding: 16px;
  background: linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%);
  border-radius: 12px;
  margin-bottom: 20px;
  color: white;
}

.platform-info-banner p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.twitter-download-options {
  margin: 24px 0;
  padding: 20px;
  background: rgba(29, 161, 242, 0.05);
  border: 1px solid rgba(29, 161, 242, 0.2);
  border-radius: 12px;
}

.twitter-download-options h5 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #1e293b;
}

.help-text {
  margin: 8px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #1da1f2;
}

.help-text strong {
  color: #1e293b;
}
</style>
