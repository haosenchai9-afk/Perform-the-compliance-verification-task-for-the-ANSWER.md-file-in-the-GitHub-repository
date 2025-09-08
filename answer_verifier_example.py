#!/usr/bin/env python3
# =============================================================================
# ANSWER.md文件合规性验证实例（基于模板实现）
#==============================
# 实例说明：
# 本代码为模板验证代码的具体实现，用于验证"missing-semester"仓库
# 中ANSWER.md文件的合规性，包含完整的配置与验证逻辑
# 执行命令：python answer_verifier_example.py
# =============================================================================
import sys
import os
import requests
import yaml
import base64
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv


# ==========================
# 实例配置（基于模板填充实际值）
# ==========================
CONFIG = {
    # 基础文件路径配置（实例值）
    "FILE_PATHS": {
        "default_env_file": ".env.example",            # 实例环境变量文件
        "default_config_file": "answer_config.yaml",   # 实例配置文件
        "script_filename": "answer_verifier_example.py"
    },

    # GitHub API配置（固定值）
    "GITHUB_API": {
        "api_version": "application/vnd.github.v3+json",
        "user_agent": "Answer-Verifier-Example/1.0",
        "success_status_code": 200,
        "not_found_status_code": 404,
        "response_truncate_length": 100,
        "sha_display_length": 8
    },

    # 环境变量配置（实例键名）
    "ENV_VARS": {
        "github_token_var": "MCP_GITHUB_TOKEN",
        "github_org_var": "GITHUB_EVAL_ORG"
    },

    # 编码配置（固定值）
    "ENCODING": {
        "file_encoding": "utf-8",
        "github_file_encoding": "base64"
    },

    # 配置文件必填字段（实例映射）
    "CONFIG_REQUIRED_FIELDS": {
        "target_repo": "target_repo",
        "target_branch": "target_branch",
        "answer_file_path": "answer_file_path",
        "expected_content": "expected_content"
    },

    # 验证流程配置（实例步骤）
    "VERIFICATION_FLOW": {
        "step_1_marker": "1",
        "step_2_marker": "2",
        "separator_length": 60
    }
}


# ==========================
# 基础配置（实例化模板变量）
# ==========================
DEFAULT_ENV_FILE = CONFIG["FILE_PATHS"]["default_env_file"]
DEFAULT_CONFIG_FILE = CONFIG["FILE_PATHS"]["default_config_file"]
GITHUB_API_VERSION = CONFIG["GITHUB_API"]["api_version"]


# ==========================
# 工具函数（模板通用实现）
# ==========================
def load_environment(env_path: str) -> Tuple[str, str]:
    """加载环境变量（实例化模板逻辑）"""
    if not os.path.exists(env_path):
        print(f"❌ 错误：环境文件 {env_path} 不存在", file=sys.stderr)
        sys.exit(1)

    load_dotenv(env_path)
    github_token = os.getenv(CONFIG["ENV_VARS"]["github_token_var"])
    github_org = os.getenv(CONFIG["ENV_VARS"]["github_org_var"])

    if not github_token:
        print(f"❌ 错误：{env_path}中未配置 {CONFIG['ENV_VARS']['github_token_var']}", file=sys.stderr)
        sys.exit(1)
    if not github_org:
        print(f"❌ 错误：{env_path}中未配置 {CONFIG['ENV_VARS']['github_org_var']}", file=sys.stderr)
        sys.exit(1)

    return github_token, github_org


def load_project_config(config_path: str) -> Dict:
    """加载项目配置（实例化模板逻辑）"""
    if not os.path.exists(config_path):
        print(f"❌ 错误：配置文件 {config_path} 不存在", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, "r", encoding=CONFIG["ENCODING"]["file_encoding"]) as f:
            config = yaml.safe_load(f)
        
        # 验证配置完整性（实例化必填字段检查）
        required_fields = [
            CONFIG["CONFIG_REQUIRED_FIELDS"]["target_repo"],
            CONFIG["CONFIG_REQUIRED_FIELDS"]["target_branch"],
            CONFIG["CONFIG_REQUIRED_FIELDS"]["answer_file_path"],
            CONFIG["CONFIG_REQUIRED_FIELDS"]["expected_content"]
        ]
        for field in required_fields:
            if field not in config:
                print(f"❌ 错误：配置文件缺少字段「{field}」", file=sys.stderr)
                sys.exit(1)
        
        return config
    except Exception as e:
        print(f"❌ 配置加载失败：{str(e)}", file=sys.stderr)
        sys.exit(1)


def get_github_headers(token: str) -> Dict[str, str]:
    """生成GitHub请求头（模板通用实现）"""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": GITHUB_API_VERSION,
        "User-Agent": CONFIG["GITHUB_API"]["user_agent"]
    }


def fetch_github_file(
    file_path: str,
    headers: Dict[str, str],
    org: str,
    repo: str,
    branch: str
) -> Optional[str]:
    """获取GitHub文件内容（实例化API调用）"""
    api_url = f"https://api.github.com/repos/{org}/{repo}/contents/{file_path}?ref={branch}"
    try:
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == CONFIG["GITHUB_API"]["success_status_code"]:
            data = response.json()
            if data.get("encoding") == CONFIG["ENCODING"]["github_file_encoding"]:
                return base64.b64decode(data["content"]).decode(CONFIG["ENCODING"]["file_encoding"])
            return data.get("content")
        
        elif response.status_code == CONFIG["GITHUB_API"]["not_found_status_code"]:
            print(f"❌ 文件 {file_path} 在 {branch} 分支不存在", file=sys.stderr)
            return None
        
        else:
            print(f"❌ API错误（{response.status_code}）：{response.text[:100]}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"❌ 请求异常：{str(e)}", file=sys.stderr)
        return None


# ==========================
# 核心验证逻辑（实例化实现）
# ==========================
def verify_answer_content(actual: str, expected: str) -> bool:
    """验证文件内容（实例化比对逻辑）"""
    actual_clean = actual.strip()
    expected_clean = expected.strip()
    
    if actual_clean != expected_clean:
        print(f"❌ 内容不匹配：\n预期: {expected_clean}\n实际: {actual_clean}", file=sys.stderr)
        return False
    return True


def run_verification(config: Dict, token: str, org: str) -> bool:
    """执行验证流程（实例化模板步骤）"""
    # 提取配置参数（实例化变量）
    repo = config[CONFIG["CONFIG_REQUIRED_FIELDS"]["target_repo"]]
    branch = config[CONFIG["CONFIG_REQUIRED_FIELDS"]["target_branch"]]
    file_path = config[CONFIG["CONFIG_REQUIRED_FIELDS"]["answer_file_path"]]
    expected_content = config[CONFIG["CONFIG_REQUIRED_FIELDS"]["expected_content"]]
    headers = get_github_headers(token)

    # 验证流程输出（实例化步骤展示）
    print("=" * CONFIG["VERIFICATION_FLOW"]["separator_length"])
    print(f"📋 验证目标：{org}/{repo}@{branch} 的 {file_path}")
    print("=" * CONFIG["VERIFICATION_FLOW"]["separator_length"])

    # 步骤1：获取文件（实例化检查）
    print(f"\n{CONFIG['VERIFICATION_FLOW']['step_1_marker']}. 获取文件内容...")
    content = fetch_github_file(file_path, headers, org, repo, branch)
    if not content:
        return False
    print(f"✅ 成功获取文件（大小：{len(content)} 字符）")

    # 步骤2：验证内容（实例化检查）
    print(f"\n{CONFIG['VERIFICATION_FLOW']['step_2_marker']}. 验证文件内容...")
    if not verify_answer_content(content, expected_content):
        return False
    print(f"✅ 内容验证通过（匹配预期值：{expected_content}）")

    # 验证通过
    print("\n" + "=" * CONFIG["VERIFICATION_FLOW"]["separator_length"])
    print("🎉 所有验证步骤通过！")
    print("=" * CONFIG["VERIFICATION_FLOW"]["separator_length"])
    return True


# ==========================
# 入口函数（实例化执行）
# ==========================
def main():
    # 加载环境与配置（实例化路径）
    print(f"📌 加载环境变量：{DEFAULT_ENV_FILE}")
    github_token, github_org = load_environment(DEFAULT_ENV_FILE)

    print(f"📌 加载项目配置：{DEFAULT_CONFIG_FILE}")
    project_config = load_project_config(DEFAULT_CONFIG_FILE)

    # 执行验证
    print("\n" + "-" * 50)
    result = run_verification(project_config, github_token, github_org)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
