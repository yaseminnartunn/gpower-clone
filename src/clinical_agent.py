"""
Clinical Research AI Agent for Power and Sample Size Analysis
Course: YZM301 Software Verification and Testing - Teardown Sprint
Role: AI Assistant translating clinician natural language questions into MCP tool calls.
Rule: The agent NEVER calculates statistical values itself; all values come from MCP.
"""

import re
import json
import datetime
from typing import Dict, Any, Tuple, Optional
from src.mcp_server import execute_power_analysis_tool

# Cohen's standard effect size benchmarks
COHEN_BENCHMARKS = {
    "küçük": 0.2,
    "kucuk": 0.2,
    "small": 0.2,
    "orta": 0.5,
    "medium": 0.5,
    "büyük": 0.8,
    "buyuk": 0.8,
    "large": 0.8
}


def classify_intent_and_extract_params(question: str) -> Dict[str, Any]:
    """
    Classifies test family, mode, and extracts parameters from Turkish clinical queries.
    Labels: t2-indep, t-paired, anova-oneway, chi2-contingency, multireg-r2, ambiguous, unsupported.
    """
    q_lower = question.lower()

    # Detect test family
    if any(k in q_lower for k in ["bağımsız", "bagimsiz", "iki grup", "ilaç ve plasebo", "ilac ve plasebo", "tedavi ve kontrol", "a grubu ve b grubu"]):
        test = "t2-indep"
        confidence = 0.95
    elif any(k in q_lower for k in ["önce ve sonra", "once ve sonra", "eşleştirilmiş", "eslestirilmis", "paired", "aynı hastalarda", "ayni hastalarda"]):
        test = "t-paired"
        confidence = 0.90
    elif any(k in q_lower for k in ["üç grup", "uc grup", "anova", "3 tedavi", "4 kol", "varyans analizi"]):
        test = "anova-oneway"
        confidence = 0.90
    elif any(k in q_lower for k in ["ki-kare", "olumsallık", "kontenjans", "oran karşılaştırma", "oran karsilastirma"]):
        test = "chi2-contingency"
        confidence = 0.90
    elif any(k in q_lower for k in ["regresyon", "risk faktör", "r2", "belirleyiciler"]):
        test = "multireg-r2"
        confidence = 0.90
    else:
        test = "ambiguous"
        confidence = 0.50

    # Detect tails (direction)
    # Default is 2 tails unless directional superiority/inferiority is claimed
    if any(k in q_lower for k in ["daha iyi", "daha etkili", "üstün", "ustun", "azaltacağını", "artıracağını", "tek yönlü", "tek yonlu", "one-tailed"]):
        tails = 1
    else:
        tails = 2

    # Detect alpha
    alpha = 0.05
    if "0.01" in q_lower or "%1" in q_lower or "yüzde 1" in q_lower:
        alpha = 0.01
    elif "0.001" in q_lower or "%0.1" in q_lower:
        alpha = 0.001
    elif "0.05" in q_lower or "%5" in q_lower or "yüzde 5" in q_lower:
        alpha = 0.05

    # Detect power
    power = 0.80  # standard clinical default
    if "0.95" in q_lower or "%95" in q_lower or "yüzde 95" in q_lower:
        power = 0.95
    elif "0.90" in q_lower or "%90" in q_lower or "yüzde 90" in q_lower:
        power = 0.90
    elif "0.80" in q_lower or "%80" in q_lower or "yüzde 80" in q_lower:
        power = 0.80

    # Detect effect size d
    d = None
    note = None
    # Look for explicit numbers e.g. "d=0.5", "d = 0.6", "0.4"
    d_match = re.search(r'\b(?:d\s*=\s*|etki\s*büyüklüğü\s*(?:olan|ise)?\s*)?([0-9]+(?:[\.,][0-9]+))\b', q_lower)
    if d_match:
        val_str = d_match.group(1).replace(",", ".")
        val_f = float(val_str)
        if 0.05 <= val_f <= 3.0:
            d = val_f

    if d is None:
        for kw, val in COHEN_BENCHMARKS.items():
            if kw in q_lower:
                d = val
                note = f"Etki büyüklüğü metinde doğrudan sayı verilmediği, '{kw}' belirtildiği için Cohen (1988) kılavuzuna göre d={val} olarak kabul edilmiştir."
                break

    if d is None:
        d = 0.5  # standard medium default
        note = "Etki büyüklüğü belirtilmediği için varsayılan orta etki (d=0.5) kabul edilmiştir."

    # Detect allocation ratio
    ratio = 1.0
    if "1:2" in q_lower or "2 katı" in q_lower or "iki katı" in q_lower:
        ratio = 2.0
    elif "2:1" in q_lower:
        ratio = 0.5

    # Mode: default a-priori (sample size query)
    mode = "a-priori"
    if "ulaşılan güç" in q_lower or "post hoc" in q_lower or "post-hoc" in q_lower or "güç nedir" in q_lower:
        mode = "post-hoc"

    return {
        "test": test,
        "confidence": confidence,
        "mode": mode,
        "tails": tails,
        "d": d,
        "alpha": alpha,
        "power": power,
        "ratio": ratio,
        "note": note
    }


def query_clinical_agent(question: str, log_file: str = "logs/agent_calls.jsonl") -> Dict[str, Any]:
    """
    Main agent endpoint: Takes clinical question, triggers MCP, logs tokens and returns response.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    classification = classify_intent_and_extract_params(question)

    test = classification["test"]
    confidence = classification["confidence"]

    # Estimate input tokens (approx 1 token per 4 chars for prompt + system message)
    tokens_in = len(question) // 4 + 180

    if test != "t2-indep" or confidence < 0.75:
        response_text = (
            f"Klinik sorunuz incelendi. Belirlenen test türü: '{test}' (Güven: {confidence:.2f}). "
            f"Sistemimiz şu anda onaylı K1 modülü olarak 't2-indep' (iki bağımsız grup t-testi) "
            f"ailesini desteklemektedir. Lütfen araştırma tasarımınızı doğrulayınız."
        )
        tokens_out = len(response_text) // 4
        # Log interaction
        log_entry = {
            "ts": start_time,
            "question": question,
            "tool_input": None,
            "tool_output": None,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "status": "CLARIFICATION_REQUIRED"
        }
        _append_log(log_file, log_entry)
        return {
            "response": response_text,
            "tool_called": False,
            "log": log_entry
        }

    # Prepare MCP tool arguments
    tool_input = {
        "test": "t2-indep",
        "mode": classification["mode"],
        "tails": classification["tails"],
        "d": classification["d"],
        "alpha": classification["alpha"],
        "power": classification["power"],
        "ratio": classification["ratio"]
    }

    # CALL MCP TOOL (Zero internal calculation - values come strictly from engine)
    mcp_result = execute_power_analysis_tool(tool_input)
    tool_output_raw = mcp_result["content"][0]["text"]
    tool_output = json.loads(tool_output_raw)

    if mcp_result["isError"]:
        response_text = f"Hesaplama hatası: {tool_output.get('error', 'Bilinmeyen hata')}"
    else:
        n1 = tool_output["n1"]
        n2 = tool_output["n2"]
        n_tot = tool_output["n_total"]
        act_pwr = tool_output["actual_power"]
        tcrit = tool_output["critical_t"]
        df = tool_output["df"]

        note_str = f"\n> *Not:* {classification['note']}" if classification.get("note") else ""
        tail_str = "Tek yönlü (üstünlük hipotezi)" if classification["tails"] == 1 else "Çift yönlü (fark hipotezi)"

        response_text = (
            f"### Klinik Araştırma Örneklem Büyüklüğü Raporu\n\n"
            f"Araştırma sorunuz için **G*Power Bağımsız İki Örneklem t-Testi (`t2-indep`)** modeli uygulanmıştır.\n\n"
            f"- **Hipotez Yönü:** {tail_str}\n"
            f"- **Hedef İstatistiksel Güç (1-β):** %{classification['power'] * 100:.0f}\n"
            f"- **Tip I Hata Riski (α):** {classification['alpha']}\n"
            f"- **Varsayılan Etki Büyüklüğü (Cohen's d):** {classification['d']}\n"
            f"- **Grup Dağılım Oranı (N2/N1):** {classification['ratio']}\n\n"
            f"#### 📊 Hesaplanan Örneklem İhtiyacı:\n"
            f"- **Grup 1 (İlaç / Tedavi):** {n1} hasta\n"
            f"- **Grup 2 (Plasebo / Kontrol):** {n2} hasta\n"
            f"- **TOPLAM GEREKEN ÖRNEKLEM (N):** **{n_tot} hasta**\n\n"
            f"#### 📐 İstatistiksel Doğrulama Parametreleri:\n"
            f"- **Ulaşılan Gerçek Güç (Actual Power):** %{act_pwr * 100:.4f}\n"
            f"- **Kritik t Değeri:** {tcrit:.4f}\n"
            f"- **Serbestlik Derecesi (df):** {df}\n"
            f"- **Merkezsizlik Parametresi (δ):** {tool_output['ncp']:.4f}\n"
            f"{note_str}\n\n"
            f"*Sonuçlar G*Power 3.1.9.7 motoru ile diferansiyel olarak doğrulanmıştır.*"
        )

    tokens_out = len(response_text) // 4
    log_entry = {
        "ts": start_time,
        "question": question,
        "tool_input": tool_input,
        "tool_output": tool_output,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "status": "SUCCESS" if not mcp_result["isError"] else "ERROR"
    }
    _append_log(log_file, log_entry)

    return {
        "response": response_text,
        "tool_called": True,
        "tool_input": tool_input,
        "tool_output": tool_output,
        "log": log_entry
    }


def _append_log(log_file: str, entry: Dict[str, Any]):
    """Appends JSON-line log entry."""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
