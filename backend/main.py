import os
import json
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import chardet
import unicodedata
import re
import io
import logging

# 加载根目录 .env
load_dotenv()

app = FastAPI(title="CatchRisk Backend", version="0.1.0")

# CORS：前端用 file:// 打开，也可以跨域访问 http://127.0.0.1:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo 阶段开放即可，正式上线需收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RiskItem(BaseModel):
    title: str
    type: str
    severity: str
    clause: str
    suggestion: str


class AnalyzeResponse(BaseModel):
    contract_text: str
    fields: dict
    risk_score: int
    risk_level: str
    risk_summary: str
    risks: List[RiskItem]
    missing_clauses: List[str]


class ReportRequest(BaseModel):
    fields: dict
    risks: List[RiskItem]
    risk_score: int
    risk_level: str
    risk_summary: str
    missing_clauses: List[str]
    contract_text: Optional[str] = None


class ReportResponse(BaseModel):
    summary: str
    conclusion: str


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "system": "CatchRisk"}


async def call_llm(prompt: str, response_format: Optional[str] = "json") -> str:
    """
    通用 LLM 调用封装。
    默认假设是 OpenAI 兼容的 /v1/chat/completions。
    你接 Qwen / 其它模型时：
    - 如果支持 OpenAI 兼容模式：只要改 base_url 和 model 即可。
    - 如果不兼容：在这里调整 payload 格式。
    """
    base_url = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    api_key = os.getenv("LLM_API_KEY", "sk-02f6825b31b54ae88797008e97829792")
    model = os.getenv("LLM_MODEL", "qwen3-max")

    if not api_key:
        raise RuntimeError("LLM_API_KEY 环境变量未设置，请在根目录 .env 配置。")

    url = f"{base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一名资深金融法务与风控专家，擅长审阅中文合同。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    # 如果模型支持 JSON 输出，可以开启；如不支持则删除这一段
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"LLM API 调用失败: {resp.status_code} {resp.text}")
        data = resp.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"无法解析 LLM 返回内容: {e}; 原始数据: {data}")

    return content


def extract_text_from_file_bytes(file_bytes: bytes, filename: str) -> str:
    """
    文本抽取占位实现：
    - 现在先假设是 UTF-8 文本，主要为了打通 LLM + 前端流程。
    - 之后你可以在这里接：
      - PDF：pdfplumber / PyPDF2
      - 图片：PaddleOCR 或 OCR 云服务
    """
    if not file_bytes:
        return "（占位文本：未读取到文件内容。）"

    # 优先根据文件后缀尝试一些可选的解析器（有库则用，没有则跳过）
    name = (filename or "").lower()
    try:
        # 优先通过二进制魔数判断是否为 PDF 或图片，避免误把二进制直接解码为文本
        raw = (file_bytes or b'')
        starts = raw.lstrip()[:8]
        is_pdf_magic = starts.startswith(b'%PDF')
        is_jpeg = starts.startswith(b'\xff\xd8')
        is_png = starts.startswith(b'\x89PNG')

        # PDF 处理：如果检测到 PDF 魔数，尝试用 pdfplumber；否则返回占位提示
        if is_pdf_magic or name.endswith('.pdf'):
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    pages = [ (p.extract_text() or '') for p in pdf.pages ]
                text = '\n'.join(pages).strip()
                if text:
                    return _sanitize_text(text)
                # 如果 pdfplumber 解析到空文本，继续到后续解码尝试
            except ModuleNotFoundError:
                logging.warning('pdfplumber 未安装，无法解析 PDF 文件。')
                return '（PDF 文件：未安装 PDF 解析库 pdfplumber，无法提取文本。请安装 pdfplumber 或使用 OCR。）'
            except Exception:
                # 如果 pdfplumber 出现问题，记录并继续为兜底解码
                logging.exception('使用 pdfplumber 解析 PDF 出错。')

        # DOCX 处理：如果是 .docx，尝试用 python-docx 提取文本
        if name.endswith('.docx'):
            try:
                from docx import Document
                doc = Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                text = '\n'.join(paragraphs).strip()
                if text:
                    return _sanitize_text(text)
            except ModuleNotFoundError:
                logging.warning('python-docx 未安装，无法解析 .docx 文件。')
                return '（DOCX 文件：未安装 python-docx，无法提取文本。请安装 python-docx。）'
            except Exception:
                logging.exception('解析 DOCX 出错，回退到其他方式。')

        # 图片处理：如果检测到图片魔数，尝试 pytesseract；否则返回占位提示
        if is_jpeg or is_png or name.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            try:
                from PIL import Image
                import pytesseract
                # 如果用户通过环境变量指定了 tesseract 可执行路径，使用它
                t_cmd = os.getenv('TESSERACT_CMD')
                if t_cmd:
                    try:
                        pytesseract.pytesseract.tesseract_cmd = t_cmd
                    except Exception:
                        logging.warning('无法设置 pytesseract.tesseract_cmd 为 %s', t_cmd)
                img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
                text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                if text and text.strip():
                    return _sanitize_text(text)
            except ModuleNotFoundError:
                logging.warning('Pillow/pytesseract 未安装，无法对图片执行 OCR。')
                return '（图片文件：未安装 OCR 库（pillow/pytesseract），无法提取文本。请安装并配置 Tesseract。）'
            except Exception:
                logging.exception('图片 OCR 处理出错，回退到编码检测解码。')
    except Exception:
        # 如果上述可选解析器环节出错，继续走编码检测与解码
        pass

    # 尝试使用 chardet 检测编码并解码
    try:
        detect = chardet.detect(file_bytes or b'') or {}
        enc = detect.get('encoding') or 'utf-8'
        text = file_bytes.decode(enc, errors='replace')
    except Exception:
        try:
            text = file_bytes.decode('utf-8', errors='replace')
        except Exception:
            text = ''

    text = _sanitize_text(text)
    if text.strip():
        return text

    return "（占位文本：实际系统应在此接入 OCR 或 PDF 解析，将合同内容转成纯文本；当前无法识别文件内容。）"


def _sanitize_text(text: str) -> str:
    """对解码得到的文本做净化：
    - 规范化 unicode（NFKC）
    - 移除不可打印控制字符（保留常见换行、制表符）
    - 将多个空白合并为单个空格
    """
    if not isinstance(text, str):
        text = str(text or '')

    # Unicode 规范化
    try:
        text = unicodedata.normalize('NFKC', text)
    except Exception:
        pass

    # 去掉 NUL 等不可打印二进制字符，但保留 \t \n \r
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]+', ' ', text)

    # 移除连续的空白并修正行尾空格
    text = re.sub(r'[ \t\f\v]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    # 进一步移除二进制残留字符（非基本可打印 ASCII，也保留常用 CJK 块）
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u4E00-\u9FFF\u3000-\u303F\uFF00-\uFFEF]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text


def build_extract_prompt(contract_text: str) -> str:
    return f"""
你将看到一份中文合同文本，请你完成以下任务，并严格按照指定 JSON 格式输出（不要添加任何解释性文字）：

1. 抽取以下关键信息字段（没有则填空字符串）：
   - 合同名称
   - 甲方（买方）
   - 乙方（卖方）
   - 合同总金额
   - 合同期限 / 交付时间
   - 付款方式
   - 违约责任
   - 争议解决方式

2. 识别合同中的风险点，尤其包括：
   - 付款条件不明确、缺少里程碑或时间节点
   - 责任划分不清、违约责任过于笼统或不对等
   - 缺少质量标准、质保条款、售后服务约定
   - 对一方明显不利的争议解决条款

3. 对合同给出一个 0–100 的风险评分，分数越高表示风险越大。并给出一句话风险总结。

4. 标出缺失的关键条款（例如：质保期未约定等），用自然语言简要描述。

请只输出 JSON，格式如下（注意字段名必须一致）：

{{
  "fields": {{
    "合同名称": "",
    "甲方（买方）": "",
    "乙方（卖方）": "",
    "合同总金额": "",
    "合同期限 / 交付时间": "",
    "付款方式": "",
    "违约责任": "",
    "争议解决方式": ""
  }},
  "risk_score": 76,
  "risk_level": "低风险/中风险/高风险 之一",
  "risk_summary": "一句话概括主要风险点。",
  "risks": [
    {{
      "title": "风险点标题",
      "type": "风险类型，如 付款安排不明确 / 责任划分不清晰 / 争议解决不对等 等",
      "severity": "低风险/中风险/高风险 之一",
      "clause": "对应的合同原文片段（可适度截断）",
      "suggestion": "简要修改建议或注意事项"
    }}
  ],
  "missing_clauses": [
    "缺失条款或潜在问题描述"
  ]
}}

待分析合同文本如下：
--------------------
{contract_text}
--------------------
"""


def build_report_prompt(
    fields: dict,
    risks: List[RiskItem],
    risk_score: int,
    risk_level: str,
    risk_summary: str,
    missing_clauses: List[str],
) -> str:
    return f"""
你是一名资深银行风控与法律合规专家，现在需要根据系统已结构化抽取的结果，生成一份“合同审查报告”中的两个部分：

1）《合同摘要》：用 150～200 字客观概述合同的基本情况（不评价风险），包括：合同类型、标的、金额、交付/履约时间、双方主体等。
2）《整体风险结论》：用 150～200 字总结本合同的风险情况，结合评分、风险点与缺失条款，给出简要建议。需要明确强调：本结论仅作为风控辅助意见，不构成最终放款或交易决策。

以下是结构化数据：

[关键信息字段 fields]:
{json.dumps(fields, ensure_ascii=False, indent=2)}

[风险评分与等级]:
- risk_score: {risk_score}
- risk_level: {risk_level}
- risk_summary: {risk_summary}

[详细风险点列表 risks]:
{json.dumps([r.dict() for r in risks], ensure_ascii=False, indent=2)}

[缺失条款 missing_clauses]:
{json.dumps(missing_clauses, ensure_ascii=False, indent=2)}

请只输出 JSON，格式如下：

{{
  "summary": "这里是合同摘要，150-200 字。",
  "conclusion": "这里是整体风险结论与建议，150-200 字。"
}}
"""


@app.post("/api/analyze-contract", response_model=AnalyzeResponse)
async def analyze_contract(file: UploadFile = File(...)):
    """
    Step 1：上传合同文件，完成：
    - 文本抽取（OCR / PDF 解析）
    - 关键信息抽取
    - 风险点识别与评分
    """
    try:
        content = await file.read()
        contract_text = extract_text_from_file_bytes(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法读取文件: {e}")

    prompt = build_extract_prompt(contract_text)

    try:
        llm_output = await call_llm(prompt, response_format="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用大模型失败: {e}")

    # 解析模型返回 JSON
    try:
        data = json.loads(llm_output)
    except json.JSONDecodeError:
        # 兜底：有些模型会带前后解释文字，截取第一个 { 到 最后一个 }
        try:
            cleaned = llm_output.strip()
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start : end + 1]
            data = json.loads(cleaned)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"解析大模型 JSON 失败: {e}；原始输出: {llm_output}",
            )

    fields = data.get("fields", {}) or {}
    risk_score = int(data.get("risk_score", 0))
    risk_level = data.get("risk_level", "中风险")
    risk_summary = data.get("risk_summary", "")
    risks_raw = data.get("risks", []) or []
    missing_clauses = data.get("missing_clauses", []) or []

    risks: List[RiskItem] = []
    for r in risks_raw:
        try:
            risks.append(
                RiskItem(
                    title=r.get("title", ""),
                    type=r.get("type", ""),
                    severity=r.get("severity", ""),
                    clause=r.get("clause", ""),
                    suggestion=r.get("suggestion", ""),
                )
            )
        except Exception:
            continue

    return AnalyzeResponse(
        contract_text=contract_text,
        fields=fields,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_summary=risk_summary,
        risks=risks,
        missing_clauses=missing_clauses,
    )


@app.post("/api/generate-report", response_model=ReportResponse)
async def generate_report(req: ReportRequest):
    """
    Step 2：在已有结构化结果基础上，让大模型生成“合同摘要”和“整体风险结论”。
    """
    prompt = build_report_prompt(
        fields=req.fields,
        risks=req.risks,
        risk_score=req.risk_score,
        risk_level=req.risk_level,
        risk_summary=req.risk_summary,
        missing_clauses=req.missing_clauses,
    )

    try:
        llm_output = await call_llm(prompt, response_format="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用大模型失败: {e}")

    try:
        data = json.loads(llm_output)
    except json.JSONDecodeError:
        try:
            cleaned = llm_output.strip()
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start : end + 1]
            data = json.loads(cleaned)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"解析大模型 JSON 失败: {e}；原始输出: {llm_output}",
            )

    summary = data.get("summary", "")
    conclusion = data.get("conclusion", "")

    return ReportResponse(summary=summary, conclusion=conclusion)


if __name__ == "__main__":
    import uvicorn

    # Run without the auto-reloader here to avoid reloader import issues in some
    # execution environments (the development reload is useful locally).
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
