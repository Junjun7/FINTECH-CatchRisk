# CatchRisk · 合同票据智能审核系统

> 面向贷前授信场景的智能合同审查平台  
> 由 深圳大学 Cache 团队设计

---

## 中文版本

### 1. 系统介绍

**CatchRisk** 是一个面向银行、持牌金融机构贷前授信场景的**合同与票据智能审核系统**。通过集成先进的大语言模型（LLM）和风控规则引擎，系统对上传的合同文档进行全面自动化分析，包括文本智能解析、关键要素抽取、潜在风险识别，并生成专业的《合同审查报告》，有效辅助风控人员做出更加科学决策。

系统采用**三阶段处理流程**：文档识别 → 内容分析 → 报告生成，确保审查过程的完整性和可追溯性。

### 2. 核心功能

#### 2.1 智能文档导入
- 支持多种格式：**DOC / DOCX / PDF**
- 自动识别文件类型并进行智能解析
- 采用银行级 OCR 与版面分析引擎，精准识别合同内容

#### 2.2 合同内容智能识别
系统自动抽取以下关键要素：
- 合同基本信息（名称、甲乙方、签署日期）
- 经济条款（合同总金额、支付方式、期限）
- 法律条款（违约责任、争议解决方式、管辖权）
- 其他关键条款（质保期、保险安排、生效条件）

#### 2.3 多维度风险识别
系统识别的风险类别包括：
- **付款安排风险**：条件不明确、里程碑缺失、时间节点模糊
- **责任划分风险**：双方义务界定不清、违约责任不对等
- **条款完整性风险**：缺少质保、售后、保险等关键条款
- **法律合规风险**：争议解决机制不完善、管辖权约定模糊

风险评分范围：0-100 分，综合评估为"低风险 / 中风险 / 高风险"

#### 2.4 专业审查报告生成
- **《合同摘要》**：客观概述合同基本情况和交易结构
- **《整体风险结论》**：系统分析结论与专业建议
- **关键要素表**：结构化呈现所有抽取的关键信息
- **风险点详情**：逐项描述风险及改进建议
- **缺失条款分析**：提示应补充的重要条款

报告支持 TXT 格式导出，便于存档和后续处理。

### 3. 系统架构

```
┌─────────────────────────────────────────────┐
│          Web 浏览器 (index.html)             │
│   - 文档上传与预览                          │
│   - 分析流程展示                            │
│   - 报告生成与导出                          │
└──────────────┬──────────────────────────────┘
          │ HTTP API (JSON)
          ▼
┌─────────────────────────────────────────────┐
│      FastAPI 后端服务 (main.py)             │
│   - 文本抽取与预处理                        │
│   - 结构化数据处理                          │
│   - API 调用协调                            │
└──────────────┬──────────────────────────────┘
          │ OpenAI 兼容 API
          ▼
┌─────────────────────────────────────────────┐
│      大语言模型 (LLM)                       │
│   - 支持 Qwen、GPT 等主流模型               │
│   - 可配置任意 OpenAI 兼容接口              │
└─────────────────────────────────────────────┘
```

### 4. 技术栈

- **前端**：HTML5 + CSS3 + 原生 JavaScript
- **后端**：Python FastAPI + AsyncIO
- **文件处理**：pdfplumber（PDF）、python-docx（DOCX）、Tesseract（OCR）
- **模型集成**：OpenAI 兼容 HTTP API
- **数据格式**：JSON、Pydantic 数据验证

### 5. 快速开始

#### 5.01 在已有python环境下的快速启动（如否则5.1开始）

1. 启动后端
win系统下直接运行 run.bat
```
macos系统下直接运行run.sh
```

2. 打开index.html

3. 等待安装完依赖后就可以上传文件或者拖拽文件进入上传区域

#### 5.1 环境配置

1. 创建 Python 虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate
```

2. 安装依赖：
```bash
cd backend
pip install -r requirements.txt
```
3. 默认已经有1000k tokens的qwen3-max模型api供评委们测试

4. 配置环境变量（根目录 `.env`）：
```
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=qwen-max
```

#### 5.2 启动服务

启动后端服务：
```bash
cd backend
python main.py
```

后端将在 `http://127.0.0.1:8000` 启动

#### 5.3 使用前端

在浏览器中打开：
```
file:///path/to/frontend/index.html
```

或者使用本地 Web 服务器：
```bash
python -m http.server 8080 --directory frontend
```

然后访问：`http://localhost:8080`

### 6. 使用流程

1. **第一步：文档导入**
  - 选择或拖拽上传 DOC / DOCX / PDF 文件
  - 点击"开始智能审核"

2. **第二步：内容分析**
  - 系统自动完成文本识别与风险分析
  - 查看关键要素抽取结果和风险评分
  - 左侧状态指示器实时显示处理进度

3. **第三步：报告生成**
  - 点击"生成自动审查报告"
  - 系统生成专业的《合同审查报告》
  - 点击"导出报告"下载 TXT 文件

### 7. 系统优势

✅ **高效自动化** - 减少人工审查时间 80% 以上  
✅ **精准风险识别** - 基于金融法务领域知识的深度分析  
✅ **可溯源性强** - 完整的分析过程记录和结论说明  
✅ **易于集成** - 标准 REST API，支持与现有风控系统对接  
✅ **灵活可配置** - 支持任意 OpenAI 兼容模型，风险规则可定制  
✅ **用户体验优秀** - 直观的界面设计，流程清晰易用

### 8. 后期扩展方向

#### 8.1 功能扩展
- [ ] 支持 PDF 批量处理和对比分析
- [ ] 增加图片和扫描件 OCR 识别能力
- [ ] 支持多语言合同识别（英文、日文等）
- [ ] 历史报告管理和版本对比功能

#### 8.2 风控功能增强
- [ ] 与历史案例库对标，识别"黑名单"条款
- [ ] 支持自定义风险规则和行业模板
- [ ] 集成工商信息、征信等外部数据源
- [ ] 智能预警和决策建议优化

#### 8.3 报告与集成
- [ ] 支持 PDF、JSON、Excel 等多格式导出
- [ ] 生成可视化风险分布图表
- [ ] 与贷前风控系统数据对接
- [ ] 支持电子签名和报告防篡改

#### 8.4 模型与算法优化
- [ ] 微调行业专用模型，提升准确度
- [ ] 引入少样本学习处理特殊条款
- [ ] 多模型融合提高鲁棒性
- [ ] 实时反馈机制持续改进

#### 8.5 合规与安全
- [ ] 完整的审计日志和操作追溯
- [ ] 敏感信息加密存储
- [ ] 支持权限管理和角色控制
- [ ] 定期安全评估和合规检查

### 9. 项目结构

```
CatchRisk_Demo/
├── frontend/
│   ├── index.html          # 前端主页面
│   └── ...
├── backend/
│   ├── main.py             # FastAPI 主程序
│   ├── requirements.txt     # 依赖配置
│   ├── check_import.py      # 导入检查
│   └── test_backend.py      # 单元测试
├── .env                    # 环境配置文件
├── README.md               # 本文件
└── run.sh / .bat      # 启动脚本
```

---

## English Version

### 1. System Introduction

**CatchRisk** is an intelligent contract and document review system designed for pre-lending authorization scenarios in banking and licensed financial institutions. By integrating advanced Large Language Models (LLM) and risk control rule engines, the system provides comprehensive automated analysis of uploaded contract documents, including intelligent text parsing, key element extraction, potential risk identification, and generation of professional《Contract Review Reports》to effectively assist risk control personnel in making more scientific decisions.

The system adopts a **three-stage processing workflow**: document recognition → content analysis → report generation, ensuring the completeness and traceability of the review process.

### 2. Core Features

#### 2.1 Intelligent Document Import
- Supports multiple formats: **DOC / DOCX / PDF**
- Automatic file type recognition and intelligent parsing
- Bank-grade OCR and layout analysis engine for precise content identification

#### 2.2 Contract Content Intelligent Recognition
System automatically extracts the following key elements:
- Basic contract information (name, parties, signature date)
- Economic terms (total amount, payment method, duration)
- Legal clauses (liability, dispute resolution, jurisdiction)
- Other key terms (warranty period, insurance arrangements, effectiveness conditions)

#### 2.3 Multi-Dimensional Risk Identification
Risk categories identified by the system include:
- **Payment Arrangement Risk**: Unclear conditions, missing milestones, vague timelines
- **Responsibility Allocation Risk**: Unclear obligation definition, unequal liability allocation
- **Clause Completeness Risk**: Missing warranty, after-sales, insurance and other key terms
- **Legal Compliance Risk**: Incomplete dispute resolution mechanism, unclear jurisdiction

Risk score range: 0-100, assessed as "Low Risk / Medium Risk / High Risk"

#### 2.4 Professional Review Report Generation
- **《Contract Summary》**: Objective overview of basic contract information and transaction structure
- **《Overall Risk Conclusion》**: System analysis conclusion and professional recommendations
- **Key Elements Table**: Structured presentation of all extracted information
- **Risk Details**: Item-by-item description of risks and improvement suggestions
- **Missing Clause Analysis**: Highlight important terms that should be added

Reports support TXT format export for archiving and subsequent processing.

### 3. System Architecture

```
┌─────────────────────────────────────────────┐
│      Web Browser (index.html)               │
│   - Document Upload & Preview               │
│   - Analysis Process Display                │
│   - Report Generation & Export              │
└──────────────┬──────────────────────────────┘
          │ HTTP API (JSON)
          ▼
┌─────────────────────────────────────────────┐
│    FastAPI Backend Service (main.py)        │
│   - Text Extraction & Preprocessing         │
│   - Structured Data Processing              │
│   - API Call Coordination                   │
└──────────────┬──────────────────────────────┘
          │ OpenAI Compatible API
          ▼
┌─────────────────────────────────────────────┐
│    Large Language Model (LLM)               │
│   - Support Qwen, GPT and other models      │
│   - Any OpenAI compatible interface         │
└─────────────────────────────────────────────┘
```

### 4. Technology Stack

- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Backend**: Python FastAPI + AsyncIO
- **File Processing**: pdfplumber (PDF), python-docx (DOCX), Tesseract (OCR)
- **Model Integration**: OpenAI Compatible HTTP API
- **Data Format**: JSON, Pydantic Data Validation

### 5. Quick Start

#### 5.1 Environment Setup

1. Create Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables (`.env` in root directory):
```
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=qwen-max
```

#### 5.2 Start Backend Service

```bash
cd backend
python main.py
```

Backend will start at `http://127.0.0.1:8000`

#### 5.3 Use Frontend

Open in browser:
```
file:///path/to/frontend/index.html
```

Or use a local web server:
```bash
python -m http.server 8080 --directory frontend
```

Then visit: `http://localhost:8080`

### 6. Usage Workflow

1. **Step 1: Document Import**
  - Select or drag-drop upload DOC / DOCX / PDF file
  - Click "Start Intelligent Review"

2. **Step 2: Content Analysis**
  - System automatically completes text recognition and risk analysis
  - View key element extraction results and risk scores
  - Left status indicator shows real-time processing progress

3. **Step 3: Report Generation**
  - Click "Generate Automatic Review Report"
  - System generates professional《Contract Review Report》
  - Click "Export Report" to download TXT file

### 7. System Advantages

✅ **High Automation Efficiency** - Reduce manual review time by 80%+  
✅ **Accurate Risk Identification** - Deep analysis based on financial and legal domain knowledge  
✅ **Strong Traceability** - Complete analysis process records and conclusion documentation  
✅ **Easy Integration** - Standard REST API, supports integration with existing risk systems  
✅ **Flexible Configuration** - Support any OpenAI-compatible model, customizable risk rules  
✅ **Excellent User Experience** - Intuitive interface design, clear and easy-to-use workflow

### 8. Future Extension Directions

#### 8.1 Feature Extensions
- [ ] Support batch PDF processing and comparative analysis
- [ ] Add image and scanned document OCR recognition capability
- [ ] Support multi-language contract recognition (English, Japanese, etc.)
- [ ] Historical report management and version comparison functionality

#### 8.2 Risk Control Enhancement
- [ ] Benchmark against historical case database to identify "blacklist" clauses
- [ ] Support custom risk rules and industry templates
- [ ] Integrate external data sources (business registry, credit information, etc.)
- [ ] Intelligent early warning and decision recommendation optimization

#### 8.3 Reporting and Integration
- [ ] Support multiple export formats (PDF, JSON, Excel, etc.)
- [ ] Generate visual risk distribution charts
- [ ] Integrate with pre-lending risk control system data
- [ ] Support digital signature and anti-tampering measures

#### 8.4 Model and Algorithm Optimization
- [ ] Fine-tune industry-specific models to improve accuracy
- [ ] Introduce few-shot learning for handling special clauses
- [ ] Multi-model fusion to improve robustness
- [ ] Real-time feedback mechanism for continuous improvement

#### 8.5 Compliance and Security
- [ ] Complete audit logs and operation traceability
- [ ] Sensitive information encryption storage
- [ ] Support permission management and role control
- [ ] Regular security assessments and compliance checks

### 9. Project Structure

```
CatchRisk_Demo/
├── frontend/
│   ├── index.html          # Frontend main page
│   └── ...
├── backend/
│   ├── main.py             # FastAPI main program
│   ├── requirements.txt     # Dependency configuration
│   ├── check_import.py      # Import check
│   └── test_backend.py      # Unit tests
├── .env                    # Environment configuration
├── README.md               # This file
└── run.sh / .bat      # Startup scripts
```

---

**Designed by Cache Team**
