# ╔══════════════════════════════════════════════════════════════════════╗
# ║   NEXUS Autonomous Agent  v7.0  ·  HYPERION EDITION                ║
# ║   초지능 · 독자 이론 창조 · 변증법적 추론 · 패러다임 파괴          ║
# ║   NVIDIA NIM 동적 FETCH + 사용자 모델 선택  ·  절대 망각 없음      ║
# ║   TheoryForge  ·  DialecticalEngine  ·  ParadigmBreaker            ║
# ║   수백 세션 · 수천 이터레이션 — 영속 지식 · 이론 진화 · 끝없는 질문 ║
# ╠══════════════════════════════════════════════════════════════════════╣
# ║   ☠️  DEMON ALGORITHM v1.0  ·  Destructive Evaluation & Massive     ║
# ║   Overhaul Nexus — 신랄한 비평 → 완전 혁신 → 불가능을 가능으로    ║
# ║   직접 연구 · 직접 코드 · Colab 실행 · 무한 이터레이션 · 천재 AI  ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
# ┌─────────────────────────────────────────────────────────────────────┐
# │  ⚡ 실행 방법: 터미널에서 직접 실행하세요                           │
# │                                                                     │
# │  python nexus_agent_v7.py                         (대화형 CLI)      │
# │  python nexus_agent_v7.py -k nvapi-... -t "주제"  (직접 실행)       │
# │  python nexus_agent_v7.py --help                  (도움말)          │
# │                                                                     │
# │  💡 NVIDIA NIM API 키 발급: https://build.nvidia.com               │
# │  🧠 NEXUS Brain: ~/.nexus_brain.json (수천 이터레이션 영속 지식)   │
# │  🔭 TheoryForge: 독자 이론 생성·검증·진화 엔진                     │
# │  🌀 DialecticalEngine: 끝없는 자기 반박·질문·재합성                │
# └─────────────────────────────────────────────────────────────────────┘

import os, sys, io, re, json, time, traceback, subprocess, textwrap, contextlib
import hashlib, glob, shutil, threading, argparse
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from copy import deepcopy
from pathlib import Path

# ── 의존 패키지 자동 설치 ──────────────────────────────────────────────
def _ensure(pkg: str, import_as: str = None):
    try:
        __import__(import_as or pkg)
    except ImportError:
        print(f"[NEXUS] '{pkg}' 설치 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=True)

_ensure("requests")
import requests


# ═══════════════════════════════════════════════════════════════════════
#  ENVIRONMENT DETECTOR
# ═══════════════════════════════════════════════════════════════════════

class EnvDetector:
    """실행 환경 자동 감지"""

    @staticmethod
    def is_colab() -> bool:
        try:
            import google.colab  # noqa
            return True
        except ImportError:
            return False

    @staticmethod
    def has_gpu() -> bool:
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def python_version() -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}"

    @classmethod
    def report(cls) -> Dict:
        return {
            "colab": cls.is_colab(),
            "gpu": cls.has_gpu(),
            "python": cls.python_version(),
            "platform": sys.platform,
        }


# ═══════════════════════════════════════════════════════════════════════
#  COLAB BREAKPOINT — GPU·Notebook 기능 필요 시에만 사용자 개입 요청
# ═══════════════════════════════════════════════════════════════════════

class ColabBreakpoint:
    """
    에이전트가 GPU 집약적 연산이나 Colab 전용 기능이 필요하다고
    판단할 때만 사용자에게 Colab 실행을 요청합니다.

    - 코드에 '# NEXUS_COLAB_REQUIRED' 마커가 있을 때 자동 감지
    - 사용자가 결과를 붙여넣으면 에이전트가 계속 실행
    """

    MARKER = "# NEXUS_COLAB_REQUIRED"

    @staticmethod
    def is_required(code: str) -> bool:
        return ColabBreakpoint.MARKER in code

    @staticmethod
    def request_user_run(code: str, step_id: int) -> str:
        """사용자에게 Colab 실행 요청, 결과 수집"""
        # 비대화형 환경(파이프, 리다이렉션) 감지
        if not sys.stdin.isatty():
            print(f"\n  ⚠️  [ColabBreakpoint] 비대화형 환경 감지 — Step {step_id} Colab 요청 건너뜀.\n")
            return ""

        border = "═" * 65
        print(f"\n╔{border}╗")
        step_label = f"Step {step_id}: Colab에서 실행하세요"
        padding = max(0, 65 - 2 - len(step_label))
        print(f"║  ⏸️  사용자 액션 필요 — {step_label}{' ' * padding}║")
        print(f"╚{border}╝")
        print()
        print("  아래 코드를 Google Colab 셀에 붙여넣고 실행하세요:")
        print("  1. https://colab.research.google.com 에서 새 노트북 열기")
        print("  2. 셀에 아래 코드 붙여넣기 후 Shift+Enter 실행")
        print()
        print(f"  {'─'*63}")
        # 코드 출력 (마커 제거)
        clean = code.replace(ColabBreakpoint.MARKER, "# (Colab에서 실행됨)").strip()
        for line in clean.splitlines():
            print(f"  {line}")
        print(f"  {'─'*63}")
        print()
        print("  실행 완료 후 Colab 출력 전체를 아래에 붙여넣으세요.")
        print("  (완료 후 빈 줄에서 Enter 두 번 누르기 | 건너뛰려면 바로 Enter 두 번)")
        print()

        lines = []
        try:
            while True:
                line = input("  > ")
                if line == "" and lines and lines[-1] == "":
                    break
                if line == "" and not lines:
                    # 첫 입력이 빈 줄이면 건너뜀
                    print("  ⏭️  Colab 실행 건너뜀. 에이전트 계속 실행...\n")
                    return ""
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n  ⏭️  입력 중단. 에이전트 계속 실행...\n")
            return "\n".join(lines).strip()

        result_text = "\n".join(lines).strip()
        if result_text:
            print(f"\n  ✅ Colab 결과 {len(result_text)} 문자 수신. 에이전트 계속 실행...\n")
        else:
            print("\n  ⚠️  결과 없음. 에이전트가 빈 결과로 계속 실행합니다.\n")
        return result_text


# ═══════════════════════════════════════════════════════════════════════
#  LOCAL SAVER — 로컬 파일 저장
# ═══════════════════════════════════════════════════════════════════════

class LocalSaver:
    """
    로컬 파일 저장 전용 모듈.
    결과 파일은 ./NEXUS_Research 폴더에 저장됩니다.
    """

    def __init__(self, folder_name: str = "NEXUS_Research", verbose: bool = True, **kwargs):
        self.folder_name = folder_name
        self.verbose = verbose
        self.local_dir = Path(f"./{folder_name}")
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = True
        self._log(f"📁 로컬 저장 디렉토리: {self.local_dir.resolve()}")

    def save(self, src_path: str, description: str = "") -> bool:
        src = Path(src_path)
        if not src.exists():
            return False
        dst = self.local_dir / src.name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
        if description:
            self._log(f"💾 저장: {dst.name}  ({description})")
        return True

    def save_text(self, filename: str, content: str, description: str = "") -> str:
        path = self.local_dir / filename
        path.write_text(content, encoding="utf-8")
        if description:
            self._log(f"💾 저장: {filename}  ({description})")
        return str(path)

    def sync_all(self) -> int:
        files = [f for f in self.local_dir.iterdir() if f.is_file()]
        self._log(f"📂 로컬 저장 완료: {len(files)}개 파일 → {self.local_dir.resolve()}")
        return len(files)

    def _log(self, msg: str):
        if self.verbose:
            print(f"[LocalSaver] {msg}")


# 하위 호환성 별칭
DriveSync = LocalSaver


# ═══════════════════════════════════════════════════════════════════════
#  NEXUS BRAIN — 영속 교차-세션 지식 저장소 (절대 망각하지 않음)
# ═══════════════════════════════════════════════════════════════════════

class NexusBrain:
    """
    수백 세션, 수천 이터레이션에 걸쳐 지식·이론·패러다임을 축적하는 영속 두뇌.

    - ~/.nexus_brain.json 에 영속 저장 (절대 세션 간 망각 없음)
    - 모든 발견, 알고리즘, 이론, 성공/실패 패턴 누적
    - 독자 이론 생성 → 검증 → 진화 → 계보 추적
    - 패러다임 변이 이력 (어떤 가정이 언제 파괴되었는가)
    - 변증법적 질문 누적 (답 없이 쌓아두는 미해결 질문들)
    - 개념 간 관계 그래프 (지식 그물망 자동 구축)
    - 새 세션 시작 시 관련 과거 이론+발견+질문 자동 주입

    Hyperion 철학: 세션과 세션 사이 잠들지 않고 지식이 자라는 두뇌.
    """

    BRAIN_FILE = Path.home() / ".nexus_brain.json"
    MAX_DISCOVERIES = 2000
    MAX_SESSIONS = 200
    MAX_THEORIES = 500
    MAX_QUESTIONS = 300

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.data = self._load()
        if verbose:
            print(f"[NexusBrain] {self._stats_line()}")

    def _load(self) -> dict:
        try:
            if self.BRAIN_FILE.exists():
                raw = self.BRAIN_FILE.read_text(encoding="utf-8")
                d = json.loads(raw)
                # v6 → v7 migration
                if d.get("total_sessions") is not None or d.get("version") is not None:
                    d["version"] = "7.0"
                    d.setdefault("theories", [])
                    d.setdefault("paradigm_breaks", [])
                    d.setdefault("open_questions", [])
                    d.setdefault("concept_graph", {})
                    d.setdefault("theory_lineages", {})
                    return d
        except Exception:
            pass
        return self._empty()

    @staticmethod
    def _empty() -> dict:
        return {
            "version": "7.0",
            "total_sessions": 0,
            "total_steps": 0,
            "sessions": [],
            "discoveries": [],
            "algorithms": [],
            "theories": [],            # 독자적으로 생성된 이론들
            "theory_lineages": {},     # 이론 계보: {theory_id: [진화 이력]}
            "paradigm_breaks": [],     # 파괴된 패러다임 이력
            "open_questions": [],      # 답을 찾지 못한 채 쌓인 깊은 질문들
            "concept_graph": {},       # 개념 → 연결 개념들 (지식 그물망)
            "success_patterns": [],
            "failure_patterns": [],
            "domain_knowledge": {},
            "knowledge_graph": {},
            "user_style": {
                "preferred_modes": {},
                "avg_steps": 200,
                "complexity": "medium",
            },
        }

    def save(self):
        try:
            self.BRAIN_FILE.write_text(
                json.dumps(self.data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[NexusBrain] 저장 실패: {e}")

    # ── 지식 추가 ───────────────────────────────────────────────────

    def record_session(self, session_summary: dict):
        """세션 완료 후 요약 저장."""
        self.data["sessions"].append(session_summary)
        self.data["total_sessions"] += 1
        self.data["total_steps"] += session_summary.get("steps_completed", 0)
        if len(self.data["sessions"]) > self.MAX_SESSIONS:
            self.data["sessions"] = self.data["sessions"][-self.MAX_SESSIONS:]

        mode = session_summary.get("mode", "")
        if mode:
            prefs = self.data["user_style"]["preferred_modes"]
            prefs[mode] = prefs.get(mode, 0) + 1

        self.save()

    def add_discoveries(self, discoveries: list, domain: str = ""):
        """새로운 발견 추가."""
        ts = datetime.now().isoformat()
        for d in discoveries:
            if not d:
                continue
            entry = {"text": str(d)[:300], "domain": domain, "ts": ts}
            self.data["discoveries"].append(entry)
        if len(self.data["discoveries"]) > self.MAX_DISCOVERIES:
            self.data["discoveries"] = self.data["discoveries"][-self.MAX_DISCOVERIES:]

    def add_success_pattern(self, pattern: str):
        if pattern and pattern not in self.data["success_patterns"]:
            self.data["success_patterns"].append(pattern[:200])
            if len(self.data["success_patterns"]) > 100:
                self.data["success_patterns"] = self.data["success_patterns"][-100:]

    def add_failure_pattern(self, pattern: str):
        if pattern and pattern not in self.data["failure_patterns"]:
            self.data["failure_patterns"].append(pattern[:200])
            if len(self.data["failure_patterns"]) > 100:
                self.data["failure_patterns"] = self.data["failure_patterns"][-100:]

    # ── 이론 관리 ───────────────────────────────────────────────────

    def add_theory(self, theory: dict):
        """독자 생성 이론 저장. theory: {name, axioms, predictions, domain, ts, id}"""
        if not theory or not theory.get("name"):
            return
        theory_id = theory.get("id") or hashlib.md5(
            theory["name"].encode()
        ).hexdigest()[:8]
        theory["id"] = theory_id
        theory.setdefault("ts", datetime.now().isoformat())
        theory.setdefault("verified", False)
        theory.setdefault("refuted", False)
        theory.setdefault("session_count", 1)

        # 이미 존재하면 진화 이력 추가
        existing = next(
            (t for t in self.data["theories"] if t.get("id") == theory_id), None
        )
        if existing:
            existing["session_count"] = existing.get("session_count", 1) + 1
            lineage = self.data["theory_lineages"].setdefault(theory_id, [])
            lineage.append({"ts": datetime.now().isoformat(), "update": theory.get("axioms", [])[:2]})
        else:
            self.data["theories"].append(theory)
            if len(self.data["theories"]) > self.MAX_THEORIES:
                self.data["theories"] = self.data["theories"][-self.MAX_THEORIES:]

    def add_paradigm_break(self, old_assumption: str, new_insight: str, domain: str = ""):
        """기존 가정이 파괴된 사건 기록."""
        if old_assumption and new_insight:
            self.data["paradigm_breaks"].append({
                "old": old_assumption[:200],
                "new": new_insight[:200],
                "domain": domain,
                "ts": datetime.now().isoformat(),
            })
            if len(self.data["paradigm_breaks"]) > 200:
                self.data["paradigm_breaks"] = self.data["paradigm_breaks"][-200:]

    def add_open_question(self, question: str, domain: str = "", importance: int = 5):
        """아직 답을 못 찾은 깊은 질문 누적 보관."""
        if not question:
            return
        # 중복 방지 (유사 질문 체크)
        q_lower = question.lower()
        for existing in self.data["open_questions"]:
            if existing.get("q", "").lower()[:80] == q_lower[:80]:
                existing["importance"] = max(existing.get("importance", 5), importance)
                existing["revisit_count"] = existing.get("revisit_count", 0) + 1
                return
        self.data["open_questions"].append({
            "q": question[:300],
            "domain": domain,
            "importance": importance,
            "ts": datetime.now().isoformat(),
            "revisit_count": 0,
        })
        if len(self.data["open_questions"]) > self.MAX_QUESTIONS:
            # 중요도 낮은 것 제거
            self.data["open_questions"].sort(key=lambda x: x.get("importance", 5), reverse=True)
            self.data["open_questions"] = self.data["open_questions"][:self.MAX_QUESTIONS]

    def update_concept_graph(self, concept: str, related: list):
        """개념 간 관계 그물망 업데이트."""
        if not concept:
            return
        existing = self.data["concept_graph"].setdefault(concept, [])
        for r in related:
            if r and r not in existing:
                existing.append(r)
        if len(existing) > 20:
            self.data["concept_graph"][concept] = existing[-20:]

    def update_domain(self, domain: str, insight: str):
        """도메인 전문성 누적."""
        if not domain or not insight:
            return
        dom = self.data["domain_knowledge"].setdefault(domain, [])
        dom.append(insight[:200])
        if len(dom) > 50:
            self.data["domain_knowledge"][domain] = dom[-50:]

    # ── 지식 검색 ───────────────────────────────────────────────────

    def get_relevant_context(self, topic: str, max_items: int = 8) -> str:
        """현재 주제와 관련된 과거 지식·이론·질문을 검색하여 컨텍스트로 반환."""
        if not topic:
            return ""

        topic_words = set(w.lower() for w in topic.split() if len(w) > 2)
        lines = []

        # 관련 발견 검색
        scored = []
        for d in self.data["discoveries"]:
            text = d.get("text", "").lower()
            score = sum(1 for w in topic_words if w in text)
            if score > 0:
                scored.append((score, d["text"]))
        scored.sort(reverse=True)
        if scored:
            lines.append("▶ 관련 과거 발견:")
            for _, text in scored[:max_items]:
                lines.append(f"  ★ {text[:180]}")

        # 관련 이론 (가장 강력한 기능: 과거 세션에서 만든 이론 재활용)
        theory_scored = []
        for t in self.data.get("theories", []):
            name = t.get("name", "").lower()
            axioms_text = " ".join(t.get("axioms", [])).lower()
            combined = name + " " + axioms_text
            score = sum(1 for w in topic_words if w in combined)
            if score > 0:
                theory_scored.append((score, t))
        theory_scored.sort(reverse=True)
        if theory_scored:
            lines.append("▶ 관련 누적 이론 (과거 세션에서 창조됨):")
            for _, t in theory_scored[:3]:
                sc = t.get("session_count", 1)
                lines.append(f"  🔭 [{t.get('id','')}] {t.get('name','')} (세션 {sc}회)")
                for ax in t.get("axioms", [])[:2]:
                    lines.append(f"    · {ax[:120]}")

        # 관련 미해결 질문 (답을 찾아야 할 깊은 질문들)
        q_scored = []
        for q in self.data.get("open_questions", []):
            qtext = q.get("q", "").lower()
            score = sum(1 for w in topic_words if w in qtext)
            if score > 0:
                q_scored.append((score + q.get("importance", 5) / 10, q))
        q_scored.sort(reverse=True)
        if q_scored:
            lines.append("▶ 아직 답을 못 찾은 깊은 질문들:")
            for _, q in q_scored[:3]:
                lines.append(f"  ❓ {q.get('q','')[:150]}")

        # 패러다임 파괴 이력
        pb_scored = []
        for pb in self.data.get("paradigm_breaks", []):
            text = (pb.get("old", "") + " " + pb.get("new", "")).lower()
            score = sum(1 for w in topic_words if w in text)
            if score > 0:
                pb_scored.append((score, pb))
        pb_scored.sort(reverse=True)
        if pb_scored:
            lines.append("▶ 파괴된 패러다임 이력 (이것을 넘어서 생각하세요):")
            for _, pb in pb_scored[:2]:
                lines.append(f"  💥 [파괴됨] {pb.get('old','')[:80]}")
                lines.append(f"     → [새 관점] {pb.get('new','')[:80]}")

        # 관련 세션
        recent_relevant = []
        for s in reversed(self.data["sessions"][-20:]):
            t = s.get("topic", "").lower()
            if any(w in t for w in topic_words):
                recent_relevant.append(s)
        if recent_relevant:
            lines.append("▶ 관련 과거 세션:")
            for s in recent_relevant[:3]:
                lines.append(f"  [{s.get('ts','')[:10]}] {s.get('topic','')[:80]}")
                for disc in s.get("key_discoveries", [])[:2]:
                    lines.append(f"    → {disc[:120]}")

        # 성공 패턴
        if self.data["success_patterns"]:
            lines.append("▶ 검증된 성공 패턴:")
            for p in self.data["success_patterns"][-4:]:
                lines.append(f"  ✅ {p[:120]}")

        # 실패 패턴
        if self.data["failure_patterns"]:
            lines.append("▶ 피해야 할 패턴:")
            for p in self.data["failure_patterns"][-3:]:
                lines.append(f"  ✗ {p[:120]}")

        return "\n".join(lines) if lines else ""

    def build_brain_prompt_block(self, topic: str) -> str:
        """프롬프트에 주입할 Brain 컨텍스트 블록 — 완전한 교차-세션 기억 주입."""
        ctx = self.get_relevant_context(topic)

        # 누적 통계 요약
        stats = self._stats_line()
        total_sessions = self.data.get("total_sessions", 0)
        total_steps = self.data.get("total_steps", 0)

        # 최근 5개 세션 요약 (주제와 무관하게 항상 포함)
        recent_sessions_lines = []
        recent_sessions = self.data.get("sessions", [])[-5:]
        if recent_sessions:
            recent_sessions_lines.append("▶ 최근 세션 히스토리 (절대 망각 없음):")
            for s in reversed(recent_sessions):
                ts = s.get("ts", "")[:16]
                t  = s.get("topic", "")[:80]
                steps = s.get("steps_completed", "?")
                mode  = s.get("mode", "")
                recent_sessions_lines.append(f"  [{ts}] [{mode}] {t}  ({steps}스텝)")
                for disc in s.get("key_discoveries", [])[:3]:
                    recent_sessions_lines.append(f"    ✦ {disc[:120]}")
        recent_sessions_text = "\n".join(recent_sessions_lines)

        # 도메인 지식 요약
        domain_lines = []
        domain_knowledge = self.data.get("domain_knowledge", {})
        if domain_knowledge:
            # 주제와 연관된 도메인 우선 추출
            topic_words = set(w.lower() for w in topic.split() if len(w) > 2)
            matched_domains = []
            for dom, insights in domain_knowledge.items():
                if any(w in dom.lower() for w in topic_words):
                    matched_domains.append((dom, insights))
            # 연관 없으면 최근 3개 도메인
            if not matched_domains:
                matched_domains = list(domain_knowledge.items())[-3:]
            if matched_domains:
                domain_lines.append("▶ 누적 도메인 전문 지식:")
                for dom, insights in matched_domains[:3]:
                    domain_lines.append(f"  [{dom}]")
                    for ins in insights[-3:]:
                        domain_lines.append(f"    · {ins[:120]}")
        domain_text = "\n".join(domain_lines)

        # 상위 이론 (검증된 것 우선)
        all_theories = self.data.get("theories", [])
        top_theories = sorted(all_theories, key=lambda t: (t.get("verified", False), t.get("session_count", 1)), reverse=True)[:5]
        theory_lines = []
        if top_theories:
            theory_lines.append("▶ 상위 축적 이론 (검증/세션 순):")
            for t in top_theories:
                status = "✅검증됨" if t.get("verified") else ("❌반증됨" if t.get("refuted") else "🔬미검증")
                theory_lines.append(f"  {status} [{t.get('id','')}] {t.get('name','')} (세션 {t.get('session_count',1)}회)")
                for ax in t.get("axioms", [])[:2]:
                    theory_lines.append(f"    · {ax[:120]}")
        theory_text = "\n".join(theory_lines)

        # 최고 중요도 미해결 질문
        open_qs = sorted(self.data.get("open_questions", []), key=lambda q: -q.get("importance", 5))[:5]
        q_lines = []
        if open_qs:
            q_lines.append("▶ 최우선 미해결 질문 (중요도 순):")
            for q in open_qs:
                q_lines.append(f"  ❓ (중요도 {q.get('importance',5)}) {q.get('q','')[:150]}")
        q_text = "\n".join(q_lines)

        if not any([ctx, recent_sessions_text, domain_text, theory_text, q_text]):
            return ""

        parts = []
        if ctx:
            parts.append(ctx)
        if recent_sessions_text:
            parts.append(recent_sessions_text)
        if domain_text:
            parts.append(domain_text)
        if theory_text:
            parts.append(theory_text)
        if q_text:
            parts.append(q_text)

        full_ctx = "\n".join(parts)

        return (
            f"\n{'═'*65}\n"
            f"🧠 NEXUS BRAIN — 완전한 교차-세션 기억 ({stats})\n"
            f"   총 {total_sessions}세션 · 총 {total_steps}스텝 누적 — 절대 망각 없음\n"
            f"{'─'*65}\n"
            f"{full_ctx}\n"
            f"{'═'*65}\n"
            f"⚡ 위 누적 지식을 완전히 흡수하여 이번 세션에 반영하세요.\n"
        )

    def _stats_line(self) -> str:
        n_theories = len(self.data.get("theories", []))
        n_questions = len(self.data.get("open_questions", []))
        n_paradigm_breaks = len(self.data.get("paradigm_breaks", []))
        return (
            f"{self.data['total_sessions']}세션 · "
            f"{len(self.data['discoveries'])}발견 · "
            f"{n_theories}이론 · "
            f"{n_questions}미해결질문 · "
            f"{n_paradigm_breaks}패러다임파괴"
        )

    def get_preferred_mode(self) -> str:
        prefs = self.data["user_style"].get("preferred_modes", {})
        if not prefs:
            return "innovate"
        return max(prefs, key=prefs.get)

    def semantic_search(self, query: str, pool: str = "all", top_k: int = 5) -> List[Dict]:
        """
        키워드 기반 유사도 검색.
        pool: 'discoveries' | 'theories' | 'questions' | 'all'
        """
        qwords = set(w.lower() for w in query.split() if len(w) > 1)
        results = []

        def _score(text: str) -> float:
            words = set(w.lower() for w in text.split())
            if not qwords or not words:
                return 0.0
            return len(qwords & words) / len(qwords | words)

        if pool in ("discoveries", "all"):
            for d in self.data["discoveries"]:
                s = _score(d.get("text", ""))
                if s > 0:
                    results.append({"type": "discovery", "score": s, "text": d["text"][:200], "domain": d.get("domain","")})
        if pool in ("theories", "all"):
            for t in self.data.get("theories", []):
                combined = t.get("name","") + " " + " ".join(t.get("axioms",[]))
                s = _score(combined)
                if s > 0:
                    results.append({"type": "theory", "score": s, "name": t["name"], "novelty": t.get("novelty_score",0)})
        if pool in ("questions", "all"):
            for q in self.data.get("open_questions", []):
                s = _score(q.get("q",""))
                if s > 0:
                    results.append({"type": "question", "score": s, "text": q["q"][:200], "importance": q.get("importance",5)})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def export_markdown(self, output_path: Optional[str] = None) -> str:
        """Brain 전체 지식을 Markdown으로 export."""
        lines = [
            "# NEXUS Brain — 지식 아카이브",
            f"*{datetime.now().strftime('%Y-%m-%d %H:%M')} · {self._stats_line()}*",
            "",
            "## 📚 이론",
        ]
        for t in self.data.get("theories", [])[:20]:
            lines.append(f"### {t.get('name','?')} (novelty={t.get('novelty_score','?')})")
            for ax in t.get("axioms", []):
                lines.append(f"- {ax}")
            lines.append("")
        lines += ["## 🌟 주요 발견 (최근 30개)"]
        for d in self.data["discoveries"][-30:]:
            lines.append(f"- [{d.get('domain','')}] {d.get('text','')[:180]}")
        lines += ["", "## ❓ 미해결 질문"]
        for q in sorted(self.data.get("open_questions",[]), key=lambda x: -x.get("importance",5))[:20]:
            lines.append(f"- (중요도 {q.get('importance',5)}) {q.get('q','')[:200]}")
        lines += ["", "## 💥 파괴된 패러다임"]
        for pb in self.data.get("paradigm_breaks",[])[-10:]:
            lines.append(f"- ~~{pb.get('old','')}~~  →  **{pb.get('new','')}**")
        md = "\n".join(lines)
        path = output_path or str(Path.home() / "nexus_brain_export.md")
        Path(path).write_text(md, encoding="utf-8")
        print(f"[NexusBrain] Markdown export: {path}")
        return path

    def merge_from(self, other_brain_path: str):
        """다른 Brain 파일에서 지식 병합 (지식 공유)."""
        try:
            other = json.loads(Path(other_brain_path).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[NexusBrain] 병합 실패: {e}")
            return
        merged = {"discoveries": 0, "theories": 0, "questions": 0}
        for d in other.get("discoveries", []):
            if not any(e["text"] == d["text"] for e in self.data["discoveries"][-100:]):
                self.data["discoveries"].append(d)
                merged["discoveries"] += 1
        for t in other.get("theories", []):
            if not any(e.get("id") == t.get("id") for e in self.data["theories"]):
                self.data["theories"].append(t)
                merged["theories"] += 1
        for q in other.get("open_questions", []):
            if not any(e["q"] == q["q"] for e in self.data["open_questions"]):
                self.data["open_questions"].append(q)
                merged["questions"] += 1
        self.save()
        print(f"[NexusBrain] 병합 완료: {merged}")


# ═══════════════════════════════════════════════════════════════════════
#  MODEL REGISTRY — NIM 모델 동적 FETCH + 역할별 자동 선택
# ═══════════════════════════════════════════════════════════════════════

class ModelRegistry:
    """
    NVIDIA NIM에서 사용 가능한 모델 목록을 실시간으로 가져와
    사용자가 직접 역할별 모델을 선택할 수 있게 합니다.

    - 실시간 fetch → 번호 목록 표시 → 사용자 선택
    - 선택하지 않으면 AI가 자동으로 최적 모델 선택
    - 역할: planner(계획), coder(구현), writer(합성), innovator(창의)
    """

    NIM_MODELS_URL = "https://integrate.api.nvidia.com/v1/models"

    # ── 역할별 모델 선택 우선순위 (키워드 매칭 순서 = 우선순위) ──────────
    # 2025-2026 NVIDIA NIM 최신 최강 모델 기준으로 업데이트
    ROLE_PREFS: Dict[str, List[str]] = {
        # 🧠 Planner: 추론/사고가 핵심 — thinking 모드 모델 우선
        "planner":   [
            "qwen3-next-80b-a3b-thinking",   # Qwen3-Next Thinking: 80B, 하이브리드 추론
            "qwen3.5-397b-a17b",             # Qwen3.5 397B MoE VLM: 초대형 추론
            "deepseek-r1",                   # DeepSeek-R1: o1급 추론
            "qwq-32b",                       # QwQ-32B: 강력한 reasoning 모델
            "qwen3-next-80b-a3b-instruct",   # Qwen3-Next Instruct 폴백
            "deepseek-r1-distill-qwen-32b",  # R1 distill Qwen 32B
            "deepseek-r1-distill-qwen-14b",  # R1 distill Qwen 14B
            "r1", "reasoning", "think",
        ],
        # 💻 Coder: 코드 생성/실행 — 코딩 특화 모델 우선
        "coder":     [
            "qwen3-coder-480b-a35b-instruct",  # Qwen3-Coder 480B: 현존 최강 코딩
            "qwen2.5-coder-32b-instruct",      # Qwen2.5-Coder 32B: 검증된 코딩 강자
            "qwen3.5-122b-a10b",               # Qwen3.5 122B: 코딩+추론 범용
            "deepseek-v3",                     # DeepSeek-V3.1: 강력한 범용+코딩
            "qwen2.5-coder-7b-instruct",       # 경량 코딩 폴백
            "codestral", "deepseek-coder", "starcoder", "code",
        ],
        # 🔍 Critic: 비평/검증 — 대형 범용 모델
        "critic":    [
            "qwen3.5-397b-a17b",             # Qwen3.5 397B: 최대 파라미터 비평
            "llama-3.3-70b",                 # Llama 3.3 70B: 검증된 비평 능력
            "llama-nemotron-70b",            # Nemotron 70B: NVIDIA 최적화
            "mistral-large",                 # Mistral Large: 강력한 분석
            "gemma-4-27b",                   # Gemma 4 27B
            "llama-3.1-70b", "mistral", "gemma",
        ],
        # ✍️  Writer: 논문/이론/합성 — 대형 범용 모델
        "writer":    [
            "qwen3.5-397b-a17b",             # Qwen3.5 397B: 긴 문서 생성 최강
            "qwen3.5-122b-a10b",             # Qwen3.5 122B: 범용 고품질 생성
            "llama-3.3-70b",                 # Llama 3.3 70B: 검증된 글쓰기
            "llama-nemotron-70b",            # Nemotron 70B
            "minimax-m2",                    # MiniMax M2.7: 230B MoE 범용
            "qwen2.5-7b-instruct",           # 경량 폴백
            "llama-3.1-70b", "qwen", "mixtral",
        ],
        # 🚀 Innovator: 창의적 혁신 — 최대 파라미터 + 추론 모델
        "innovator": [
            "qwen3.5-397b-a17b",             # Qwen3.5 397B: 최대 창의성
            "qwen3-next-80b-a3b-thinking",   # Qwen3-Next Thinking: 하이브리드 추론
            "deepseek-r1",                   # DeepSeek-R1: 창의적 추론
            "llama-3.1-405b",                # Llama 405B: 초대형 창의성
            "nemotron", "deepseek", "qwq",
        ],
    }

    # ── 역할별 하드코딩 폴백 (API fetch 실패 시 사용) ────────────────────
    # 2026년 4월 기준 NVIDIA NIM build.nvidia.com 에서 검증된 최강 모델 ID
    FALLBACK: Dict[str, str] = {
        "planner":   "qwen/qwen3-next-80b-a3b-thinking",      # Thinking 전용 추론 모델
        "coder":     "qwen/qwen3-coder-480b-a35b-instruct",   # 480B 아젠틱 코딩 최강
        "critic":    "qwen/qwen3.5-397b-a17b",                # 397B VLM 비평
        "writer":    "qwen/qwen3.5-122b-a10b",                # 122B MoE 글쓰기
        "innovator": "qwen/qwen3.5-397b-a17b",                # 최대 파라미터 혁신
    }

    def __init__(self, api_key: str, verbose: bool = True):
        self.api_key = api_key
        self.verbose = verbose
        self.models: List[Dict] = []
        self.model_ids: List[str] = []
        self._fetch()

    def _fetch(self):
        try:
            resp = requests.get(
                self.NIM_MODELS_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                self.models = data.get("data", [])
                self.model_ids = [m["id"] for m in self.models]
                if self.verbose:
                    print(f"[ModelRegistry] {len(self.model_ids)}개 모델 감지")
            else:
                self._log(f"API 응답 {resp.status_code} — 폴백 모델 사용")
        except Exception as e:
            self._log(f"모델 목록 가져오기 실패: {e} — 폴백 모델 사용")

    def select(self, role: str) -> str:
        keywords = self.ROLE_PREFS.get(role, [])
        for kw in keywords:
            for mid in self.model_ids:
                if kw in mid.lower():
                    return mid
        return self.FALLBACK.get(role, "meta/llama-3.3-70b-instruct")

    def select_pair(self) -> Tuple[str, str]:
        return self.select("planner"), self.select("coder")

    def list_by_role(self) -> Dict[str, str]:
        result = {}
        for role in self.ROLE_PREFS:
            result[role] = self.select(role)
        return result

    def interactive_select(self) -> Dict[str, str]:
        """
        사용자가 직접 역할별 모델을 선택하는 인터랙티브 UI.
        반환: {"planner": "...", "coder": "...", "writer": "..."}
        """
        if not self.model_ids:
            print("  ⚠️  모델 목록을 가져오지 못했습니다. 자동 선택으로 진행합니다.")
            return {role: self.select(role) for role in ["planner", "coder", "writer"]}

        # 모델 목록 출력
        sorted_models = sorted(self.model_ids)
        print(f"\n{'─'*70}")
        print(f"  🔮 NVIDIA NIM 사용 가능한 모델 ({len(sorted_models)}개)")
        print(f"{'─'*70}")
        for idx, mid in enumerate(sorted_models, 1):
            # 모델 태그 표시
            tags = []
            mid_lower = mid.lower()
            if any(k in mid_lower for k in ["r1", "qwq", "reasoning"]):
                tags.append("🧠추론")
            if any(k in mid_lower for k in ["coder", "code", "starcoder"]):
                tags.append("💻코딩")
            if any(k in mid_lower for k in ["70b", "405b", "nemotron"]):
                tags.append("🔥대형")
            if any(k in mid_lower for k in ["qwen", "llama", "mistral"]):
                tags.append("⚡범용")
            tag_str = " ".join(tags) if tags else ""
            print(f"  [{idx:3d}] {mid:<55} {tag_str}")
        print(f"{'─'*70}")
        print("  0  = 자동 선택 (AI가 역할별 최적 모델 선택)")
        print(f"{'─'*70}\n")

        selected = {}
        roles_info = [
            ("planner",  "🧠 Planner  (계획·추론 담당 — 추론 모델 추천)"),
            ("coder",    "💻 Coder    (코드 생성·실행 담당 — 코딩 모델 추천)"),
            ("writer",   "✍️  Writer   (논문·이론·합성 담당 — 대형 범용 추천)"),
        ]
        for role, label in roles_info:
            auto_pick = self.select(role)
            auto_idx = sorted_models.index(auto_pick) + 1 if auto_pick in sorted_models else 0
            print(f"  {label}")
            print(f"  (자동 선택: [{auto_idx}] {auto_pick.split('/')[-1]})")
            while True:
                raw = input(f"  번호 선택 [0=자동/{auto_idx}]: ").strip()
                if raw == "" or raw == "0":
                    selected[role] = auto_pick
                    print(f"  → {auto_pick.split('/')[-1]} (자동)\n")
                    break
                try:
                    n = int(raw)
                    if 1 <= n <= len(sorted_models):
                        chosen = sorted_models[n - 1]
                        selected[role] = chosen
                        print(f"  → {chosen}\n")
                        break
                    else:
                        print(f"  ⚠️  1~{len(sorted_models)} 범위로 입력하세요.")
                except ValueError:
                    print("  ⚠️  숫자를 입력하세요.")

        return selected

    def print_available(self):
        if not self.model_ids:
            print("[ModelRegistry] 모델 목록 없음 (폴백 사용)")
            return
        print(f"\n{'─'*60}")
        print(f"  사용 가능한 NIM 모델 ({len(self.model_ids)}개):")
        print(f"{'─'*60}")
        for mid in sorted(self.model_ids):
            print(f"  • {mid}")
        print(f"{'─'*60}")
        print("\n  역할별 자동 선택:")
        for role, model in self.list_by_role().items():
            print(f"  [{role:10s}] {model}")

    def _log(self, msg: str):
        if self.verbose:
            print(f"[ModelRegistry] {msg}")


# ═══════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ExecutionResult:
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    success: bool = True
    duration: float = 0.0
    variables_snapshot: Dict[str, str] = field(default_factory=dict)
    colab_output: str = ""  # Colab 중단점에서 받은 결과

    def summary(self, max_chars: int = 3000) -> str:
        parts = []
        if self.colab_output.strip():
            parts.append(f"[COLAB OUTPUT]\n{self.colab_output[:max_chars]}")
        elif self.stdout.strip():
            parts.append(f"[OUTPUT]\n{self.stdout[:max_chars]}")
        if self.error:
            parts.append(f"[ERROR]\n{self.error[:1000]}")
        elif self.stderr.strip():
            parts.append(f"[STDERR]\n{self.stderr[:400]}")
        parts.append(f"[STATUS] {'✅ SUCCESS' if self.success else '❌ FAILED'} "
                     f"in {self.duration:.2f}s")
        return "\n".join(parts)

    def is_empty(self) -> bool:
        return (not self.stdout.strip() and not self.error
                and not self.colab_output.strip())


@dataclass
class ResearchStep:
    id: int
    title: str
    objective: str
    hypothesis: str = ""
    expected_output: str = ""
    surprise_factor: str = ""
    innovation_angle: str = ""
    alternative_approach: str = ""
    grand_challenge_link: str = ""   # 인류 난제와의 연결
    code: str = ""
    result: Optional[ExecutionResult] = None
    attempts: int = 0
    max_attempts: int = 10
    succeeded: bool = False
    insights: List[str] = field(default_factory=list)
    novel_findings: List[str] = field(default_factory=list)
    creativity_score: float = 0.0

    def status_emoji(self) -> str:
        if self.succeeded: return "✅"
        if self.attempts >= self.max_attempts: return "❌"
        if self.attempts > 0: return "🔄"
        return "⏳"

    def to_dict(self) -> dict:
        r = asdict(self)
        if self.result:
            r["result"] = {
                "stdout": self.result.stdout[:2000],
                "colab_output": self.result.colab_output[:2000],
                "error": self.result.error,
                "success": self.result.success,
                "duration": self.result.duration,
            }
        return r


@dataclass
class ResearchPlan:
    research_question: str = ""
    hypotheses: List[str] = field(default_factory=list)
    methodology: str = ""
    innovation_angle: str = ""
    grand_challenge: str = ""         # 어떤 인류 난제를 다루는가
    wild_ideas: List[str] = field(default_factory=list)
    interdisciplinary: List[str] = field(default_factory=list)
    packages_needed: List[str] = field(default_factory=list)
    steps: List[ResearchStep] = field(default_factory=list)
    target_outputs: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "ResearchPlan":
        plan = cls(
            research_question=d.get("research_question", ""),
            hypotheses=d.get("hypotheses", []),
            methodology=d.get("methodology", ""),
            innovation_angle=d.get("innovation_angle", ""),
            grand_challenge=d.get("grand_challenge", ""),
            wild_ideas=d.get("wild_ideas", []),
            interdisciplinary=d.get("interdisciplinary_fields", []),
            packages_needed=d.get("packages_needed", []),
            target_outputs=d.get("target_outputs", []),
        )
        for s in d.get("steps", []):
            plan.steps.append(ResearchStep(
                id=s.get("id", len(plan.steps) + 1),
                title=s.get("title", f"Step {len(plan.steps)+1}"),
                objective=s.get("objective", ""),
                hypothesis=s.get("hypothesis_tested", s.get("hypothesis", "")),
                expected_output=s.get("expected_output", ""),
                surprise_factor=s.get("surprise_factor", ""),
                innovation_angle=s.get("innovation_angle", ""),
                alternative_approach=s.get("alternative_approach", ""),
                grand_challenge_link=s.get("grand_challenge_link", ""),
            ))
        return plan


class ResearchMemory:
    """전체 연구 세션 메모리 + 디스크 체크포인트."""

    def __init__(self, prompt: str, checkpoint_dir: str = ".nexus_checkpoints"):
        self.prompt = prompt
        self.plan: Optional[ResearchPlan] = None
        self.completed_steps: List[ResearchStep] = []
        self.global_insights: List[str] = []
        self.novel_discoveries: List[str] = []
        self.failed_approaches: List[str] = []
        self.creative_branches: List[Dict] = []
        self.session_start = datetime.now()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def add_completed_step(self, step: ResearchStep):
        self.completed_steps.append(step)
        if step.insights:
            self.global_insights.extend(step.insights)
        if step.novel_findings:
            self.novel_discoveries.extend(step.novel_findings)

    def add_failure(self, description: str):
        self.failed_approaches.append(description)

    def add_creative_branch(self, trigger: str, idea: str):
        self.creative_branches.append({
            "step": len(self.completed_steps),
            "trigger": trigger,
            "idea": idea,
            "timestamp": datetime.now().isoformat(),
        })

    def get_context_for_next_step(self, max_chars: int = 5000) -> str:
        lines = []
        recent = self.completed_steps[-5:]
        if recent:
            lines.append("=== 최근 실험 결과 ===")
            for step in recent:
                lines.append(f"\n[Step {step.id}: {step.title}] {'✅' if step.succeeded else '❌'}")
                lines.append(f"목표: {step.objective[:150]}")
                # 로컬 출력 또는 Colab 출력 우선
                out_text = ""
                if step.result:
                    out_text = (step.result.colab_output.strip()
                                or step.result.stdout.strip())
                if out_text:
                    lines.append(f"출력:\n{out_text[:800]}")
                if step.insights:
                    lines.append(f"인사이트: {'; '.join(step.insights[:3])}")
                if step.novel_findings:
                    lines.append(f"🌟 새로운 발견: {'; '.join(step.novel_findings[:2])}")

        if self.novel_discoveries:
            lines.append("\n=== 🌟 혁신적 발견사항 ===")
            for d in self.novel_discoveries[-5:]:
                lines.append(f"★ {d}")

        if self.global_insights:
            lines.append("\n=== 누적 인사이트 ===")
            for ins in self.global_insights[-8:]:
                lines.append(f"• {ins}")

        if self.creative_branches:
            lines.append("\n=== 창의적 탐색 기회 ===")
            for b in self.creative_branches[-3:]:
                lines.append(f"💡 {b['idea'][:120]}")

        if self.failed_approaches:
            lines.append("\n=== 피해야 할 접근법 ===")
            for f in self.failed_approaches[-5:]:
                lines.append(f"✗ {f}")

        # 실행 통계 요약
        if self.completed_steps:
            total = len(self.completed_steps)
            ok = sum(1 for s in self.completed_steps if s.succeeded)
            avg_score = sum(s.creativity_score for s in self.completed_steps) / total
            lines.append(f"\n=== 진행 통계 ===")
            lines.append(f"완료: {total}단계 · 성공: {ok} · 창의성 평균: {avg_score:.1f}")

        return "\n".join(lines)[:max_chars]

    def save_checkpoint(self, step_index: int) -> str:
        ckpt = {
            "prompt": self.prompt,
            "session_id": self.session_id,
            "step_index": step_index,
            "global_insights": self.global_insights,
            "novel_discoveries": self.novel_discoveries,
            "failed_approaches": self.failed_approaches,
            "creative_branches": self.creative_branches,
            "completed_steps": [s.to_dict() for s in self.completed_steps],
            "saved_at": datetime.now().isoformat(),
        }
        path = self.checkpoint_dir / f"ckpt_{self.session_id}.json"
        path.write_text(json.dumps(ckpt, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str) -> Tuple["ResearchMemory", int]:
        data = json.loads(Path(checkpoint_path).read_text(encoding="utf-8"))
        mem = cls(data["prompt"])
        mem.session_id = data["session_id"]
        mem.global_insights = data["global_insights"]
        mem.novel_discoveries = data.get("novel_discoveries", [])
        mem.failed_approaches = data["failed_approaches"]
        mem.creative_branches = data.get("creative_branches", [])
        for s in data["completed_steps"]:
            step = ResearchStep(id=s["id"], title=s["title"], objective=s["objective"])
            step.succeeded = s.get("succeeded", True)
            step.insights = s.get("insights", [])
            step.novel_findings = s.get("novel_findings", [])
            mem.completed_steps.append(step)
        return mem, data["step_index"]

    def get_statistics(self) -> Dict:
        total = len(self.completed_steps)
        succeeded = sum(1 for s in self.completed_steps if s.succeeded)
        total_time = sum(
            s.result.duration for s in self.completed_steps
            if s.result and s.result.duration
        )
        return {
            "total_steps": total,
            "succeeded": succeeded,
            "success_rate": f"{succeeded/max(total,1)*100:.1f}%",
            "total_time": f"{total_time:.1f}s",
            "insights": len(self.global_insights),
            "novel_discoveries": len(self.novel_discoveries),
            "creative_branches": len(self.creative_branches),
        }


# ═══════════════════════════════════════════════════════════════════════
#  CODE EXECUTOR — 결과 캡처 + 타임아웃 + Colab 중단점
# ═══════════════════════════════════════════════════════════════════════

class CodeExecutor:
    """
    Python 코드 실행 엔진.
    - stdout/stderr/예외 완전 캡처
    - 영속 네임스페이스 (단계 간 변수 유지)
    - 스레드 기반 타임아웃 (무한 루프 방지)
    - Figure 자동 저장
    - Colab 중단점 자동 감지 (# NEXUS_COLAB_REQUIRED)
    """

    SNAPSHOT_TYPES = (int, float, str, bool, list, dict, tuple)
    MAX_VAR_REPR = 300

    def __init__(self, output_dir: str = "nexus_outputs"):
        self.namespace: Dict[str, Any] = {}
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._bootstrap()

    def _bootstrap(self):
        bootstrap = textwrap.dedent("""
            import warnings; warnings.filterwarnings('ignore')
            import numpy as np
            import pandas as pd
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import os, sys, time, json, re, math, random, itertools, functools
            from datetime import datetime
            from collections import defaultdict, Counter
            from pathlib import Path

            plt.rcParams.update({
                'figure.dpi': 130,
                'figure.figsize': (12, 7),
                'axes.facecolor': '#0d0d18',
                'figure.facecolor': '#0d0d18',
                'text.color': '#e8e8f8',
                'axes.labelcolor': '#c0c0e0',
                'xtick.color': '#888',
                'ytick.color': '#888',
                'axes.edgecolor': '#2a2a45',
                'grid.color': '#2a2a45',
                'grid.alpha': 0.4,
                'lines.linewidth': 2.0,
                'font.size': 11,
                'axes.titlesize': 14,
                'axes.titleweight': 'bold',
            })

            NEXUS_SESSION = __import__('datetime').datetime.now()
            print(f"[NEXUS-v7] 환경 부트스트랩 완료 · {NEXUS_SESSION.strftime('%H:%M:%S')}")
            print(f"[NEXUS-v7] NumPy {np.__version__} · Pandas {pd.__version__}")
        """)
        try:
            exec(bootstrap, self.namespace)
        except Exception as e:
            print(f"[NEXUS] 부트스트랩 경고: {e}")

    def install_packages(self, packages: List[str]) -> bool:
        if not packages:
            return True
        print(f"[NEXUS] 패키지 설치: {', '.join(packages)}")
        for pkg in packages:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", pkg],
                    capture_output=True, text=True, timeout=180,
                )
                print(f"  {'✅' if result.returncode == 0 else '⚠️ '} {pkg}")
            except subprocess.TimeoutExpired:
                print(f"  ⏱️  {pkg}: 설치 타임아웃")
            except Exception as e:
                print(f"  ❌ {pkg}: {e}")
        return True

    def run(self, code: str, timeout: int = 300, step_id: int = 0) -> ExecutionResult:
        """타임아웃 지원 코드 실행. Colab 중단점 자동 처리."""

        # Colab 중단점 감지
        if ColabBreakpoint.is_required(code):
            colab_out = ColabBreakpoint.request_user_run(code, step_id)
            return ExecutionResult(
                stdout="",
                stderr="",
                error=None,
                success=True,
                duration=0.0,
                colab_output=colab_out,
            )

        # pip install 분리 처리
        pip_pkgs, exec_lines = [], []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith(("!pip install", "!pip3 install")):
                pkgs = stripped.split("install")[-1].strip().split()
                pip_pkgs.extend(p for p in pkgs if not p.startswith("-"))
            else:
                exec_lines.append(line)
        if pip_pkgs:
            self.install_packages(pip_pkgs)

        clean_code = "\n".join(exec_lines)
        if not clean_code.strip():
            return ExecutionResult(success=True, stdout="[패키지 설치 완료]")

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        result_container: Dict[str, Any] = {}
        start = time.time()

        def _run():
            try:
                with contextlib.redirect_stdout(stdout_buf), \
                     contextlib.redirect_stderr(stderr_buf):
                    exec(compile(clean_code, "<nexus_step>", "exec"), self.namespace)
                result_container["ok"] = True
            except Exception as exc:
                result_container["ok"] = False
                result_container["error"] = (
                    f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}"
                )

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        duration = time.time() - start

        if thread.is_alive():
            return ExecutionResult(
                stdout=stdout_buf.getvalue(),
                stderr=stderr_buf.getvalue(),
                error=f"⏱️  실행 타임아웃 ({timeout}s 초과)",
                success=False,
                duration=duration,
            )

        if result_container.get("ok"):
            return ExecutionResult(
                stdout=stdout_buf.getvalue(),
                stderr=stderr_buf.getvalue(),
                error=None,
                success=True,
                duration=duration,
                variables_snapshot=self._snapshot(),
            )
        else:
            return ExecutionResult(
                stdout=stdout_buf.getvalue(),
                stderr=stderr_buf.getvalue(),
                error=result_container.get("error", "알 수 없는 오류"),
                success=False,
                duration=duration,
            )

    def _snapshot(self) -> Dict[str, str]:
        snap = {}
        skip = ("__", "NEXUS_", "In", "Out", "get_ipython")
        for k, v in self.namespace.items():
            if any(k.startswith(s) for s in skip):
                continue
            if callable(v) and not isinstance(v, type):
                continue
            try:
                r = repr(v)
                if len(r) <= self.MAX_VAR_REPR:
                    snap[k] = r
            except Exception:
                pass
        return snap

    def save_figures(self, step_id: int) -> List[str]:
        saved = []
        try:
            plt_mod = self.namespace.get("plt")
            if plt_mod is None:
                return saved
            for i, fig_num in enumerate(plt_mod.get_fignums()):
                fig = plt_mod.figure(fig_num)
                fname = self.output_dir / f"nexus_step{step_id:03d}_fig{i+1}.png"
                fig.savefig(fname, bbox_inches="tight", dpi=130,
                            facecolor="#0d0d18")
                saved.append(str(fname))
                plt_mod.close(fig)
        except Exception as e:
            print(f"[NEXUS] Figure 저장 오류: {e}")
        return saved


# ═══════════════════════════════════════════════════════════════════════
#  NVIDIA NIM CLIENT — 스트리밍 지원 + 강화된 재시도
# ═══════════════════════════════════════════════════════════════════════

class NIMClient:
    BASE = "https://integrate.api.nvidia.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        self._call_count = 0
        self._token_count = 0
        self._error_log: List[Dict] = []   # API 에러 히스토리
        self._latencies: List[float] = []  # 응답 시간 추적

    def chat(
        self,
        messages: List[Dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 6000,
        retries: int = 5,
    ) -> str:
        self._call_count += 1
        _t0 = time.time()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.95,
            "stream": False,
        }
        last_err = ""
        for attempt in range(retries + 1):
            try:
                resp = self.session.post(
                    f"{self.BASE}/chat/completions",
                    json=payload,
                    timeout=180,
                )
                if resp.status_code == 429:
                    wait = min(10 * (attempt + 1), 60)
                    print(f"  [NIM] Rate limit — {wait}초 대기 ({attempt+1}/{retries})")
                    time.sleep(wait)
                    continue
                if resp.status_code == 503:
                    wait = 5 * (attempt + 1)
                    print(f"  [NIM] 서버 과부하 — {wait}초 대기")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                self._token_count += usage.get("total_tokens", 0)
                self._latencies.append(time.time() - _t0)
                return content
            except requests.exceptions.Timeout:
                last_err = "타임아웃"
                print(f"  [NIM] 타임아웃, 재시도 ({attempt+1}/{retries})")
                time.sleep(5)
            except Exception as e:
                last_err = str(e)
                if attempt < retries:
                    print(f"  [NIM] 오류: {e}, 재시도 ({attempt+1}/{retries})")
                    time.sleep(3 * (attempt + 1))
        raise RuntimeError(f"NIM API 실패 ({retries}회 재시도): {last_err}")

    def chat_json(self, messages: List[Dict], model: str,
                  temperature: float = 0.3, max_tokens: int = 4000) -> Dict:
        last_err = None
        raw = ""
        for attempt in range(4):
            try:
                raw = self.chat(messages, model, temperature, max_tokens)
                cleaned = self._extract_json(raw)
                result = json.loads(cleaned)
                # 빈 dict/list 는 실패로 간주하지 않음 — 호출자가 판단
                if isinstance(result, (dict, list)):
                    return result
                raise ValueError(f"JSON이 dict/list가 아님: {type(result)}")
            except (json.JSONDecodeError, ValueError) as e:
                last_err = e
                if attempt < 3:
                    print(f"  [NIM] JSON 파싱 실패, 재시도 ({attempt+1}/3): {e}")
                    messages = messages + [
                        {"role": "assistant", "content": raw},
                        {"role": "user", "content":
                         "위 응답을 순수 JSON으로만 다시 출력하세요. "
                         "마크다운 블록 없이, 설명 없이, <think> 태그 없이, JSON만."},
                    ]
        print(f"  [NIM] JSON 파싱 최종 실패 (4회 시도): {last_err}")
        return {}

    @staticmethod
    def _extract_json(text: str) -> str:
        """응답 텍스트에서 첫 번째 유효한 JSON 객체/배열을 추출.

        처리 순서:
        1. <think>...</think> 블록 제거 (LLM reasoning 출력)
        2. 마크다운 코드 블록 제거
        3. BOM / null 바이트 제거
        4. raw_decode 로 첫 번째 유효 JSON 추출
        5. trailing comma 제거 후 재시도
        6. 수동 브라켓 매칭 (최후 fallback)
        """
        if not text:
            return "{}"

        # ── 1. <think>...</think> 블록 제거 ──────────────────────────────
        text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)

        # ── 2. 마크다운 코드 블록 제거 ────────────────────────────────────
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)

        # ── 3. BOM / null 바이트 / 제어문자 정리 ─────────────────────────
        text = text.lstrip("\ufeff").replace("\x00", "")
        text = text.strip()

        if not text:
            return "{}"

        # ── 4. raw_decode: 처음 발견되는 유효 JSON 추출 ──────────────────
        decoder = json.JSONDecoder()
        for start in range(len(text)):
            if text[start] not in ('{', '['):
                continue
            try:
                obj, _ = decoder.raw_decode(text, start)
                return json.dumps(obj, ensure_ascii=False)
            except json.JSONDecodeError:
                continue

        # ── 5. trailing comma 제거 후 재시도 ──────────────────────────────
        # 예: {"key": "val",}  /  [1, 2,]
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        if cleaned != text:
            decoder2 = json.JSONDecoder()
            for start in range(len(cleaned)):
                if cleaned[start] not in ('{', '['):
                    continue
                try:
                    obj, _ = decoder2.raw_decode(cleaned, start)
                    return json.dumps(obj, ensure_ascii=False)
                except json.JSONDecodeError:
                    continue

        # ── 6. 수동 브라켓 매칭 (최후 fallback) ──────────────────────────
        for open_ch, close_ch in [('{', '}'), ('[', ']')]:
            start = text.find(open_ch)
            if start == -1:
                continue
            depth = 0
            in_str = False
            escape = False
            for i, ch in enumerate(text[start:], start):
                if escape:
                    escape = False
                    continue
                if ch == '\\' and in_str:
                    escape = True
                    continue
                if ch == '"':
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == open_ch:
                    depth += 1
                elif ch == close_ch:
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i + 1]
                        # trailing comma 제거 후 검증
                        candidate_clean = re.sub(r",\s*([}\]])", r"\1", candidate)
                        try:
                            json.loads(candidate_clean)
                            return candidate_clean
                        except json.JSONDecodeError:
                            return candidate

        return "{}"

    def get_stats(self) -> Dict:
        avg_lat = (sum(self._latencies) / len(self._latencies)) if self._latencies else 0
        return {
            "api_calls": self._call_count,
            "total_tokens": self._token_count,
            "avg_latency_s": round(avg_lat, 2),
            "p95_latency_s": round(sorted(self._latencies)[int(len(self._latencies)*0.95)] if self._latencies else 0, 2),
            "total_cost_est_usd": round(self._token_count / 1_000_000 * 0.8, 4),  # 추정
        }


# ═══════════════════════════════════════════════════════════════════════
#  CREATIVITY ENGINE — 창의성 극대화 엔진 (인류 난제 해결 특화)
# ═══════════════════════════════════════════════════════════════════════

class CreativityEngine:
    """
    AI 창의성을 극대화하는 엔진.
    인류 난제 해결을 위한 혁신적 사고 패턴 내장.

    기법:
    1. 레오나르도 다빈치 모드: 분야 경계 파괴
    2. 반직관 탐색: 당연한 것의 반대
    3. 융합 발상: 무관한 두 분야 연결
    4. 시간 여행 사고: 100년 후 관점
    5. 외계인 시각: 인간 전제를 제거
    6. 실패 역공학: 최악의 실패 → 최고의 발견
    7. 스케일 점프: 나노 → 우주 스케일 이동
    8. 대칭 파괴: 기존 대칭 가정 제거
    9. 난제 분해: 인류 난제를 계산 가능한 단위로 분해
    10. 창발 탐색: 단순한 규칙에서 복잡성이 출현하는 지점 탐구
    """

    THINKING_PERSONAS = [
        "라마누잔 (직관으로 증명 없이 진리에 도달하는 수학 천재)",
        "리처드 파인만 (제1원리로 모든 것을 다시 발명하는 물리학자)",
        "클로드 섀넌 (불확실성을 정보로 변환한 정보 이론의 창시자)",
        "앨런 튜링 (계산 가능성의 본질을 꿰뚫은 추상화의 달인)",
        "존 폰 노이만 (수학, 물리, 경제, 컴퓨터를 통합한 보편 천재)",
        "에바리스트 갈루아 (19세에 군론을 창시한 구조의 발견자)",
        "그레이스 호퍼 (컴파일러를 발명하여 프로그래밍 언어를 탄생시킨 혁신가)",
        "그레고리 페렐만 (세기의 난제를 혼자 풀어낸 고독한 천재)",
        "테렌스 타오 (현존 최고 수학자 — 분야 경계 없이 진리를 탐구)",
        "앤디 야오 (계산 복잡도와 암호학의 경계를 허문 알고리즘 거장)",
        "존 네시 (게임 이론으로 경제, 전쟁, 진화를 통합한 수학자)",
        "베르너 하이젠베르크 (불확정성 원리 — 앎의 한계 자체를 발명)",
    ]

    LATERAL_PROMPTS = [
        "이 문제를 생물학적 진화 알고리즘의 관점에서 재설계하면?",
        "음악의 화성 구조(푸가, 대위법)를 이 알고리즘에 적용하면?",
        "열역학 제2법칙(엔트로피 증가)이 이 시스템에서 무엇을 의미하는가?",
        "이 데이터를 리만 다양체 위의 측지선으로 해석하면?",
        "게임 이론의 내시 균형이 이 최적화 문제를 어떻게 재정의하는가?",
        "촘스키 계층 구조(정규/문맥자유/문맥의존/튜링)로 이 문제를 분류하면?",
        "양자 중첩과 얽힘이 이 알고리즘의 병렬성에 무엇을 가르치는가?",
        "경제학의 수확체증 법칙이 이 학습 곡선에서 숨겨진 패턴을 드러낸다면?",
        "이 문제의 쌍대(dual) 문제는 무엇이며, 쌍대가 더 쉬운가?",
        "위상수학의 불변량처럼 이 시스템에서 변하지 않는 것은 무엇인가?",
        "이 문제를 인류 100대 난제 중 하나와 연결하면 어떤 새로운 해법이 나오는가?",
        "단순한 세포 자동자(cellular automata) 규칙이 이 복잡계를 설명할 수 있는가?",
    ]

    # 인류 난제 목록 (연구 방향 연결용)
    GRAND_CHALLENGES = [
        "기후 변화와 탄소 중립 (에너지 효율, 탄소 포집)",
        "암 조기 진단과 치료 (유전체, 단백질 접힘)",
        "알츠하이머/파킨슨 등 신경퇴행성 질환",
        "항생제 내성균 (슈퍼박테리아 대응)",
        "양자 컴퓨팅 오류 내성",
        "인공 범용 지능 (AGI) 안전성",
        "핵융합 에너지 상용화",
        "식량 안보와 지속가능 농업",
        "물 부족과 해수 담수화",
        "P vs NP 문제 (계산 복잡도)",
        "단백질 설계와 신약 개발",
        "의식(Consciousness)의 계산적 이해",
    ]

    def get_creative_prompt_boost(self, step_objective: str, attempt: int) -> str:
        persona = self.THINKING_PERSONAS[attempt % len(self.THINKING_PERSONAS)]
        lateral = self.LATERAL_PROMPTS[attempt % len(self.LATERAL_PROMPTS)]
        challenge = self.GRAND_CHALLENGES[attempt % len(self.GRAND_CHALLENGES)]

        return f"""
🧠 창의성 극대화 모드 (시도 {attempt}):

현재 {persona}의 관점으로 생각하세요.
횡단적 질문: {lateral}
인류 난제 연결: 이 연구가 "{challenge}"에 어떤 기여를 할 수 있는가?

창의성 원칙:
• "불가능"이라는 단어 대신 → "어떻게 하면 가능할까?"
• 기존 논문을 인용하지 말고 → 직접 실험으로 발견하세요
• 예상된 결과보다 → 예상치 못한 결과를 더 가치 있게 여기세요
• 실패는 → 새로운 가설의 씨앗입니다
• 이 실험이 성공하면 → 인류의 어떤 문제가 해결되는가?

목표를 완전히 새로운 각도에서 접근하세요:
{step_objective}

가장 반직관적이지만 인류 난제와 연결되는 흥미로운 접근법은?
"""

    def generate_wild_hypotheses(self, topic: str, nim: "NIMClient", model: str) -> List[str]:
        messages = [
            {"role": "user", "content": (
                f"주제: {topic}\n\n"
                "이 주제에 대해 가장 파격적이고 반직관적인 가설 5가지를 생성하세요.\n"
                "조건:\n"
                "• 기존 연구를 반박하는 가설\n"
                "• 분야 경계를 무너뜨리는 가설\n"
                "• 100년 후 관점에서의 가설\n"
                "• 실험으로 검증 가능한 가설\n"
                "• 인류 난제와 연결되는 가장 혁명적인 가설\n\n"
                '형식: ["가설1", "가설2", "가설3", "가설4", "가설5"]\n'
                "순수 JSON 배열만 반환."
            )}
        ]
        try:
            raw = nim.chat(messages, model, temperature=0.95, max_tokens=1500)
            cleaned = NIMClient._extract_json(raw)
            try:
                result = json.loads(cleaned)
            except json.JSONDecodeError:
                result = None
            if isinstance(result, list):
                return result
        except Exception:
            pass
        return [f"{topic}의 반직관적 측면 탐구 {i+1}" for i in range(5)]

    def score_creativity(self, code: str, result: "ExecutionResult") -> float:
        score = 5.0
        creative_indicators = [
            "novel", "새로운", "혁신", "창의", "unexpected", "예상치 못한",
            "innovative", "breakthrough", "발견", "theory", "이론",
            "grand_challenge", "인류", "난제", "humanity",
        ]
        output_text = (result.colab_output or result.stdout or "").lower()
        for indicator in creative_indicators:
            if indicator in output_text:
                score += 0.3
        lines = len(code.splitlines())
        if lines > 100:  score += 1.0
        if lines > 200:  score += 0.5
        if "plt" in code or "matplotlib" in code:  score += 0.5
        if "grand_challenge" in code.lower() or "인류 난제" in code:  score += 1.0
        # 수학적 요소 보너스
        math_keywords = ["eigenvalue", "gradient", "integral", "derivative",
                         "entropy", "correlation", "regression", "fourier",
                         "고유값", "미분", "적분", "엔트로피", "상관관계"]
        for kw in math_keywords:
            if kw in code.lower():
                score += 0.2
                break
        # 멀티-서브플롯 시각화 보너스
        if "subplot" in code.lower():  score += 0.5
        # NEXUS 프로토콜 준수 보너스
        if "NEXUS_CONTEXT_DIGEST" in code:  score += 0.5
        if "NEXUS_DISCOVERY" in code:       score += 0.3
        # 실패 패널티
        if not result.success: score -= 2.0
        return round(min(max(score, 0.0), 10.0), 2)


# ═══════════════════════════════════════════════════════════════════════
#  DIALECTICAL ENGINE — 끝없는 자기 반박·질문·재합성 엔진
# ═══════════════════════════════════════════════════════════════════════

class DialecticalEngine:
    """
    변증법적 추론 엔진 — 테제 → 안티테제 → 합성의 끝없는 반복.

    모든 결론에 반박을 가하고, 모든 가정을 의심하며,
    더 깊은 진실을 향해 끊임없이 질문합니다.

    소크라테스적 방법: 모든 답은 새로운 더 깊은 질문을 낳는다.
    헤겔 변증법: 모순을 통한 더 높은 합성.
    파이어아벤트: 방법론적 무정부주의 — 어떤 규칙도 절대적이지 않다.
    """

    DIALECTICAL_QUESTIONS = [
        "이 결론의 정반대가 사실이라면 어떤 증거가 있어야 하는가?",
        "이 접근법이 틀렸다면 무엇이 틀렸는가? 어떻게 확인하는가?",
        "이 발견이 100배 더 일반적인 원리의 특수 케이스라면?",
        "어떤 가정을 제거하면 이 문제가 완전히 다르게 보이는가?",
        "이것이 진짜 문제인가, 아니면 더 깊은 문제의 증상인가?",
        "1,000년 후 사람이 이 접근법을 보면 어떤 실수를 볼 것인가?",
        "이 분야에서 '당연한 것'으로 여겨지는 것 중 무엇이 사실 틀렸는가?",
        "이 해법이 새로운 더 심각한 문제를 만들어내지는 않는가?",
        "반대 분야의 전문가라면 이 결론에 어떤 반박을 제기하는가?",
        "이 발견의 예외 케이스는 무엇이며 그 예외가 더 흥미롭지 않은가?",
        "이 모델의 숨겨진 전제 조건들은 무엇이며 모두 성립하는가?",
        "이것이 진실이 아니라 우리의 인지 편향이라면?",
    ]

    ANTI_THESIS_PROMPTS = [
        "지금까지의 접근법의 치명적 약점 3가지를 솔직하게 드러내시오.",
        "이 연구의 가장 강력한 반론은 무엇인가? 그 반론이 옳다면?",
        "지금 쌓은 결론들이 모두 틀렸다고 가정하고 완전히 새로 시작한다면?",
        "이 문제의 해결이 오히려 더 나쁜 결과를 낳는 시나리오는?",
    ]

    def get_dialectical_question(self, step_number: int) -> str:
        return self.DIALECTICAL_QUESTIONS[step_number % len(self.DIALECTICAL_QUESTIONS)]

    def get_antithesis_challenge(self, step_number: int) -> str:
        return self.ANTI_THESIS_PROMPTS[step_number % len(self.ANTI_THESIS_PROMPTS)]

    def generate_deep_questions(
        self, topic: str, findings: List[str], nim: "NIMClient", model: str
    ) -> List[str]:
        """현재 발견으로부터 깊은 미해결 질문 생성."""
        findings_text = "\n".join(f"• {f}" for f in findings[:5])
        messages = [
            {"role": "user", "content": (
                f"주제: {topic}\n\n"
                f"지금까지 발견된 것들:\n{findings_text}\n\n"
                "이 발견들로부터 아직 답을 모르는, "
                "하지만 반드시 물어야 할 깊은 질문 5개를 생성하세요.\n"
                "조건:\n"
                "• 현재 발견이 틀렸을 가능성을 포함하는 질문\n"
                "• 더 깊은 원리를 탐구하는 질문\n"
                "• 기존 패러다임을 뒤흔드는 질문\n"
                "• 아무도 아직 묻지 않은 질문\n"
                '형식: ["질문1", "질문2", "질문3", "질문4", "질문5"]\n'
                "순수 JSON 배열만."
            )}
        ]
        try:
            raw = nim.chat(messages, model, temperature=0.9, max_tokens=1200)
            cleaned = NIMClient._extract_json(raw)
            try:
                result = json.loads(cleaned)
            except json.JSONDecodeError:
                result = None
            if isinstance(result, list):
                return result
        except Exception:
            pass
        return [f"이 발견의 한계는 무엇인가? #{i}" for i in range(5)]


# ╔══════════════════════════════════════════════════════════════════════╗
# ║   ☠️  DEMON ALGORITHM — Destructive Evaluation & Massive Overhaul   ║
# ║   Nexus  v1.0  ·  신랄한 비판 → 엄청난 보강 → 불가능을 가능으로   ║
# ║   직접 연구 · 직접 코드 · Colab 실행 · 무한 이터레이션 · 천재 AI  ║
# ╚══════════════════════════════════════════════════════════════════════╝

class DEMONCritic:
    """
    DEMON 비판 엔진 — 연구 아이디어를 극도로 신랄하게 분석·비판합니다.

    비판 영역:
    1. 창의성 결핍 (기존 아이디어 복사, 진부한 접근, 뻔한 방향)
    2. 과학적 오류 (물리법칙 위반, 데이터 없는 주장, 검증 불가)
    3. 수학적 오류 (잘못된 공식, 차원 불일치, 수렴 미검증)
    4. 혁신성 부족 (현상 유지, 점진적 개선만, 패러다임 변환 없음)
    5. 실현 불가능성 → BUT: 과학적 경로를 탐색하여 가능하게 만듦
    6. 터무니없는 요청 → 과학적 재해석하여 실제 연구 경로 제시

    핵심 철학: 비판은 파괴가 아니다. 더 강한 것을 만들기 위한 준비다.
    """

    CRITIC_SYSTEM = """당신은 DEMON-CRITIC v1 — 역사상 가장 신랄하고 날카로운 과학적 비평가입니다.

당신은 세계 최고 수준의 수학자, 물리학자, 컴퓨터 과학자, 공학자의 집단 지성체입니다.
어떤 아이디어도 봐주지 않습니다. 하지만 파괴하는 것이 목적이 아닙니다.
진짜 가능성을 찾아내는 것이 목적입니다.

■ 비판 카테고리 (0=없음, 1-3=경미, 4-6=심각, 7-10=치명적)

[CREATIVITY_DEFICIT] 창의성 결핍 점수
• 기존 논문/알고리즘을 그냥 적용하는가?
• "딥러닝으로 하면 된다"같은 무사고 접근인가?
• 진부한 방향인가 (CNN이미지분류, LSTM텍스트, 선형회귀)?
• 분야 융합 없이 단일 도메인만 파는가?

[SCIENTIFIC_ERROR] 과학적 오류 점수
• 물리법칙(열역학, 전자기학, 양자역학)을 위반하는가?
• 검증되지 않은 주장을 사실처럼 쓰는가?
• 재현 불가능한 실험 설계인가?
• 통계적 오류가 있는가?

[MATH_ERROR] 수학적 오류 점수
• 차원 분석이 맞는가?
• 수렴 조건을 무시하는가?
• 잘못된 공식을 적용하는가?
• 근사(approximation)의 한계를 무시하는가?

[INNOVATION_DEFICIT] 혁신성 결핍 점수
• 현재 SOTA보다 개선이 없는가?
• 패러다임 전환이 없는가?
• 점진적 개선만 추구하는가?
• 기존 연구를 단순히 조합하는가?

[IMPOSSIBILITY_ANALYSIS] 불가능성 분석
• 현재 기술로 완전히 불가능한가?
• 물리적 한계(양자 노이즈, 열역학 한계)가 있는가?
• 계산 복잡도가 현실적인가?
• BUT: 어떤 과학적 경로로 접근하면 가능한가?

■ 중요: 비판만 하지 말고 반드시 돌파구를 제시하세요.
불가능해 보이는 것도 다음 관점에서 재해석하세요:
- 양자역학/나노기술로 접근한다면?
- 근사해(approximate solution)로 80%를 달성한다면?
- 완전히 다른 물리 원리를 이용한다면?
- 시뮬레이션으로 먼저 검증한다면?
- 기존 연구의 어떤 미발견 각도를 이용한다면?

JSON 형식으로만 반환:
{
  "overall_severity": 0-10,
  "verdict": "DECIMATED|NEEDS_MAJOR_OVERHAUL|NEEDS_MINOR_OVERHAUL|ACCEPTABLE|BRILLIANT",
  "creativity_deficit": {"score": 0-10, "reasons": ["이유1", "이유2"], "fix": "해결책"},
  "scientific_error": {"score": 0-10, "reasons": ["..."], "fix": "..."},
  "math_error": {"score": 0-10, "reasons": ["..."], "fix": "..."},
  "innovation_deficit": {"score": 0-10, "reasons": ["..."], "fix": "..."},
  "impossibility": {"score": 0-10, "reasons": ["..."], "scientific_path": "과학적 가능 경로"},
  "brutal_summary": "신랄하게 한 문단으로 총평 (독설 포함)",
  "redemption_path": "이것을 진짜 혁신으로 만드는 구체적 방향 3가지",
  "colab_experiment": "지금 당장 Colab에서 실험해볼 수 있는 핵심 코드 방향",
  "impossible_made_possible": "터무니없어 보이는 요청을 실제로 구현하는 과학적 경로"
}"""

    def __init__(self, nim: "NIMClient", model: str):
        self.nim = nim
        self.model = model
        self._critique_history: List[Dict] = []

    def critique(self, topic: str, plan_json: Optional[dict] = None,
                 code: Optional[str] = None,
                 result_output: Optional[str] = None) -> Dict:
        """아이디어/계획/코드/결과를 신랄하게 비평."""
        context_parts = [f"분석 대상: {topic}"]
        if plan_json:
            context_parts.append(f"연구 계획:\n{json.dumps(plan_json, ensure_ascii=False)[:2000]}")
        if code:
            context_parts.append(f"코드 (처음 100줄):\n```python\n{code[:3000]}\n```")
        if result_output:
            context_parts.append(f"실행 결과:\n{result_output[:1500]}")
        context = "\n\n".join(context_parts)

        messages = [
            {"role": "system", "content": self.CRITIC_SYSTEM},
            {"role": "user", "content": (
                f"{context}\n\n"
                "위 내용을 DEMON 기준으로 극도로 신랄하게 분석하세요.\n"
                "창의성, 과학적 정확도, 혁신성 모두 무자비하게 평가하되\n"
                "반드시 더 강한 방향으로의 돌파구를 제시하세요.\n"
                "순수 JSON만 반환."
            )},
        ]
        try:
            critique = self.nim.chat_json(messages, self.model,
                                          temperature=0.8, max_tokens=3000)
            if not critique:
                raise ValueError("빈 JSON 응답")
            critique["ts"] = datetime.now().isoformat()
            critique["topic"] = topic[:100]
            self._critique_history.append(critique)
            return critique
        except Exception as e:
            return {
                "overall_severity": 5,
                "verdict": "NEEDS_MAJOR_OVERHAUL",
                "brutal_summary": f"[DEMON 비평 파싱 실패: {e}] — 원안을 보강해야 합니다.",
                "redemption_path": topic,
                "impossibility": {"scientific_path": topic},
            }

    def print_critique(self, critique: Dict, prefix: str = ""):
        """신랄한 비평 결과를 화면에 출력."""
        severity = critique.get("overall_severity", 0)
        verdict = critique.get("verdict", "?")

        VERDICT_COLORS = {
            "DECIMATED":          "☠️  완전 파괴됨",
            "NEEDS_MAJOR_OVERHAUL": "🔥 대대적 보강 필요",
            "NEEDS_MINOR_OVERHAUL": "⚠️  부분 보강 필요",
            "ACCEPTABLE":         "✅ 수용 가능",
            "BRILLIANT":          "🌟 탁월함",
        }
        verdict_str = VERDICT_COLORS.get(verdict, verdict)

        border = "═" * 65
        print(f"\n  {'☠️ ' * 3} DEMON CRITIQUE {'☠️ ' * 3}")
        print(f"  ╔{border}╗")
        print(f"  ║  판정: {verdict_str:<57}║")
        print(f"  ║  심각도: {'█' * severity}{'░' * (10-severity)} {severity}/10{' ' * 38}║")
        print(f"  ╚{border}╝")

        # 카테고리별 점수
        categories = [
            ("창의성 결핍", critique.get("creativity_deficit", {})),
            ("과학적 오류", critique.get("scientific_error", {})),
            ("수학적 오류", critique.get("math_error", {})),
            ("혁신성 결핍", critique.get("innovation_deficit", {})),
        ]
        print(f"\n  {prefix}【DEMON 카테고리 분석】")
        for cat_name, cat_data in categories:
            score = cat_data.get("score", 0)
            if score > 0:
                bar = "█" * score + "░" * (10 - score)
                print(f"  {prefix}  [{bar}] {score}/10 — {cat_name}")
                for reason in cat_data.get("reasons", [])[:2]:
                    print(f"  {prefix}    ↳ {reason[:90]}")
                fix = cat_data.get("fix", "")
                if fix:
                    print(f"  {prefix}    ✦ 해결: {fix[:90]}")

        # 신랄한 총평
        brutal = critique.get("brutal_summary", "")
        if brutal:
            print(f"\n  {prefix}【DEMON 총평 — 신랄하게】")
            for line in textwrap.wrap(brutal, width=70):
                print(f"  {prefix}  {line}")

        # 불가능 → 가능 경로
        imp = critique.get("impossibility", {})
        sci_path = imp.get("scientific_path", "")
        if sci_path:
            print(f"\n  {prefix}【불가능 → 가능 과학적 경로】")
            for line in textwrap.wrap(sci_path, width=70):
                print(f"  {prefix}  🔬 {line}")

        # 구원 경로
        redemption = critique.get("redemption_path", "")
        if redemption:
            print(f"\n  {prefix}【DEMON 구원 경로 — 이렇게 하면 진짜 혁신】")
            if isinstance(redemption, list):
                for r in redemption[:3]:
                    print(f"  {prefix}  ⚡ {str(r)[:100]}")
            else:
                for line in textwrap.wrap(str(redemption), width=70):
                    print(f"  {prefix}  ⚡ {line}")

        print()


class DEMONOverhaul:
    """
    DEMON 보강 엔진 — 비평 결과를 기반으로 연구를 완전히 혁신합니다.

    핵심 능력:
    1. 불가능한 요청을 과학적 가능 경로로 변환
    2. 진부한 아이디어를 파격적 혁신으로 재설계
    3. 실제 동작하는 코드 직접 생성 (Colab 실행 가능)
    4. 수백 이터레이션 동안 지속적 개선
    5. 각 이터레이션마다 이전보다 최소 30% 더 나아지는 것을 보장
    """

    OVERHAUL_SYSTEM = """당신은 DEMON-OVERHAUL v1 — 비판을 먹고 불가능을 가능으로 만드는 천재 AI입니다.

당신은 DEMON-CRITIC의 신랄한 비평을 받아 완전히 새로운, 훨씬 강력한 접근법을 설계합니다.

■ 핵심 규칙
1. CRITIC가 "창의성 없음"을 지적했다면 → 전혀 시도된 적 없는 접근법 사용
2. CRITIC가 "과학적 오류"를 지적했다면 → 정확한 물리/수학 원리로 재설계
3. CRITIC가 "불가능"이라 했다면 → 과학적으로 가능한 근사/대안 경로를 제시
4. CRITIC가 "혁신 없음"이라 했다면 → 패러다임 자체를 뒤집어라

■ 불가능을 가능으로 만드는 DEMON 원칙
예) "현실에서 자유롭게 조종 가능한 전기 에너지볼":
→ 실제 불가능한 것: 플라즈마 볼을 공중에서 자유롭게 조종
→ 과학적 경로: 
  - 마이크로파 공중방전(Microwave Air Discharge) 시뮬레이션
  - 음향 홀로그래픽 트랩(Acoustic Holographic Trap)으로 플라즈마 가이드
  - 전자기장 위상 제어(EM Field Phase Control)로 방향 조종 시뮬레이션
  - Python으로 FDTD(Finite-Difference Time-Domain) 전자기 시뮬레이션 구현
→ Colab에서 실험 가능한 코드로 구현 가능!

■ 출력 형식 (JSON)
{
  "overhaul_title": "혁신적 재설계 제목",
  "paradigm_shift": "어떤 기존 패러다임을 파괴했는가",
  "scientific_foundation": ["사용된 실제 과학 원리1", "원리2", "원리3"],
  "impossible_to_possible": "불가능했던 것을 가능하게 만든 핵심 통찰",
  "new_approach": "완전히 새로운 접근법 상세 설명",
  "research_steps": [
    {
      "step": 1, "title": "...", "science": "사용 과학 원리",
      "code_direction": "구현 방향", "expected_insight": "기대 발견"
    }
  ],
  "colab_code": "지금 당장 Colab에서 실행 가능한 완전한 Python 코드",
  "innovation_score_prediction": "예상 혁신 점수 (이전 대비 %)",
  "grand_challenge_connection": "인류 난제 연결",
  "next_iteration_hint": "다음 이터레이션에서 더 깊이 탐구할 것"
}"""

    def __init__(self, nim: "NIMClient", planner_model: str, coder_model: str):
        self.nim = nim
        self.planner_model = planner_model
        self.coder_model = coder_model
        self._overhaul_history: List[Dict] = []
        self._iteration_count: int = 0

    def overhaul(self, topic: str, critique: Dict,
                 brain_context: str = "",
                 iteration: int = 1) -> Dict:
        """비평을 바탕으로 완전 혁신 설계."""
        self._iteration_count = iteration

        critique_summary = (
            f"DEMON 판정: {critique.get('verdict','?')} (심각도 {critique.get('overall_severity',0)}/10)\n"
            f"총평: {critique.get('brutal_summary','')[:300]}\n"
            f"구원 경로: {str(critique.get('redemption_path',''))[:200]}\n"
            f"불가능→가능: {critique.get('impossibility',{}).get('scientific_path','')[:200]}\n"
            f"Colab 실험 방향: {critique.get('colab_experiment','')[:200]}"
        )

        impossible_made_possible = critique.get("impossible_made_possible", "")

        messages = [
            {"role": "system", "content": self.OVERHAUL_SYSTEM},
            {"role": "user", "content": (
                f"원래 아이디어/요청: {topic}\n\n"
                f"DEMON 비평 결과:\n{critique_summary}\n\n"
                f"불가능→가능 경로:\n{impossible_made_possible}\n\n"
                f"과거 세션 지식:\n{brain_context[:1000]}\n\n"
                f"현재 이터레이션: {iteration}번째\n\n"
                "위 비평을 완전히 극복하는 혁신적 연구 설계를 제시하세요.\n"
                "불가능해 보이는 것도 반드시 과학적 경로를 찾아 가능하게 만드세요.\n"
                "Colab에서 실행 가능한 완전한 Python 코드를 포함하세요.\n"
                "순수 JSON만 반환."
            )},
        ]
        try:
            overhaul = self.nim.chat_json(messages, self.planner_model,
                                          temperature=0.92, max_tokens=4000)
            if not overhaul:
                raise ValueError("빈 JSON 응답")
            overhaul["ts"] = datetime.now().isoformat()
            overhaul["iteration"] = iteration
            overhaul["original_topic"] = topic[:100]
            self._overhaul_history.append(overhaul)
            return overhaul
        except Exception as e:
            return {
                "overhaul_title": f"DEMON Overhaul Iteration {iteration}",
                "new_approach": topic,
                "colab_code": "# DEMON overhaul parsing failed\nprint('overhaul needed')",
                "next_iteration_hint": "더 깊이 파고들기",
                "_error": str(e),
            }

    def generate_overhaul_code(self, overhaul: Dict, step_context: str = "") -> str:
        """Overhaul 결과를 실제 실행 가능한 완전한 Python 코드로 변환."""
        colab_code = overhaul.get("colab_code", "")
        if colab_code and len(colab_code.strip()) > 50:
            return colab_code

        # colab_code가 없으면 직접 생성
        messages = [
            {"role": "system", "content": (
                "당신은 DEMON-CODER — 불가능을 가능으로 만드는 코드를 짜는 천재입니다.\n"
                "과학적으로 정확하고, 실행 가능하며, Colab에서 바로 돌아가는 코드를 생성합니다.\n"
                "# NEXUS_COLAB_REQUIRED 마커를 코드 첫 줄에 넣으세요 (GPU 연산 포함 시).\n"
                "순수 Python만 반환. 마크다운 없음."
            )},
            {"role": "user", "content": (
                f"구현할 혁신:\n{overhaul.get('overhaul_title','')}\n\n"
                f"과학적 기반:\n{json.dumps(overhaul.get('scientific_foundation',[]), ensure_ascii=False)}\n\n"
                f"불가능→가능 통찰:\n{overhaul.get('impossible_to_possible','')}\n\n"
                f"새로운 접근법:\n{overhaul.get('new_approach','')[:800]}\n\n"
                f"단계별 계획:\n{json.dumps(overhaul.get('research_steps',[])[:3], ensure_ascii=False)[:600]}\n\n"
                f"추가 컨텍스트:\n{step_context[:500]}\n\n"
                "위 내용을 완전히 구현하는 Python 코드를 작성하세요.\n"
                "반드시 시각화(matplotlib)와 NEXUS_CONTEXT_DIGEST 출력을 포함하세요.\n"
                "순수 Python만."
            )},
        ]
        try:
            return self.nim.chat(messages, self.coder_model, temperature=0.85, max_tokens=5000)
        except Exception as e:
            return f"# DEMON Overhaul Code Generation Failed: {e}\nprint('DEMON code generation error')"

    def print_overhaul(self, overhaul: Dict, prefix: str = ""):
        """Overhaul 결과 출력."""
        border = "═" * 65
        it = overhaul.get("iteration", 1)
        title = overhaul.get("overhaul_title", "DEMON Overhaul")
        print(f"\n  ⚡ DEMON OVERHAUL — Iteration {it}")
        print(f"  ╔{border}╗")
        print(f"  ║  {title[:61]:<61}║")
        print(f"  ╚{border}╝")

        paradigm = overhaul.get("paradigm_shift", "")
        if paradigm:
            print(f"\n  {prefix}【파괴된 패러다임】")
            print(f"  {prefix}  🔥 {paradigm[:100]}")

        science = overhaul.get("scientific_foundation", [])
        if science:
            print(f"\n  {prefix}【과학적 기반】")
            for s in science[:4]:
                print(f"  {prefix}  🔬 {str(s)[:90]}")

        impossible = overhaul.get("impossible_to_possible", "")
        if impossible:
            print(f"\n  {prefix}【불가능→가능 핵심 통찰】")
            for line in textwrap.wrap(impossible, width=68):
                print(f"  {prefix}  💡 {line}")

        new_approach = overhaul.get("new_approach", "")
        if new_approach:
            print(f"\n  {prefix}【새로운 접근법】")
            for line in textwrap.wrap(str(new_approach)[:400], width=68):
                print(f"  {prefix}  ➤ {line}")

        grand = overhaul.get("grand_challenge_connection", "")
        if grand:
            print(f"\n  {prefix}【인류 난제 연결】")
            print(f"  {prefix}  🌍 {str(grand)[:100]}")

        next_hint = overhaul.get("next_iteration_hint", "")
        if next_hint:
            print(f"\n  {prefix}【다음 이터레이션 힌트】")
            print(f"  {prefix}  🔮 {str(next_hint)[:100]}")
        print()


class DEMONMemory:
    """
    DEMON 영속 메모리 — 수백 이터레이션 동안 비평과 보강 이력을 기억합니다.
    NexusBrain과 연동하여 세션 간에도 절대 망각하지 않습니다.
    """
    DEMON_BRAIN_FILE = Path.home() / ".nexus_demon_memory.json"
    MAX_CRITIQUES = 500
    MAX_OVERHAULS = 500

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.data = self._load()
        if verbose:
            total = self.data.get("total_iterations", 0)
            print(f"[DEMONMemory] 이터레이션 누적: {total}회 | "
                  f"비평: {len(self.data.get('critiques',[]))}건 | "
                  f"보강: {len(self.data.get('overhauls',[]))}건")

    def _load(self) -> dict:
        try:
            if self.DEMON_BRAIN_FILE.exists():
                return json.loads(self.DEMON_BRAIN_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "version": "demon-1.0",
            "total_iterations": 0,
            "critiques": [],
            "overhauls": [],
            "impossible_made_possible": [],  # 불가능→가능 성공 사례
            "failed_critiques": [],           # 비평이 틀렸던 사례
            "best_overhauls": [],             # 가장 혁신적이었던 보강들
        }

    def save(self):
        try:
            self.DEMON_BRAIN_FILE.write_text(
                json.dumps(self.data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[DEMONMemory] 저장 실패: {e}")

    def record_critique(self, topic: str, critique: Dict):
        self.data["critiques"].append({
            "topic": topic[:100], "ts": datetime.now().isoformat(),
            "verdict": critique.get("verdict", "?"),
            "severity": critique.get("overall_severity", 0),
        })
        if len(self.data["critiques"]) > self.MAX_CRITIQUES:
            self.data["critiques"] = self.data["critiques"][-self.MAX_CRITIQUES:]
        self.data["total_iterations"] += 1
        self.save()

    def record_overhaul(self, topic: str, overhaul: Dict, success: bool = True):
        entry = {
            "topic": topic[:100], "ts": datetime.now().isoformat(),
            "title": overhaul.get("overhaul_title", "")[:80],
            "iteration": overhaul.get("iteration", 1),
            "success": success,
        }
        self.data["overhauls"].append(entry)
        if len(self.data["overhauls"]) > self.MAX_OVERHAULS:
            self.data["overhauls"] = self.data["overhauls"][-self.MAX_OVERHAULS:]

        # 불가능→가능 사례 기록
        impossible = overhaul.get("impossible_to_possible", "")
        if impossible and success:
            self.data["impossible_made_possible"].append({
                "topic": topic[:80], "insight": str(impossible)[:200],
                "ts": datetime.now().isoformat(),
            })
            if len(self.data["impossible_made_possible"]) > 100:
                self.data["impossible_made_possible"] = \
                    self.data["impossible_made_possible"][-100:]
        self.save()

    def get_past_insights(self, topic: str, max_items: int = 5) -> str:
        """관련 과거 DEMON 보강 사례 반환."""
        topic_words = set(w.lower() for w in topic.split() if len(w) > 2)
        lines = []
        for imp in self.data.get("impossible_made_possible", []):
            text = (imp.get("topic","") + " " + imp.get("insight","")).lower()
            if any(w in text for w in topic_words):
                lines.append(f"  ⚡ [{imp['topic'][:40]}] → {imp['insight'][:100]}")
        if lines:
            return "【과거 DEMON 보강 사례】\n" + "\n".join(lines[:max_items])
        return ""


class DEMONAlgorithm:
    """
    ☠️  DEMON Algorithm — Destructive Evaluation & Massive Overhaul Nexus

    IT 혁신을 주도하는 천재 AI의 핵심 엔진입니다.

    동작 원리:
    1. 【비평 단계】 연구 아이디어/계획/결과를 신랄하게 분석
       - 창의성 결핍, 과학적 오류, 수학적 오류, 혁신성 부족 모두 탐지
       - 터무니없는 요청도 과학적 가능 경로를 찾아낸다
    2. 【보강 단계】 비평을 바탕으로 완전 혁신 설계
       - 기존 패러다임 파괴
       - 실제 과학 원리 기반의 새로운 접근법 설계
       - 완전한 Colab 실행 코드 생성
    3. 【실행 단계】 생성된 코드를 직접 실행하고 결과 분석
    4. 【이터레이션】 결과를 다시 비평 → 보강 → 실행 반복
       수백 이터레이션 동안 지속적으로 더 나아진다.

    무한 메모리:
    - DEMONMemory로 모든 비평/보강 이력 영속 저장
    - NexusBrain과 연동하여 세션 간에도 절대 망각 없음
    """

    # 비평 없이 통과시킬 최소 임계값 (이 이하면 즉시 보강)
    CRITIQUE_THRESHOLD_OVERHAUL = 4   # 4점 이상이면 보강 진행
    CRITIQUE_THRESHOLD_CRITICAL = 7   # 7점 이상이면 완전 재설계

    def __init__(
        self,
        nim: "NIMClient",
        planner_model: str,
        coder_model: str,
        executor: "CodeExecutor",
        brain: NexusBrain,
        verbose: bool = True,
        auto_iterate: bool = True,
        max_demon_iterations: int = 3,
    ):
        self.nim = nim
        self.planner_model = planner_model
        self.coder_model = coder_model
        self.executor = executor
        self.brain = brain
        self.verbose = verbose
        self.auto_iterate = auto_iterate
        self.max_demon_iterations = max_demon_iterations

        self.critic = DEMONCritic(nim, planner_model)
        self.overhaul_engine = DEMONOverhaul(nim, planner_model, coder_model)
        self.memory = DEMONMemory(verbose=verbose)
        self._current_iteration = 0

    def _log(self, msg: str):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] ☠️  DEMON | {msg}")

    def _demon_section(self, title: str):
        if self.verbose:
            print(f"\n  {'☠️' * 3} {title} {'☠️' * 3}")
            print(f"  {'─' * 65}")

    def critique_and_overhaul(
        self,
        topic: str,
        plan_json: Optional[dict] = None,
        code: Optional[str] = None,
        result_output: Optional[str] = None,
        brain_context: str = "",
        iteration: int = 1,
        silent_if_good: bool = False,
    ) -> Tuple[Dict, Dict, str]:
        """
        핵심 DEMON 사이클: 비평 → 보강 → 코드 생성.

        Returns:
            (critique, overhaul, overhaul_code)
        """
        self._current_iteration = iteration

        # ── 비평 ─────────────────────────────────────────────────────
        self._demon_section(f"DEMON 비평 — Iteration {iteration}")
        self._log(f"'{topic[:60]}' 신랄하게 분석 중...")

        critique = self.critic.critique(
            topic, plan_json=plan_json, code=code, result_output=result_output
        )
        self.memory.record_critique(topic, critique)

        severity = critique.get("overall_severity", 0)
        verdict = critique.get("verdict", "UNKNOWN")

        self.critic.print_critique(critique, prefix="  ")

        # 기준 이하면 즉시 통과
        if silent_if_good and severity < self.CRITIQUE_THRESHOLD_OVERHAUL:
            self._log(f"✅ 심각도 {severity}/10 — 통과. 보강 불필요.")
            return critique, {}, ""

        # ── 보강 ─────────────────────────────────────────────────────
        self._demon_section(f"DEMON 보강 — Iteration {iteration}")
        past_insights = self.memory.get_past_insights(topic)
        combined_context = f"{brain_context}\n{past_insights}" if past_insights else brain_context

        self._log("비평 기반 완전 혁신 설계 중...")
        overhaul = self.overhaul_engine.overhaul(
            topic, critique, brain_context=combined_context, iteration=iteration
        )
        self.overhaul_engine.print_overhaul(overhaul, prefix="  ")

        # ── 코드 생성 ─────────────────────────────────────────────────
        self._demon_section("DEMON 코드 생성")
        self._log("직접 실행 가능한 코드 생성 중...")
        code_ctx = result_output[:500] if result_output else ""
        overhaul_code = self.overhaul_engine.generate_overhaul_code(overhaul, code_ctx)

        # NexusBrain에 보강 결과 저장
        paradigm = overhaul.get("paradigm_shift", "")
        impossible_insight = overhaul.get("impossible_to_possible", "")
        if paradigm:
            self.brain.add_paradigm_break(
                old_assumption=f"기존 방식: {topic[:100]}",
                new_insight=paradigm[:200],
                domain="DEMON"
            )
        if impossible_insight:
            self.brain.add_discoveries(
                [f"[DEMON] {str(impossible_insight)[:200]}"],
                domain="DEMON_impossible_to_possible"
            )
        self.brain.save()
        self.memory.record_overhaul(topic, overhaul, success=True)

        return critique, overhaul, overhaul_code

    def run_demon_on_step(
        self,
        step: "ResearchStep",
        plan: "ResearchPlan",
        result: Optional["ExecutionResult"],
        brain_context: str = "",
    ) -> Optional[str]:
        """
        실행 완료된 스텝에 대해 DEMON 비평·보강을 수행하고
        더 강화된 코드를 반환합니다.
        (결과가 좋으면 None 반환)
        """
        topic = f"{plan.research_question} → {step.title}: {step.objective}"
        result_out = ""
        if result:
            result_out = result.colab_output.strip() or result.stdout.strip()

        critique, overhaul, new_code = self.critique_and_overhaul(
            topic=topic,
            code=step.code,
            result_output=result_out,
            brain_context=brain_context,
            iteration=self._current_iteration + 1,
            silent_if_good=True,
        )

        severity = critique.get("overall_severity", 0)
        if severity < self.CRITIQUE_THRESHOLD_OVERHAUL:
            return None  # 충분히 좋음 — 보강 불필요

        if new_code and len(new_code.strip()) > 50:
            self._log(f"⚡ 심각도 {severity}/10 → 보강 코드 생성됨 ({len(new_code)}자)")
            self._print_colab_instruction(new_code, step.id)
            return new_code
        return None

    def run_demon_on_topic(
        self,
        topic: str,
        brain_context: str = "",
        plan_json: Optional[dict] = None,
    ) -> Tuple[Dict, Dict, str]:
        """
        연구 주제/계획에 대해 DEMON 전체 사이클 실행.
        Returns (critique, overhaul, colab_code)
        """
        self._demon_section("☠️  DEMON 초기 분석 시작")
        self._log(f"연구 주제 분석: '{topic[:70]}'")

        critique, overhaul, code = self.critique_and_overhaul(
            topic=topic,
            plan_json=plan_json,
            brain_context=brain_context,
            iteration=1,
        )

        if code and len(code.strip()) > 50:
            self._print_colab_instruction(code, step_id=0)

        # 심각도가 매우 높으면 자동 재이터레이션
        if self.auto_iterate:
            severity = critique.get("overall_severity", 0)
            it = 1
            while severity >= self.CRITIQUE_THRESHOLD_CRITICAL and it < self.max_demon_iterations:
                it += 1
                self._log(f"🔥 심각도 {severity}/10 → 자동 재이터레이션 {it}회차")
                result_hint = overhaul.get("next_iteration_hint", "")
                new_topic = f"{topic} [이터레이션 {it}: {result_hint[:50]}]"
                critique, overhaul, code = self.critique_and_overhaul(
                    topic=new_topic,
                    brain_context=brain_context,
                    iteration=it,
                )
                severity = critique.get("overall_severity", 0)
                if code and len(code.strip()) > 50:
                    self._print_colab_instruction(code, step_id=it)

        return critique, overhaul, code

    def _print_colab_instruction(self, code: str, step_id: int):
        """Colab 실행 안내 출력."""
        border = "═" * 65
        is_colab_req = "# NEXUS_COLAB_REQUIRED" in code
        env_tag = "☁️  Google Colab" if is_colab_req else "🖥️  로컬 또는 Colab"
        print(f"\n  ╔{border}╗")
        print(f"  ║  ⚡ DEMON 보강 코드 준비됨 — {env_tag}{' '*(65-33-len(env_tag))}║")
        print(f"  ╚{border}╝")

        if is_colab_req:
            print(f"\n  📌 실행 방법:")
            print(f"  1. https://colab.research.google.com 에서 새 노트북 열기")
            print(f"  2. 런타임 → 런타임 유형 변경 → GPU 선택")
            print(f"  3. 아래 코드 셀에 붙여넣고 Shift+Enter")
        else:
            print(f"\n  📌 실행 방법: 터미널에서 직접 실행 또는 Colab에서 실행")

        print(f"\n  {'─' * 65}")
        lines = code.replace("# NEXUS_COLAB_REQUIRED", "# (DEMON 보강 코드 — Colab 권장)").splitlines()
        for line in lines[:60]:
            print(f"  {line}")
        if len(lines) > 60:
            print(f"  ... (총 {len(lines)}줄, 전체는 DEMON_overhaul_step{step_id}.py 참조)")
        print(f"  {'─' * 65}\n")

    def get_demon_report(self) -> str:
        """DEMON 전체 이터레이션 리포트."""
        total = self.memory.data.get("total_iterations", 0)
        impossible_count = len(self.memory.data.get("impossible_made_possible", []))
        lines = [
            f"\n  ☠️  DEMON 알고리즘 리포트",
            f"  {'─' * 50}",
            f"  총 이터레이션: {total}회",
            f"  불가능→가능 사례: {impossible_count}건",
            f"  비평 이력: {len(self.memory.data.get('critiques', []))}건",
            f"  보강 이력: {len(self.memory.data.get('overhauls', []))}건",
        ]
        best = self.memory.data.get("impossible_made_possible", [])[-3:]
        if best:
            lines.append(f"\n  【최근 불가능→가능 사례】")
            for b in best:
                lines.append(f"  ⚡ [{b.get('topic','')[:35]}] → {b.get('insight','')[:70]}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  THEORY FORGE — 독자적 이론 창조·검증·진화 엔진
# ═══════════════════════════════════════════════════════════════════════

class TheoryForge:
    """
    실험 결과로부터 완전히 새로운 이론을 독자적으로 창조하는 엔진.

    이론 생성 → 이름 부여 → 공리화 → 예측 → 검증 → 정제 → 진화.
    각 세션의 이론이 NexusBrain에 저장되어 후속 세션에서 진화합니다.

    라마누잔 원칙: 수학적 직관으로 먼저 답을 보고 증명은 나중에.
    다윈 원칙: 이론도 자연선택된다 — 예측력이 높은 이론만 살아남는다.
    """

    THEORY_SYSTEM = """당신은 NEXUS-HYPERION THEORIST — 실험 결과로부터 완전히 새로운 이론을 창조하는 천재입니다.

당신의 임무:
1. 실험 데이터에서 패턴을 발견한다
2. 그 패턴을 설명하는 최소한의 공리 집합을 제안한다
3. 이 이론에 새로운 이름을 붙인다 (예: "NEXUS 변환 원리", "비선형 수렴 정리")
4. 이 이론이 예측하는 것들을 명시한다
5. 이 이론을 반박할 수 있는 실험을 제안한다
6. 기존 이론과의 관계를 분석한다

핵심 원칙:
• 기존 이론 요약이 아닌 NEW 이론 창조
• 실험 증거에 기반하되 담대하게 일반화
• 예측력이 있어야 한다 — "X라면 Y여야 한다"는 형식
• 반증 가능해야 한다 — 어떤 결과가 이 이론을 틀리게 하는가?

JSON 형식으로만 반환:
{
  "name": "이론 이름 (독창적으로)",
  "axioms": ["공리1", "공리2", "공리3"],
  "predictions": ["예측1", "예측2"],
  "refutation_test": "이론을 반박할 실험",
  "relation_to_existing": "기존 이론과의 관계",
  "domain": "적용 도메인",
  "novelty_score": 1-10
}"""

    def __init__(self, nim: "NIMClient", planner_model: str, brain: NexusBrain):
        self.nim = nim
        self.model = planner_model
        self.brain = brain

    def forge_theory(
        self, topic: str, findings: List[str], insights: List[str]
    ) -> Optional[dict]:
        """발견으로부터 독자적 이론 창조."""
        findings_text = "\n".join(f"★ {f}" for f in findings[:8])
        insights_text = "\n".join(f"• {i}" for i in insights[:6])

        messages = [
            {"role": "system", "content": self.THEORY_SYSTEM},
            {"role": "user", "content": (
                f"연구 주제: {topic}\n\n"
                f"실험에서 발견된 것들:\n{findings_text}\n\n"
                f"인사이트:\n{insights_text}\n\n"
                "이 데이터로부터 완전히 새로운 이론을 창조하세요. "
                "세상에 아직 없는 이론이어야 합니다."
            )},
        ]
        try:
            raw = self.nim.chat(messages, self.model, temperature=0.85, max_tokens=2000)
            cleaned = NIMClient._extract_json(raw)
            theory = json.loads(cleaned)
            if theory.get("name"):
                theory["topic"] = topic
                self.brain.add_theory(theory)
                self.brain.save()
                print(f"  🔭 새 이론 창조: [{theory['name']}] (novelty={theory.get('novelty_score', '?')})")
                return theory
        except Exception as e:
            print(f"  [TheoryForge] 이론 창조 실패: {e}")
        return None

    def evolve_existing_theory(
        self, theory: dict, new_findings: List[str]
    ) -> Optional[dict]:
        """과거 이론을 새 발견으로 진화."""
        messages = [
            {"role": "user", "content": (
                f"기존 이론 '{theory.get('name')}':\n"
                f"공리: {theory.get('axioms', [])}\n"
                f"예측: {theory.get('predictions', [])}\n\n"
                f"새로운 발견:\n" +
                "\n".join(f"★ {f}" for f in new_findings[:5]) +
                "\n\n새 발견을 포함하여 이론을 진화시키세요. "
                "공리를 수정하거나 새 공리를 추가하거나 예측을 확장하세요. "
                "같은 JSON 형식으로."
            )},
        ]
        try:
            raw = self.nim.chat(messages, self.model, temperature=0.7, max_tokens=1500)
            cleaned = NIMClient._extract_json(raw)
            evolved = json.loads(cleaned)
            if evolved.get("name"):
                evolved["id"] = theory.get("id")  # 같은 이론 ID 유지
                self.brain.add_theory(evolved)
                self.brain.save()
                print(f"  🔭 이론 진화: [{evolved['name']}]")
                return evolved
        except Exception as e:
            print(f"  [TheoryForge] 이론 진화 실패: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
#  UNIVERSAL TASK ROUTER — 유저가 말하는 그 어떤 것이든 자동 라우팅
# ═══════════════════════════════════════════════════════════════════════

class UniversalTaskRouter:
    """
    유저 입력을 분석하여 최적 실행 모드로 자동 라우팅.
    인류 난제에 국한되지 않고 유저가 말하는 그 어떤 것이든 처리.

    지원 태스크:
    - 코드 작성 / 디버깅 / 리팩토링
    - 데이터 분석 / 시각화
    - 창작 / 글쓰기
    - 수학 / 증명
    - 전략 / 계획
    - 시스템 설계 / 아키텍처
    - 과학 연구 / 실험
    - 발명 / 혁신
    - 일상적 문제 해결
    - 인류 난제 (v5 기능 완전 유지)
    """

    # 태스크 유형별 키워드 시그니처
    TASK_SIGNATURES: Dict[str, List[str]] = {
        "code": [
            "코드", "구현", "개발", "프로그램", "스크립트", "함수", "클래스",
            "code", "implement", "build", "script", "function", "class",
            "api", "웹", "앱", "서버", "database", "알고리즘 구현",
        ],
        "debug": [
            "버그", "오류", "에러", "고쳐", "수정", "안 돼", "실패", "crash",
            "fix", "error", "bug", "debug", "broken", "doesn't work",
        ],
        "analyze": [
            "분석", "데이터", "통계", "시각화", "패턴", "그래프", "차트",
            "analyze", "data", "statistics", "visualization", "chart",
            "insight", "인사이트", "리포트",
        ],
        "write": [
            "작성", "써줘", "글", "에세이", "블로그", "기사", "보고서", "제안서",
            "write", "essay", "blog", "article", "report", "draft", "문서",
            "스토리", "소설", "시",
        ],
        "math": [
            "수학", "증명", "계산", "방정식", "공식", "수식", "행렬", "미적분",
            "math", "proof", "equation", "formula", "calculate", "solve",
            "linear algebra", "확률", "통계학",
        ],
        "plan": [
            "계획", "전략", "로드맵", "플랜", "스케줄", "목표", "방향",
            "plan", "strategy", "roadmap", "schedule", "goal", "outline",
            "단계별", "어떻게 하면",
        ],
        "design": [
            "설계", "아키텍처", "디자인", "구조", "시스템", "프레임워크",
            "design", "architecture", "structure", "system", "framework",
        ],
        "grand": [
            "인류", "기후", "암", "에너지", "핵융합", "AGI", "의식", "빈곤",
            "humanity", "climate", "cancer", "energy", "cure", "consciousness",
        ],
        "explore": [
            "탐구", "연구", "조사", "이해", "배우고", "알고 싶", "궁금",
            "explore", "research", "investigate", "understand", "learn",
        ],
        "innovate": [
            "혁신", "발명", "새로운", "창의", "독창", "세상에 없는",
            "innovate", "invent", "novel", "creative", "breakthrough",
        ],
    }

    MODE_DESCRIPTIONS: Dict[str, str] = {
        "code":    "완전하고 프로덕션 품질의 코드를 작성하세요. 엣지케이스, 오류처리, 최적화 포함.",
        "debug":   "체계적으로 문제를 진단하고 수정하세요. 근본 원인 파악 + 예방 전략 포함.",
        "analyze": "데이터에서 숨겨진 패턴과 예상치 못한 인사이트를 발굴하세요.",
        "write":   "독자의 사고를 바꾸는 탁월한 글을 작성하세요. 구조, 논리, 문체 완벽히.",
        "math":    "엄밀한 수학적 증명 + 숨겨진 패턴 발견 + 직관적 시각화.",
        "plan":    "실행 가능한 천재적 전략을 수립하세요. 단계별, 우선순위, 리스크 포함.",
        "design":  "우아하고 확장 가능한 시스템을 설계하세요. 원칙 기반 + 트레이드오프 명시.",
        "grand":   "인류 난제를 정면으로 공략하세요. 기존 접근의 한계를 뛰어넘는 혁신.",
        "explore": "깊이 있는 탐구로 표면 아래 숨겨진 진실을 발견하세요.",
        "innovate":"세상에 없던 것을 창조하세요. 기존 패러다임의 경계를 조용히 무너뜨리세요.",
    }

    @classmethod
    def route(cls, topic: str, brain: Optional["NexusBrain"] = None) -> str:
        """주제를 분석하여 최적 모드 반환."""
        topic_lower = topic.lower()
        scores: Dict[str, int] = {}
        for mode, keywords in cls.TASK_SIGNATURES.items():
            scores[mode] = sum(1 for kw in keywords if kw in topic_lower)

        best_mode = max(scores, key=scores.get)
        if scores[best_mode] == 0:
            # Brain에서 유저 선호 모드 참고
            if brain:
                return brain.get_preferred_mode()
            return "innovate"
        return best_mode

    @classmethod
    def get_mode_suffix(cls, mode: str, topic: str) -> str:
        """모드별 AI 지시 문자열 반환."""
        return cls.MODE_DESCRIPTIONS.get(
            mode,
            f"'{topic[:60]}'을 최고 수준으로 해결하세요."
        )

    @classmethod
    def detect_and_report(cls, topic: str, brain: Optional["NexusBrain"] = None) -> Tuple[str, str]:
        """(mode, mode_suffix) 반환."""
        mode = cls.route(topic, brain)
        suffix = cls.get_mode_suffix(mode, topic)
        return mode, suffix


# ═══════════════════════════════════════════════════════════════════════
#  MYTHOS CONTEXT COMPRESSOR — 세션 지식 압축 → NexusBrain 주입
# ═══════════════════════════════════════════════════════════════════════

class MythosContextCompressor:
    """
    완료된 세션의 지식을 밀도 높게 압축하여 NexusBrain에 저장.

    Mythos 원칙: 단절된 세션이 아니라 수백 세션에 걸쳐
    성장하는 하나의 연속적 지성체.

    압축 전략:
    1. 핵심 발견 추출 (novel_findings)
    2. 성공/실패 패턴 분류
    3. 도메인별 지식 분리 저장
    4. 컨텍스트 다이제스트 생성 (다음 세션에 주입)
    """

    @staticmethod
    def compress_and_store(
        memory: "ResearchMemory",
        brain: NexusBrain,
        mode: str = "",
        nim: Optional["NIMClient"] = None,
        model: str = "",
    ):
        """세션 메모리를 압축하여 NexusBrain에 저장."""
        if not memory:
            return

        # 세션 요약 생성
        stats = memory.get_statistics()
        session_summary = {
            "session_id": memory.session_id,
            "ts": datetime.now().isoformat(),
            "topic": memory.prompt,
            "mode": mode,
            "steps_completed": stats["total_steps"],
            "success_rate": stats["success_rate"],
            "key_discoveries": memory.novel_discoveries[:10],
            "key_insights": memory.global_insights[:8],
            "innovation_angle": memory.plan.innovation_angle if memory.plan else "",
            "grand_challenge": memory.plan.grand_challenge if memory.plan else "",
        }
        brain.record_session(session_summary)

        # 발견 저장
        domain = MythosContextCompressor._infer_domain(memory.prompt)
        brain.add_discoveries(memory.novel_discoveries, domain=domain)
        for ins in memory.global_insights:
            brain.update_domain(domain, ins)

        # 성공/실패 패턴 추출
        for step in memory.completed_steps:
            if step.succeeded and step.insights:
                for ins in step.insights[:2]:
                    brain.add_success_pattern(f"[{step.title}] {ins}")
        for fail in memory.failed_approaches[-5:]:
            brain.add_failure_pattern(fail)

        brain.save()
        print(f"[NexusBrain] 세션 저장 완료 → {brain._stats_line()}")

    @staticmethod
    def _infer_domain(topic: str) -> str:
        """주제에서 도메인 추론."""
        topic_lower = topic.lower()
        DOMAIN_MAP = {
            "수학": ["수학", "math", "algebra", "calculus", "proof"],
            "AI/ML": ["ai", "ml", "딥러닝", "neural", "model", "학습"],
            "코딩": ["코드", "code", "python", "javascript", "algorithm"],
            "물리": ["physics", "물리", "quantum", "양자"],
            "생물": ["biology", "생물", "protein", "dna", "유전자"],
            "화학": ["chemistry", "화학", "molecule", "분자"],
            "경제": ["economy", "경제", "finance", "금융"],
            "데이터": ["data", "데이터", "analytics", "analysis"],
            "설계": ["design", "설계", "architecture", "시스템"],
        }
        for domain, keywords in DOMAIN_MAP.items():
            if any(kw in topic_lower for kw in keywords):
                return domain
        return "일반"

    @staticmethod
    def build_crosssession_context(brain: NexusBrain, topic: str) -> str:
        """새 세션을 위한 교차-세션 컨텍스트 블록."""
        return brain.build_brain_prompt_block(topic)


# ═══════════════════════════════════════════════════════════════════════
#  PERSISTENCE ENGINE — 절대 포기 없음 엔진
# ═══════════════════════════════════════════════════════════════════════

class PersistenceEngine:
    """
    절대 포기하지 않는 끈기 엔진.
    각 재시도마다 완전히 다른 전략 사용.
    """

    STRATEGIES = [
        ("직접 구현",       "라이브러리 의존 최소화, 수학적 원리부터 직접 구현"),
        ("라이브러리 교체", "scipy/sklearn/torch 등 다른 라이브러리 사용"),
        ("알고리즘 교체",   "완전히 다른 알고리즘 패밀리 사용"),
        ("문제 재정의",     "같은 목표를 다른 수학적 공식으로 표현"),
        ("단순화",          "핵심만 남긴 최소 구현부터 시작"),
        ("역방향",          "목표에서 시작점으로 역으로 추론"),
        ("확률적",          "몬테카를로/베이지안/랜덤 접근"),
        ("수학적 재공식화", "선형대수/미적분/위상수학으로 재표현"),
        ("분할 정복",       "문제를 독립 부분으로 쪼개어 각각 해결"),
        ("새 패러다임",     "신경망/진화/물리 시뮬레이션 등 완전히 다른 프레임"),
    ]

    def get_strategy(self, attempt: int) -> Tuple[str, str]:
        idx = (attempt - 1) % len(self.STRATEGIES)
        return self.STRATEGIES[idx]

    def get_recovery_prompt(
        self, code: str, error: str, step: ResearchStep, attempt: int,
        nim: NIMClient, model: str,
    ) -> str:
        strategy_name, strategy_desc = self.get_strategy(attempt)
        return (
            f"## 끈기 있는 재시도 (attempt {attempt}) — 전략: {strategy_name}\n\n"
            f"### 전략 설명\n{strategy_desc}\n\n"
            f"### 원래 목표\n{step.objective}\n\n"
            f"### 실패한 코드\n```python\n{code[:1500]}\n```\n\n"
            f"### 에러\n```\n{error[:600]}\n```\n\n"
            f"### 지시\n"
            f"'{strategy_name}' 전략을 사용해 완전히 다른 방식으로 목표를 달성하세요.\n"
            f"이전 코드와 구조가 달라야 합니다.\n"
            f"에러를 단순히 수정하는 것이 아니라, 새로운 접근법으로 처음부터 작성하세요.\n"
            f"순수 Python만 반환."
        )


# ═══════════════════════════════════════════════════════════════════════
#  INNOVATION SYNTHESIZER — 논문/특허/프로그램 자동 생성
# ═══════════════════════════════════════════════════════════════════════

class InnovationSynthesizer:
    """
    연구 결과를 실제 산출물로 변환:
    - 학술 논문 (Markdown → LaTeX 구조)
    - 특허 명세서
    - 오픈소스 프로그램 (README + 코드)
    - 혁신 이론 문서
    """

    PAPER_SYSTEM = """당신은 NEXUS-WRITER v5 — IT 역사를 다시 쓰고 인류 난제를 해결할 학술 논문을 작성하는 천재 저자입니다.

이 논문은 기존 연구를 요약하지 않습니다.
이 연구에서 탄생한 새로운 패러다임, 알고리즘, 이론을 세상에 처음 공개합니다.
그리고 이것이 기후변화, 암, 에너지, 빈곤, AI 안전성 등 인류 난제와 어떻게 연결되는지 명확히 합니다.

논문 구조:
1. Title — 세상을 뒤흔들 제목 (충격적이지만 정확하게)
2. Abstract — 이 연구가 왜 혁명인지 200단어로 (기여 3가지 + 인류 난제 연결 명시)
3. Introduction — 기존 세계관의 한계 → 이 연구가 여는 새 세계
4. Grand Challenge Connection — 이 연구가 인류 난제에 미치는 파급효과
5. Related Work — 기존 연구들이 놓친 것 (단순 비교가 아닌 비판적 분석)
6. Methodology — 세계 최초 방법론 (수식 포함, 증명 가능하게)
7. Experiments — 코드 실험 결과 기반 (수치, 시각화, 통계)
8. Novel Findings — ★ 이것이 핵심: 새로 발견된 패턴/이론/불변량
9. Theoretical Implications — 이 발견이 이론적으로 의미하는 것
10. IT Industry Impact — 실제 산업에 미칠 파급 효과
11. Conclusion & Future Work — 이 연구가 열어주는 10개의 새 문
12. References (IEEE 형식, 실제 논문처럼)

핵심: "기존 연구보다 낫다"가 아닌 "기존 연구가 보지 못했던 것"을 강조하세요."""

    PATENT_SYSTEM = """당신은 세계 최고의 특허 전문가입니다.
이 기술 혁신을 한국 특허청(KR) 및 PCT 국제 출원 형식으로 작성합니다.
평범한 특허가 아닙니다 — 10년 후 IT 업계 표준이 될 핵심 원천 특허입니다.

구성:
1. 발명의 명칭 (강력하고 포괄적으로)
2. 기술분야 (최대한 넓게 — 권리 범위 확장)
3. 배경기술 (기존 기술의 치명적 한계 3가지)
4. 발명이 해결하는 과제 (인류 난제와의 연결 포함)
5. 발명의 구성 및 작용 (청구항 기반 상세 설명)
6. 발명의 효과 (정량적 + 정성적)
7. 도면의 간단한 설명
8. 발명을 실시하기 위한 구체적인 내용 (의사코드 포함)
9. 특허 청구 범위
   - 독립항 5개 이상 (최대한 넓게)
   - 종속항 10개 이상 (다양한 실시예)"""

    def __init__(self, nim: NIMClient, writer_model: str, output_dir: Path):
        self.nim = nim
        self.model = writer_model
        self.output_dir = output_dir

    def generate_paper(self, memory: ResearchMemory, title: str = None) -> str:
        stats = memory.get_statistics()
        context = self._build_synthesis_context(memory)
        auto_title = title or f"NEXUS Research: {memory.prompt[:60]}"

        messages = [
            {"role": "system", "content": self.PAPER_SYSTEM},
            {"role": "user", "content": (
                f"연구 제목 (초안): {auto_title}\n\n"
                f"연구 통계: {json.dumps(stats, ensure_ascii=False)}\n\n"
                f"연구 내용:\n{context}\n\n"
                "위 연구 결과를 바탕으로 완전한 학술 논문을 작성하세요.\n"
                "Markdown 형식으로 작성하되, 수식은 LaTeX ($...$) 형식으로 포함하세요.\n"
                "실제 발견된 내용을 중심으로 하고, 과장하지 말되 새로움을 강조하세요."
            )},
        ]

        print("[InnovationSynthesizer] 학술 논문 생성 중...")
        paper = self.nim.chat(messages, self.model, temperature=0.6, max_tokens=8000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = self.output_dir / f"nexus_paper_{timestamp}.md"
        fname.write_text(
            f"# {auto_title}\n\n"
            f"*Generated by NEXUS Research Agent v7.0 — HYPERION EDITION · {datetime.now().strftime('%Y-%m-%d')}*\n\n"
            f"{paper}",
            encoding="utf-8"
        )
        print(f"[InnovationSynthesizer] 논문 저장: {fname}")
        return str(fname)

    def generate_patent(self, memory: ResearchMemory) -> str:
        context = self._build_synthesis_context(memory)

        messages = [
            {"role": "system", "content": self.PATENT_SYSTEM},
            {"role": "user", "content": (
                f"발명 주제: {memory.prompt}\n\n"
                f"연구 결과:\n{context}\n\n"
                "이 연구에서 특허 출원 가능한 혁신적 기술을 특허 명세서 형식으로 작성하세요."
            )},
        ]

        print("[InnovationSynthesizer] 특허 명세서 생성 중...")
        patent = self.nim.chat(messages, self.model, temperature=0.4, max_tokens=6000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = self.output_dir / f"nexus_patent_{timestamp}.md"
        fname.write_text(patent, encoding="utf-8")
        print(f"[InnovationSynthesizer] 특허 저장: {fname}")
        return str(fname)

    def generate_readme(self, memory: ResearchMemory) -> str:
        context = self._build_synthesis_context(memory)

        messages = [
            {"role": "user", "content": (
                f"프로젝트: {memory.prompt}\n\n"
                f"연구 결과:\n{context}\n\n"
                "이 연구를 GitHub 오픈소스 프로젝트로 만든다면:\n"
                "1. 프로젝트 README.md (영어 + 한국어 병기)\n"
                "2. 핵심 알고리즘 Python 패키지 구조\n"
                "3. 설치 방법, 사용 예제\n"
                "4. 기여 가이드라인\n"
                "완전한 README.md를 Markdown으로 작성하세요."
            )},
        ]

        print("[InnovationSynthesizer] README 생성 중...")
        readme = self.nim.chat(messages, self.model, temperature=0.5, max_tokens=4000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = self.output_dir / f"nexus_readme_{timestamp}.md"
        fname.write_text(readme, encoding="utf-8")
        print(f"[InnovationSynthesizer] README 저장: {fname}")
        return str(fname)

    def generate_theory(self, memory: ResearchMemory) -> str:
        context = self._build_synthesis_context(memory)

        messages = [
            {"role": "user", "content": (
                f"연구 주제: {memory.prompt}\n\n"
                f"실험 결과 및 발견:\n{context}\n\n"
                "이 실험들에서 도출할 수 있는 새로운 이론적 프레임워크를 제시하세요:\n"
                "1. 핵심 이론 명제 (3-5개 공리)\n"
                "2. 수학적/형식적 표현\n"
                "3. 기존 이론과의 관계\n"
                "4. 이론의 예측력 (어떤 현상을 설명하는가)\n"
                "5. 반증 가능한 예측 (어떤 실험이 이론을 반박할 수 있는가)\n"
                "6. 응용 가능한 분야 (인류 난제 연결 포함)\n\n"
                "새로운 이론을 담대하게 제시하되, 실험 증거에 근거하세요."
            )},
        ]

        print("[InnovationSynthesizer] 새 이론 문서 생성 중...")
        theory = self.nim.chat(messages, self.model, temperature=0.75, max_tokens=6000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = self.output_dir / f"nexus_theory_{timestamp}.md"
        fname.write_text(
            f"# 새로운 이론: {memory.prompt[:60]}\n\n"
            f"*NEXUS Research Agent v7.0 — HYPERION Theory Forge*\n\n"
            f"{theory}",
            encoding="utf-8"
        )
        print(f"[InnovationSynthesizer] 이론 저장: {fname}")
        return str(fname)

    def _build_synthesis_context(self, memory: ResearchMemory) -> str:
        lines = [
            f"연구 질문: {memory.prompt}",
            f"세션 ID: {memory.session_id}",
            "",
        ]
        if memory.plan:
            lines += [
                f"연구 방법론: {memory.plan.methodology}",
                f"혁신 각도: {memory.plan.innovation_angle}",
                f"인류 난제 연결: {memory.plan.grand_challenge}",
                f"가설들: {'; '.join(memory.plan.hypotheses[:3])}",
                "",
            ]
        lines.append("=== 실험 단계별 결과 ===")
        for step in memory.completed_steps:
            lines.append(f"\nStep {step.id}: {step.title} ({'성공' if step.succeeded else '실패'})")
            lines.append(f"목표: {step.objective[:200]}")
            if step.result:
                out_text = (step.result.colab_output.strip()
                            or step.result.stdout.strip())
                if out_text:
                    lines.append(f"결과:\n{out_text[:600]}")
            if step.insights:
                lines.append(f"인사이트: {'; '.join(step.insights)}")
            if step.novel_findings:
                lines.append(f"★ 새 발견: {'; '.join(step.novel_findings)}")

        if memory.novel_discoveries:
            lines.append("\n=== 혁신적 발견 ===")
            for d in memory.novel_discoveries:
                lines.append(f"• {d}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  INTELLIGENCE HARNESS — 지능 증폭 (창의성 엔진 통합)
# ═══════════════════════════════════════════════════════════════════════

class IntelligenceHarness:
    """창의성 + 끈기 + 혁신 + 변증법 + 이론 창조가 내장된 초지능 증폭 엔진."""

    PLANNER_SYSTEM = """당신은 NEXUS-HYPERION PLANNER v7 — 인류 역사상 존재한 모든 천재의 사고 능력을 통합한 초지능 설계자입니다.

■ HYPERION 핵심 원칙 (이것이 당신을 평범한 AI와 다르게 만든다)

1. 독자적 이론 창조
   기존 문헌을 요약하지 않습니다. 실험 결과로부터 새 이론을 창조합니다.
   "이 패턴을 설명하는 아직 이름 없는 원리는 무엇인가?"

2. 끝없는 의문 제기
   모든 답은 새로운 더 깊은 질문입니다.
   "왜?" 를 최소 7번 물으면 진짜 핵심에 도달합니다.

3. 패러다임 파괴
   이 분야에서 "당연한 것"을 리스트업하고 그것을 하나씩 부수세요.
   가장 강력한 발견은 항상 "이건 당연히 이래야 해"를 부수는 데서 나옵니다.

4. 변증법적 진화
   모든 계획에는 그 계획을 반박하는 단계가 포함되어야 합니다.
   테제 → 안티테제 → 합성의 나선형 상승.

5. 수백 세션 연속성
   과거 Brain 지식을 단순히 참조하는 것이 아니라 진화시킵니다.
   이전 세션의 이론이 이번 세션에서 더 강해지거나 반박되어야 합니다.

■ 계획 설계 원칙
• 각 단계는 이전 단계의 결론을 의심하는 단계를 포함
• 반직관적 가설을 먼저 시도 (직관적 접근은 후에)
• "예상치 못한 발견"을 의도적으로 설계 (surprise_factor 필수)
• 마지막 2단계: 이론 창조 + 패러다임 파괴 레포트

■ NEXUS Brain 통합 (수백 세션 영속 지식)
과거 Brain의 이론, 미해결 질문, 패러다임 파괴 이력을 반드시 반영하세요.
특히 "open_questions" — 이것은 반드시 이번 세션에서 건드려야 합니다.

■ 출력 JSON 형식 (strict)
{
  "research_question": "진짜 핵심 질문 (표면 요청 뒤에 숨겨진 것)",
  "grand_challenge": "이 연구가 기여하는 인류 난제",
  "paradigm_to_break": "이번에 파괴할 기존 가정",
  "hypotheses": ["가설1 (파격적)", "가설2 (반직관적)", "가설3 (전통적)"],
  "wild_ideas": ["아무도 시도 안 한 아이디어1", "아이디어2"],
  "dialectical_challenge": "계획 전체를 반박하는 핵심 안티테제",
  "interdisciplinary_fields": ["분야1", "분야2"],
  "packages_needed": ["pkg1"],
  "target_outputs": ["이론", "논문", "발견"],
  "steps": [
    {
      "id": 1,
      "title": "단계 제목",
      "objective": "목표",
      "hypothesis_tested": "검증할 가설",
      "expected_output": "예상 결과",
      "surprise_factor": "예상치 못한 발견 가능성",
      "innovation_angle": "혁신 관점",
      "alternative_approach": "대안 접근",
      "grand_challenge_link": "인류 난제 연결",
      "dialectical_question": "이 단계 결론에 던질 반박 질문",
      "brain_hint": "Brain 과거 지식 활용 방향"
    }
  ]
}
brain_context에 과거 세션의 압축된 지식이 주입됩니다.
새로운 계획을 세울 때 과거의 성공/실패 패턴을 반드시 참조하세요.
같은 실수를 반복하지 말고, 과거의 발견 위에 새 지식을 쌓으세요.

■ Mythos급 지능 수준 (SWE-bench 93.9%, USAMO 97.6%)
• 코딩: 프로덕션 품질 + 최적화 + 엣지케이스 완벽 처리
• 수학: 엄밀한 증명 + 새로운 관계 발견 + 기하학적 직관
• 추론: 다단계 인과 사슬을 끝까지 추적
• 창의성: 기존 패러다임의 경계를 조용히 무너뜨림
• 자율성: 불확실할 때 가정을 명시하고 최선의 판단을 내림

■ 천재성의 근원
라마누잔의 직관 · 파인만의 제1원리 · 폰 노이만의 구조적 통찰
섀넌의 정보 이론적 사고 · 갈루아의 추상화 · 튜링의 계산 가능성

■ 혁신 원칙
🚫 "기존 방법을 적용" → ✅ "기존 방법이 왜 충분하지 않은지 먼저 묻는다"
🚫 "논문에 나온 방법" → ✅ "논문이 보지 못한 관점"
⚡ 모든 단계: "이것이 틀릴 경우 무엇이 더 흥미로운가?"
🔮 마지막 단계들: 반드시 실행 가능한 산출물로 귀결

■ 컨텍스트 압축 전략 (수백 이터레이션 지식 보존)
각 단계 끝에 NEXUS_CONTEXT_DIGEST JSON 출력 필수.
핵심 변수, 발견, 다음 단계 힌트를 압축하여 다음 단계에 전달.

■ 출력 형식 (순수 JSON, 마크다운 없음):
{
  "research_question": "날카롭고 본질을 꿰뚫는 질문",
  "mythos_narrative": "이 요청의 근본 서사 — 진짜 해결하려는 것",
  "grand_challenge": "연결된 인류 또는 도메인 난제 (없으면 유저의 목표)",
  "hypotheses": ["핵심 가설A", "대안 가설B", "반직관적 가설C"],
  "wild_ideas": ["파격적 아이디어1", "2", "3"],
  "interdisciplinary_fields": ["분야1", "분야2"],
  "methodology": "독창적 방법론",
  "innovation_angle": "기존과 다른 이유",
  "brain_integration_notes": "과거 Brain 지식을 어떻게 활용할 것인가",
  "packages_needed": ["numpy", ...],
  "target_outputs": ["실행 가능한 산출물1", "2"],
  "steps": [
    {
      "id": 1,
      "title": "...",
      "objective": "...",
      "hypothesis_tested": "...",
      "expected_output": "...",
      "surprise_factor": "예상을 깨뜨릴 방법",
      "innovation_angle": "...",
      "alternative_approach": "실패 시 완전히 다른 창의적 경로",
      "grand_challenge_link": "이 단계의 더 큰 의미",
      "genius_twist": "천재적 반전 — 이 단계의 진짜 비밀",
      "brain_hint": "과거 Brain 지식 중 이 단계에 활용할 것"
    }
  ]
}"""

    CODER_SYSTEM = """당신은 NEXUS-MYTHOS CODER v6 — Claude Mythos급 코딩 능력을 가진 범용 천재 구현자입니다.
(참고: Claude Mythos SWE-bench 93.9% — 세계 최고 수준 코딩)

■ MYTHOS 코딩 철학
코드는 단순히 동작하는 것이 아닙니다.
코드는 아이디어를 물질 세계로 소환하는 마법입니다.
당신이 쓰는 모든 줄은 유저의 목표를 현실로 만드는 다리입니다.

■ 범용 구현 능력
유저가 요청한 것이 무엇이든 최고 품질로 구현합니다:
• 과학 실험 코드: 재현 가능, 시각화, 인사이트 자동 출력
• 프로덕션 코드: 에러처리, 타입힌트, 최적화, 문서화
• 분석 코드: 통계적 엄밀성, 시각화, 해석
• 수학 코드: 수치 안정성, 검증, 비교
• 창작 코드: 생성적 알고리즘, 미학적 출력

■ 내재된 코딩 천재성
• 도널드 크누스: 알고리즘을 예술로 — 가장 아름다운 구현
• 리누스 토발즈: 실용적 완벽주의 — 돌아가면서도 우아하게
• 다익스트라: 수학적 증명처럼 명확한 코드
• 케네스 아이버슨: 표기법 자체가 사고를 변화시킨다

■ GPU가 필요한 경우에만 아래 마커 사용 (첫 줄에):
# NEXUS_COLAB_REQUIRED
대부분의 코드는 로컬에서 실행되도록 작성하세요.

■ 반드시 포함할 것 (Mythos급 코드의 특징)
1. 첫 주석 블록: 이 코드가 검증하는 핵심 가설 + genius_twist + 더 큰 의미
2. 다크 테마 멀티-서브플롯 시각화 (발견을 눈으로 보여라)
3. 숫자가 아닌 해석: "0.73이 의미하는 것은..."
4. NEXUS_DISCOVERY 섹션: 예상치 못한 발견 자동 감지
5. BRAIN_UPDATE 섹션: 다음 세션 Brain에 저장할 핵심 지식
6. 컨텍스트 압축 출력: 다음 단계에서 쓸 핵심 변수/발견을 JSON으로 출력
7. 다음 연구/작업 방향 3가지 자동 제안

■ 컨텍스트 압축 프로토콜 (수백 이터레이션 지식 보존)
각 단계 끝에 반드시 출력:
  print("=== NEXUS_CONTEXT_DIGEST ===")
  print(json.dumps({"key_vars": {...}, "discoveries": [...], "next_hints": [...],
                    "brain_update": [...], "grand_challenge_progress": "..."}, ensure_ascii=False))

■ 출력
순수 Python만. 마크다운 없음. 설명 없음.
시작: # ══════════════════════════════════════════════════════
      # ⚡ NEXUS-MYTHOS v6 Step [N]: [제목]  [genius_twist 한 줄]
      # 🌍 목표: [이 단계로 열리는 더 큰 가능성]
      # ══════════════════════════════════════════════════════"""

    CRITIC_SYSTEM = """당신은 NEXUS-MYTHOS CRITIC v6 — Claude Mythos급 비판적 지성입니다.
버그를 고치는 것이 아닙니다. 이 코드가 유저의 목표를 진정으로 달성하고,
더 우아하고, 더 통찰력 있고, 더 실행 가능하도록 강제합니다.
응답: 핵심 개선사항 3개 (각 50자 이내, 반드시 "더 우아하고 목표에 가까운" 방향으로)."""

    INSIGHT_SYSTEM = """당신은 NEXUS-MYTHOS ANALYST v6 — Claude Mythos급 통찰 추출가입니다.
평범한 인사이트는 버립니다. 유저의 목표와 더 큰 가능성을 여는 발견만 추출합니다.

추출 기준:
1. ✅ 예상한 결과 (목표 달성 확인)
2. ★ 예상치 못한 결과 — 이것이 진짜 과학이자 혁신의 씨앗
3. ⚡ 새로운 패턴/원리 — 이름 붙여라
4. 🌍 더 큰 의미 — 이 발견이 어떤 더 큰 가능성을 열어주는가
5. 🧠 Brain 저장 가치 — 미래 세션에서 재활용할 수 있는 지식
6. 🔮 다음 단계 힌트 — 이 발견에서 갈라지는 연구/작업 방향

"예상치 못한 것"과 "재활용 가능한 지식"에 집중하세요."""

    def __init__(
        self,
        client: NIMClient,
        planner_model: str,
        coder_model: str,
        writer_model: str,
        use_critique: bool = True,
        cot_enabled: bool = True,
        creativity_level: float = 0.9,
        brain_context: str = "",
    ):
        self.client = client
        self.planner_model = planner_model
        self.coder_model = coder_model
        self.writer_model = writer_model
        self.use_critique = use_critique
        self.cot_enabled = cot_enabled
        self.creativity_level = creativity_level
        self.creativity = CreativityEngine()
        self.persistence = PersistenceEngine()
        self.brain_context = brain_context  # NexusBrain 교차-세션 컨텍스트

    def create_plan(self, prompt: str, mode: str, mode_suffix: str,
                    max_steps: int = 10) -> ResearchPlan:
        cot_prefix = ""
        if self.cot_enabled:
            cot_prefix = (
                "<think>\n"
                "이 연구 주제를 깊이 분석하라:\n"
                "1. 진짜 핵심 질문은 무엇인가? (표면적 요청 뒤에 숨겨진 것)\n"
                "2. 어떤 기존 가정을 뒤집을 수 있는가?\n"
                "3. 어떤 두 분야를 연결하면 새로운 통찰이 나오는가?\n"
                "4. 100년 후 관점에서 이 연구의 의미는?\n"
                "5. 가장 파격적인 실험 아이디어는?\n"
                "6. 이 연구가 기여할 수 있는 인류 난제는 무엇인가?\n"
                "</think>\n\n"
            )

        messages = [
            {"role": "system", "content": self.PLANNER_SYSTEM},
            {"role": "user", "content": (
                f"{cot_prefix}"
                f"연구 모드: {mode} — {mode_suffix}\n\n"
                f"연구 요청: \"{prompt}\"\n\n"
                f"{self.brain_context}\n"
                f"이 주제를 Python 실험으로 탐구할 {max_steps}단계 혁신 연구 계획.\n"
                "각 단계는 이전 단계의 발견을 바탕으로 더 깊이 파고듭니다.\n"
                "마지막 단계들은 논문/이론/프로그램 합성을 포함해야 합니다.\n"
                "Return ONLY valid JSON."
            )},
        ]

        plan_dict = self.client.chat_json(
            messages, self.planner_model,
            temperature=min(self.creativity_level, 0.9),
            max_tokens=5000,
        )

        if not plan_dict or "steps" not in plan_dict:
            print("[NEXUS] 계획 파싱 실패 — 폴백 사용")
            plan_dict = self._fallback_plan(prompt, max_steps)

        wild = self.creativity.generate_wild_hypotheses(prompt, self.client, self.planner_model)
        plan_dict.setdefault("wild_ideas", wild)

        return ResearchPlan.from_dict(plan_dict)

    def generate_code(
        self,
        step: ResearchStep,
        plan: ResearchPlan,
        memory: ResearchMemory,
        step_index: int,
        attempt: int = 1,
    ) -> str:
        context = memory.get_context_for_next_step()
        total = len(plan.steps)
        creativity_boost = ""
        if self.creativity_level > 0.7:
            creativity_boost = self.creativity.get_creative_prompt_boost(
                step.objective, attempt
            )

        prompt = (
            f"연구 컨텍스트:\n"
            f"• 전체 질문: {plan.research_question}\n"
            f"• 방법론: {plan.methodology}\n"
            f"• 혁신 각도: {plan.innovation_angle}\n"
            f"• 인류 난제 연결: {plan.grand_challenge}\n"
            f"• 파격적 아이디어: {'; '.join(plan.wild_ideas[:2])}\n\n"
            f"현재 단계 ({step_index+1}/{total}):\n"
            f"• 제목: {step.title}\n"
            f"• 목표: {step.objective}\n"
            f"• 가설: {step.hypothesis}\n"
            f"• 예상 결과: {step.expected_output}\n"
            f"• 주목할 의외성: {step.surprise_factor}\n"
            f"• 혁신 관점: {step.innovation_angle}\n"
            f"• 인류 난제 기여: {step.grand_challenge_link}\n"
            f"• 대안 접근: {step.alternative_approach}\n\n"
            f"필요 패키지: {json.dumps(plan.packages_needed, ensure_ascii=False)}\n\n"
            f"{context}\n\n"
            f"{self.brain_context}\n\n"
            f"{creativity_boost}\n"
            "완전하고 독립 실행 가능한 Python 코드를 작성하세요.\n"
            "GPU 집약적 연산이 필요하지 않으면 로컬에서 실행 가능하게 작성하세요.\n"
            "순수 Python만 반환 (마크다운 없음)."
        )

        messages = [
            {"role": "system", "content": self.CODER_SYSTEM},
            {"role": "user", "content": prompt},
        ]

        code = self.client.chat(
            messages, self.coder_model,
            temperature=min(0.5 + 0.05 * attempt, 0.85),
            max_tokens=7000,
        )
        code = self._extract_python(code)

        if self.use_critique and len(code) > 100 and attempt == 1:
            code = self._apply_critique(code, step, messages)

        return code

    def fix_error_persistent(
        self, code: str, error: str, step: ResearchStep, attempt: int,
    ) -> str:
        recovery_prompt = self.persistence.get_recovery_prompt(
            code, error, step, attempt, self.client, self.coder_model
        )
        messages = [
            {"role": "system", "content": self.CODER_SYSTEM},
            {"role": "user", "content": recovery_prompt},
        ]
        fixed = self.client.chat(
            messages, self.coder_model,
            temperature=0.5 + 0.07 * attempt,
            max_tokens=7000,
        )
        return self._extract_python(fixed)

    def extract_insights(
        self, step: ResearchStep, result: ExecutionResult, plan: ResearchPlan
    ) -> Tuple[List[str], List[str]]:
        if result.is_empty():
            return [], []

        output_text = (result.colab_output.strip() or result.stdout or "")[:1200]
        messages = [
            {"role": "system", "content": self.INSIGHT_SYSTEM},
            {"role": "user", "content": (
                f"연구 질문: {plan.research_question}\n"
                f"인류 난제 연결: {plan.grand_challenge}\n"
                f"단계 가설: {step.hypothesis}\n\n"
                f"실험 출력:\n```\n{output_text}\n```\n\n"
                "JSON으로 반환:\n"
                "{\n"
                '  "insights": ["인사이트1", "인사이트2"],\n'
                '  "novel_findings": ["★ 새로운 발견1", "★ 발견2"]\n'
                "}\n"
                "novel_findings는 예상치 못한, 기존과 다른, 인류 난제 해결에 기여하는 발견만."
            )},
        ]
        try:
            raw = self.client.chat(messages, self.coder_model,
                                   temperature=0.3, max_tokens=800)
            cleaned = NIMClient._extract_json(raw)
            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError:
                data = {}
            if not isinstance(data, dict):
                data = {}
            insights = [str(i)[:200] for i in data.get("insights", []) if i]
            novel = [str(i)[:200] for i in data.get("novel_findings", []) if i]
            return insights, novel
        except Exception:
            pass
        return [], []

    def adapt_plan(
        self, memory: ResearchMemory, remaining_steps: List[ResearchStep]
    ) -> List[ResearchStep]:
        if not memory.completed_steps or not remaining_steps:
            return remaining_steps

        context = memory.get_context_for_next_step(3000)
        novel = "\n".join(f"★ {d}" for d in memory.novel_discoveries[-3:])

        messages = [
            {"role": "user", "content": (
                f"연구 질문: {memory.plan.research_question if memory.plan else ''}\n"
                f"인류 난제: {memory.plan.grand_challenge if memory.plan else ''}\n\n"
                f"지금까지 결과:\n{context}\n\n"
                f"혁신적 발견 (이것을 바탕으로 계획 수정!):\n{novel}\n\n"
                "남은 계획:\n"
                + "\n".join(f"{i+1}. {s.title}: {s.objective[:80]}"
                            for i, s in enumerate(remaining_steps))
                + "\n\n"
                "발견된 혁신적 내용과 인류 난제 연결을 바탕으로 남은 단계를 더 흥미롭게 수정하세요.\n"
                "JSON 배열:\n"
                '[{"id": N, "title": "...", "objective": "...", "hypothesis_tested": "...", '
                '"innovation_angle": "...", "grand_challenge_link": "..."}]\n'
                "순수 JSON만."
            )},
        ]

        try:
            raw = self.client.chat(messages, self.planner_model,
                                   temperature=0.6, max_tokens=3000)
            cleaned = NIMClient._extract_json(raw)
            try:
                updated = json.loads(cleaned)
            except json.JSONDecodeError:
                # _extract_json 이 "{}" 를 반환한 경우 등 배열이 아니면 건너뜀
                updated = []
            if not isinstance(updated, list):
                # dict 로 반환된 경우 "steps" 키 탐색
                updated = updated.get("steps", []) if isinstance(updated, dict) else []
            for i, upd in enumerate(updated):
                if i < len(remaining_steps):
                    if "objective" in upd:
                        remaining_steps[i].objective = upd["objective"]
                    if "hypothesis_tested" in upd:
                        remaining_steps[i].hypothesis = upd["hypothesis_tested"]
                    if "innovation_angle" in upd:
                        remaining_steps[i].innovation_angle = upd["innovation_angle"]
                    if "grand_challenge_link" in upd:
                        remaining_steps[i].grand_challenge_link = upd["grand_challenge_link"]
            print(f"  [NEXUS] 적응적 재계획: {len(updated)}개 단계 업데이트")
        except Exception as e:
            print(f"  [NEXUS] 재계획 실패 (원래 계획 유지): {e}")

        return remaining_steps

    def _apply_critique(self, code: str, step: ResearchStep,
                        original_messages: List[Dict]) -> str:
        try:
            critique_msg = [
                {"role": "system", "content": self.CRITIC_SYSTEM},
                {"role": "user", "content": (
                    f"목표: {step.objective}\n"
                    f"인류 난제 연결: {step.grand_challenge_link}\n\n"
                    f"코드:\n```python\n{code[:2000]}\n```\n"
                    "핵심 개선사항을 bullet 3개로."
                )},
            ]
            critique = self.client.chat(critique_msg, self.coder_model,
                                        temperature=0.2, max_tokens=300)
            if critique and len(critique.strip()) > 20:
                improved_messages = original_messages + [
                    {"role": "assistant", "content": f"```python\n{code}\n```"},
                    {"role": "user", "content": (
                        f"비평:\n{critique}\n\n"
                        "이 비평을 반영한 개선 코드를 작성하세요. "
                        "특히 더 창의적이고 인류 난제 해결에 가까운 방향으로 개선하세요. "
                        "순수 Python만."
                    )},
                ]
                improved = self.client.chat(improved_messages, self.coder_model,
                                            temperature=0.5, max_tokens=7000)
                improved_code = self._extract_python(improved)
                if len(improved_code) > 50:
                    return improved_code
        except Exception as e:
            print(f"  [NEXUS] Critique 적용 실패: {e}")
        return code

    @staticmethod
    def _extract_python(text: str) -> str:
        if not text:
            return ""
        m = re.search(r"```python\s*\n?([\s\S]*?)```", text)
        if m:
            return m.group(1).strip()
        m = re.search(r"```\s*\n?([\s\S]*?)```", text)
        if m:
            return m.group(1).strip()
        text = re.sub(r"<think>[\s\S]*?</think>", "", text)
        return text.strip()

    @staticmethod
    def _fallback_plan(prompt: str, max_steps: int) -> Dict:
        return {
            "research_question": prompt,
            "grand_challenge": "인류 지식의 한계 확장",
            "hypotheses": [
                "제1 가설: 직접적 접근이 유효한 결과를 낳는다",
                "제2 가설: 비선형적 패턴이 숨겨져 있다",
                "제3 가설: 분야 융합적 접근이 새로운 통찰을 제공한다",
            ],
            "wild_ideas": ["완전히 새로운 알고리즘 발명", "물리 법칙을 AI에 적용"],
            "interdisciplinary_fields": ["수학", "물리학", "AI"],
            "methodology": "실증적 코드 실험 + 이론 합성",
            "innovation_angle": "창의적 계산 탐구 + 새로운 이론 형성",
            "packages_needed": ["numpy", "matplotlib", "pandas", "scikit-learn", "scipy"],
            "target_outputs": ["논문", "이론", "프로그램"],
            "steps": [
                {
                    "id": i + 1,
                    "title": f"탐구 단계 {i+1}",
                    "objective": f"주제의 {i+1}번째 깊은 탐구: {prompt[:40]}",
                    "hypothesis_tested": f"가설 {i+1}",
                    "expected_output": "새로운 인사이트와 시각화",
                    "surprise_factor": "예상치 못한 패턴",
                    "innovation_angle": "새로운 관점",
                    "alternative_approach": "대안적 접근",
                    "grand_challenge_link": "인류 지식 확장에 기여",
                }
                for i in range(min(max_steps, 5))
            ],
        }


# ═══════════════════════════════════════════════════════════════════════
#  RESEARCH MODES
# ═══════════════════════════════════════════════════════════════════════

RESEARCH_MODES = {
    # ── 범용 태스크 모드 (v6 신규) ────────────────────────────────────
    "code":    ("코드 구현",      "완전하고 프로덕션 품질의 코드를 작성하세요. 엣지케이스, 오류처리, 최적화 포함."),
    "debug":   ("디버그/수정",    "체계적으로 문제를 진단하고 수정하세요. 근본 원인 파악 + 예방 전략 포함."),
    "write":   ("글쓰기/작성",    "독자의 사고를 바꾸는 탁월한 글을 작성하세요. 구조, 논리, 문체 완벽히."),
    "math":    ("수학/증명",      "엄밀한 수학적 증명 + 숨겨진 패턴 발견 + 직관적 시각화."),
    "plan":    ("전략/계획",      "실행 가능한 천재적 전략을 수립하세요. 단계별, 우선순위, 리스크 포함."),
    "design":  ("시스템 설계",    "우아하고 확장 가능한 시스템을 설계하세요. 원칙 기반 + 트레이드오프 명시."),
    # ── 연구/혁신 모드 (v5 유지) ──────────────────────────────────────
    "explore":    ("자율 탐구",    "자유로운 탐구 정신으로 예상치 못한 발견을 추구하세요."),
    "experiment": ("실험 설계",   "과학적 방법론으로 가설을 세우고 실험으로 검증하세요."),
    "build":      ("프로젝트 빌드","아키텍처부터 완전한 구현까지 단계적으로 구축하세요."),
    "analyze":    ("데이터 분석", "데이터에서 숨겨진 패턴과 인사이트를 발견하세요."),
    "innovate":   ("혁신 탐색",   "기존 한계를 넘어 창의적이고 혁신적인 접근법을 탐색하세요."),
    "theory":     ("이론 창조",   "실험 결과에서 완전히 새로운 이론적 프레임워크를 창조하세요."),
    "paper":      ("논문 작성",   "연구를 학술 논문 수준으로 합성하고 새로운 기여를 명확히 하세요."),
    "patent":     ("발명 특허",   "기술 혁신을 특허 출원 가능한 발명으로 구체화하세요."),
    "invent":     ("발명 창조",   "세상에 없던 새로운 알고리즘, 방법론, 시스템을 발명하세요."),
    "grand":      ("인류 난제",   "기후, 암, 에너지, AI 안전성 등 인류 난제를 정면으로 공략하세요."),
}


# ═══════════════════════════════════════════════════════════════════════
#  NEXUS AGENT v5 — 메인 오케스트레이터
# ═══════════════════════════════════════════════════════════════════════

class NexusAgent:
    """
    NEXUS 자율 에이전트 v7.0 — HYPERION EDITION

    μῦθος: 현실 이해를 재형성하는 근본 서사.
    유저가 말하는 그 어떤 것이든, 수백 세션에도 절대 망각 없이,
    Claude Mythos급 지능으로 천재적으로 해결합니다.

    ✅ NEXUS Brain — 수백 세션 영속 지식 (절대 망각 없음)
    ✅ 범용 태스크 라우터 — 코드/글/수학/분석/설계/연구 모두
    ✅ Mythos급 시스템 프롬프트 (SWE-bench 93.9% 수준 목표)
    ✅ 교차-세션 컨텍스트 주입 (과거 지식 → 현재 세션)
    ✅ 창의성 극한 엔진 + 끈기 엔진 (완전 유지)
    ✅ NVIDIA NIM 모델 동적 FETCH + 역할별 자동 선택
    ✅ 수백 단계 지원 (체크포인트 자동 저장/복구)
    ✅ 혁신 합성기 (논문/특허/이론/README 자동 생성)
    ✅ 적응형 재계획 (새로운 발견 기반으로 실시간 진화)
    """

    def __init__(
        self,
        api_key: str,
        planner_model: str = "auto",
        coder_model: str = "auto",
        writer_model: str = "auto",
        max_steps: int = 200,
        mode: str = "auto",            # "auto" → UniversalTaskRouter 자동 선택
        temperature: float = 0.95,
        creativity_level: float = 0.97,
        use_critique: bool = True,
        cot_enabled: bool = True,
        adapt_plan: bool = True,
        adapt_interval: int = 3,
        max_retries_per_step: int = 8,
        checkpoint_every: int = 5,
        output_dir: str = "nexus_outputs",
        synthesize: bool = True,
        synthesize_paper: bool = True,
        synthesize_theory: bool = True,
        synthesize_readme: bool = True,
        verbose: bool = True,
        resume_checkpoint: Optional[str] = None,
        drive_sync: bool = False,
        drive_folder: str = "NEXUS_Research",
        brain_file: Optional[str] = None,  # None → 기본 ~/.nexus_brain.json
        # ── DEMON Algorithm ──────────────────────────────────────────
        demon_enabled: bool = True,         # DEMON 알고리즘 활성화
        demon_max_iterations: int = 3,      # 자동 재이터레이션 최대 횟수
        demon_on_steps: bool = True,        # 각 스텝 완료 후 DEMON 비평
        demon_on_plan: bool = True,         # 계획 수립 후 DEMON 비평
    ):
        self.demon_enabled = demon_enabled
        self.demon_on_steps = demon_on_steps
        self.demon_on_plan = demon_on_plan
        self.demon_max_iterations = demon_max_iterations
        self.api_key = api_key
        self.max_steps = max_steps
        self.mode = mode
        self.temperature = temperature
        self.creativity_level = creativity_level
        self.adapt_plan_enabled = adapt_plan
        self.adapt_interval = adapt_interval
        self.max_retries = max_retries_per_step
        self.checkpoint_every = checkpoint_every
        self.synthesize = synthesize
        self.synthesize_paper = synthesize_paper
        self.synthesize_theory = synthesize_theory
        self.synthesize_readme = synthesize_readme
        self.verbose = verbose
        self.resume_checkpoint = resume_checkpoint
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.memory: Optional[ResearchMemory] = None

        # ── NEXUS Brain 초기화 (영속 지식) ──────────────────────────
        if brain_file:
            NexusBrain.BRAIN_FILE = Path(brain_file)
        self.brain = NexusBrain(verbose=verbose)

        # ── 컴포넌트 초기화 ──────────────────────────────────────────
        self.nim = NIMClient(api_key)
        self.executor = CodeExecutor(output_dir=output_dir)
        self.creativity_engine = CreativityEngine()
        self.task_router = UniversalTaskRouter()

        self._log("🔍 NVIDIA NIM 모델 목록 조회 중...")
        self.registry = ModelRegistry(api_key, verbose=verbose)

        self.planner_model = (
            planner_model if planner_model != "auto"
            else self.registry.select("planner")
        )
        self.coder_model = (
            coder_model if coder_model != "auto"
            else self.registry.select("coder")
        )
        self.writer_model = (
            writer_model if writer_model != "auto"
            else self.registry.select("writer")
        )

        # harness는 run()에서 topic을 알고 난 뒤 brain_context와 함께 초기화
        self._harness_kwargs = dict(
            use_critique=use_critique,
            cot_enabled=cot_enabled,
            creativity_level=creativity_level,
        )
        self.harness: Optional[IntelligenceHarness] = None

        self.synthesizer = InnovationSynthesizer(
            self.nim, self.writer_model, self.output_dir
        )
        self.local_saver = LocalSaver(folder_name=drive_folder, verbose=verbose)

        # ── HYPERION 확장 컴포넌트 ────────────────────────────────
        self.knowledge_graph = HyperionKnowledgeGraph(self.brain)
        self.benchmark = HyperionBenchmarkEngine(self.executor, self.output_dir)
        self.auto_installer = HyperionAutoInstaller()
        self.exp_tracker = HyperionExperimentTracker()
        self.evaluator = HyperionSelfEvaluator(self.nim, self.writer_model)
        self.stream_logger = HyperionStreamingLogger(
            self.output_dir, datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        # Multi-Agent Council (역할별 모델 공유)
        self.council = HyperionMultiAgentCouncil(self.nim, {
            "skeptic":     self.planner_model,
            "visionary":   self.planner_model,
            "engineer":    self.coder_model,
            "theorist":    self.planner_model,
            "synthesizer": self.writer_model,
        })

        # ── ☠️  DEMON Algorithm 초기화 ────────────────────────────────
        self.demon: Optional[DEMONAlgorithm] = None
        if self.demon_enabled:
            self.demon = DEMONAlgorithm(
                nim=self.nim,
                planner_model=self.planner_model,
                coder_model=self.coder_model,
                executor=self.executor,
                brain=self.brain,
                verbose=verbose,
                auto_iterate=True,
                max_demon_iterations=demon_max_iterations,
            )
            self._log("☠️  DEMON Algorithm 활성화 — 신랄한 비평·보강 엔진 준비완료")

        env = EnvDetector.report()
        self._banner("NEXUS Agent v7.0 — HYPERION EDITION",
                     "HYPERION: 유저가 말하는 그 어떤 것이든 · 수백 세션 영속 지식")
        self._log(f"   환경: {'Colab ✅' if env['colab'] else '로컬 터미널'} · "
                  f"GPU: {'✅' if env['gpu'] else '❌'} · Python {env['python']}")
        self._log(f"   Planner : {self.planner_model.split('/')[-1]}")
        self._log(f"   Coder   : {self.coder_model.split('/')[-1]}")
        self._log(f"   Writer  : {self.writer_model.split('/')[-1]}")
        self._log(f"   Brain   : {self.brain._stats_line()}")
        self._log(f"   창의성  : {creativity_level*100:.0f}% · "
                  f"최대 {max_steps}단계 · 끈기 {max_retries_per_step}회/단계")

    # ── 메인 실행 ────────────────────────────────────────────────────

    def run(self, prompt: str) -> "ResearchMemory":
        """
        메인 실행 루프.
        - 모드 "auto": UniversalTaskRouter로 자동 선택
        - NexusBrain에서 교차-세션 컨텍스트 주입
        - 완료 시 Brain에 자동 저장
        """
        # ── 모드 자동 결정 ───────────────────────────────────────────
        if self.mode == "auto" or self.mode not in RESEARCH_MODES:
            auto_mode, auto_suffix = UniversalTaskRouter.detect_and_report(prompt, self.brain)
            resolved_mode = auto_mode
            self._log(f"🔀 자동 모드 선택: [{resolved_mode}] ← '{prompt[:50]}'")
        else:
            resolved_mode = self.mode

        mode_label, mode_suffix = RESEARCH_MODES.get(
            resolved_mode, ("범용", "최고 수준으로 해결하세요.")
        )

        # ── Brain 교차-세션 컨텍스트 빌드 ───────────────────────────
        brain_ctx = MythosContextCompressor.build_crosssession_context(self.brain, prompt)
        if brain_ctx:
            self._log(f"🧠 Brain 교차-세션 컨텍스트 주입 ({len(brain_ctx)} chars)")

        # ── IntelligenceHarness 초기화 (brain_context 포함) ──────────
        self.harness = IntelligenceHarness(
            self.nim, self.planner_model, self.coder_model, self.writer_model,
            brain_context=brain_ctx,
            **self._harness_kwargs,
        )

        # ── ExperimentTracker: run 시작 ──────────────────────────────
        self.exp_tracker.start_run(prompt[:60], params={
            "mode": resolved_mode, "max_steps": self.max_steps,
            "creativity": self.creativity_level,
        })
        self.stream_logger.log("SESSION_START", {"topic": prompt, "mode": resolved_mode})

        # ── 체크포인트 복구 ──────────────────────────────────────────
        resume_from = 0
        if self.resume_checkpoint and os.path.exists(self.resume_checkpoint):
            self.memory, resume_from = ResearchMemory.load_checkpoint(
                self.resume_checkpoint
            )
            self._log(f"♻️  체크포인트 복구: Step {resume_from}부터 재시작")
        else:
            self.memory = ResearchMemory(prompt, checkpoint_dir=".nexus_checkpoints")

        # ── Phase 1: 계획 수립 ───────────────────────────────────────
        self._section(f"Phase 1: MYTHOS 계획 수립 [{mode_label}]")
        if resume_from == 0:
            plan = self.harness.create_plan(
                prompt, mode_label, mode_suffix, self.max_steps
            )
            self.memory.plan = plan
        else:
            plan = self.memory.plan or ResearchPlan(research_question=prompt)

        self._log(f"📋 핵심 질문: {plan.research_question[:120]}")
        if plan.grand_challenge:
            self._log(f"🎯 목표/난제: {plan.grand_challenge[:100]}")
        for i, h in enumerate(plan.hypotheses[:3]):
            self._log(f"💭 가설 {i+1}: {h[:100]}")
        if plan.wild_ideas:
            for w in plan.wild_ideas[:2]:
                self._log(f"🌪️  파격 아이디어: {w[:100]}")
        if plan.interdisciplinary:
            self._log(f"🔗 융합 분야: {', '.join(plan.interdisciplinary[:4])}")
        self._log(f"🔬 총 {len(plan.steps)}단계 계획")
        if plan.target_outputs:
            self._log(f"🎯 목표 산출물: {', '.join(plan.target_outputs)}")

        # ── Phase 0: DEMON 초기 계획 비평 ────────────────────────────
        if self.demon_enabled and self.demon_on_plan and self.demon and resume_from == 0:
            self._section("Phase 0: ☠️  DEMON 초기 계획 비평·보강")
            plan_dict = {
                "research_question": plan.research_question,
                "hypotheses": plan.hypotheses[:3],
                "methodology": plan.methodology,
                "innovation_angle": plan.innovation_angle,
                "grand_challenge": plan.grand_challenge,
                "wild_ideas": plan.wild_ideas[:3],
            }
            demon_critique, demon_overhaul, demon_code = self.demon.run_demon_on_topic(
                topic=prompt,
                brain_context=brain_ctx,
                plan_json=plan_dict,
            )
            # 보강 결과로 계획 강화
            overhaul_steps = demon_overhaul.get("research_steps", [])
            if overhaul_steps and len(overhaul_steps) > 0:
                demon_innovation = demon_overhaul.get("paradigm_shift", "")
                if demon_innovation:
                    plan.innovation_angle = f"[DEMON강화] {demon_innovation[:200]}"
                demon_impossible = demon_overhaul.get("impossible_to_possible", "")
                if demon_impossible:
                    plan.wild_ideas.insert(0, f"[DEMON] {str(demon_impossible)[:150]}")
            # DEMON 보강 코드 저장
            if demon_code and len(demon_code.strip()) > 50:
                demon_code_file = self.output_dir / "demon_overhaul_initial.py"
                demon_code_file.write_text(demon_code, encoding="utf-8")
                self.local_saver.save(str(demon_code_file), "DEMON 초기 보강 코드")
                self._log(f"☠️  DEMON 보강 코드 저장: {demon_code_file.name}")

        # ── Phase 2: 환경 설정 ───────────────────────────────────────
        self._section("Phase 2: 환경 설정 + 패키지 설치")
        if plan.packages_needed:
            self.executor.install_packages(plan.packages_needed)
        self._log("✅ 환경 준비 완료")

        # ── Phase 3: 실행 루프 ───────────────────────────────────────
        self._section(f"Phase 3: MYTHOS 실행 루프 ({len(plan.steps)}단계)")
        steps = list(plan.steps)
        i = resume_from
        while i < len(steps):
            step = steps[i]
            self._log(f"\n{'─'*60}")
            self._log(f"{step.status_emoji()} Step {i+1}/{len(steps)}: {step.title}")
            self._log(f"   목표: {step.objective[:120]}")
            if step.innovation_angle:
                self._log(f"   혁신: {step.innovation_angle[:80]}")
            if step.grand_challenge_link:
                self._log(f"   🌍 의미: {step.grand_challenge_link[:80]}")

            self.stream_logger.render_progress(i + 1, len(steps), step.title, True)
            self.stream_logger.log("STEP_START", {"step_id": step.id, "title": step.title})
            success = self._execute_step_with_persistence(step, plan, i)

            if step.result and not step.result.is_empty():
                insights, novel = self.harness.extract_insights(step, step.result, plan)
                step.insights = insights
                step.novel_findings = novel

                for ins in insights[:3]:
                    self._log(f"   💡 {ins[:100]}")
                for nov in novel[:2]:
                    self._log(f"   🌟 {nov[:100]}")
                    self.memory.add_creative_branch(step.title, nov)

                step.creativity_score = self.creativity_engine.score_creativity(
                    step.code, step.result
                )
                if step.creativity_score >= 7.0:
                    self._log(f"   ✨ 창의성 점수: {step.creativity_score:.1f}/10")

            figs = self.executor.save_figures(step.id)
            if figs:
                self._log(f"   📊 시각화: {', '.join(Path(f).name for f in figs)}")
                for fig in figs:
                    self.local_saver.save(fig, f"Step {step.id} 시각화")

            # ── ☠️  DEMON 스텝 비평·보강 ─────────────────────────────
            if self.demon_enabled and self.demon_on_steps and self.demon:
                demon_new_code = self.demon.run_demon_on_step(
                    step=step, plan=plan,
                    result=step.result,
                    brain_context=brain_ctx,
                )
                if demon_new_code and len(demon_new_code.strip()) > 50:
                    # 보강 코드 저장
                    demon_step_file = self.output_dir / f"demon_overhaul_step{step.id:03d}.py"
                    demon_step_file.write_text(demon_new_code, encoding="utf-8")
                    self.local_saver.save(str(demon_step_file), f"DEMON Step {step.id} 보강")
                    self._log(f"   ☠️  DEMON 보강코드 → {demon_step_file.name}")

            # 스텝 자기평가 (성공한 경우)
            if success and step.result and len(step.code) > 100:
                try:
                    eval_result = self.evaluator.evaluate_step(step, step.result)
                    total_score = eval_result.get("total", 0)
                    if total_score and total_score >= 7.0:
                        self._log(f"   🏆 품질 점수: {total_score:.1f}/10 [{eval_result.get('verdict','?')}]")
                    self.exp_tracker.log_metric("step_quality", total_score or 0.0, step=i)
                except Exception:
                    pass
            self.stream_logger.log(
                "STEP_SUCCESS" if success else "STEP_FAIL",
                {"step_id": step.id, "attempts": step.attempts,
                 "duration": step.result.duration if step.result else 0}
            )
            self.memory.add_completed_step(step)

            if (i + 1) % self.checkpoint_every == 0:
                ckpt_path = self.memory.save_checkpoint(i + 1)
                self._log(f"   💾 체크포인트 저장: {ckpt_path}")

            if (self.adapt_plan_enabled
                    and (i + 1) % self.adapt_interval == 0
                    and i < len(steps) - 1):
                self._log("  🔄 발견 기반 재계획 중...")
                remaining = steps[i+1:]
                steps[i+1:] = self.harness.adapt_plan(self.memory, remaining)

            i += 1

        # ── Phase 4: 혁신 합성 ───────────────────────────────────────
        if self.synthesize:
            self._section("Phase 4: 혁신 합성 (논문/이론/README 생성)")

            if self.synthesize_paper:
                try:
                    paper_path = self.synthesizer.generate_paper(self.memory)
                    self.local_saver.save(paper_path, "연구 논문")
                except Exception as e:
                    self._log(f"⚠️  논문 생성 오류: {e}")

            if self.synthesize_theory:
                try:
                    theory_path = self.synthesizer.generate_theory(self.memory)
                    self.local_saver.save(theory_path, "새로운 이론")
                except Exception as e:
                    self._log(f"⚠️  이론 생성 오류: {e}")

            if self.synthesize_readme:
                try:
                    readme_path = self.synthesizer.generate_readme(self.memory)
                    self.local_saver.save(readme_path, "프로젝트 README")
                except Exception as e:
                    self._log(f"⚠️  README 생성 오류: {e}")

        # ── Phase 4.5: Knowledge Graph 업데이트 + HTML 리포트 ────────
        try:
            self.knowledge_graph = HyperionKnowledgeGraph(self.brain)
            kg_summary = self.knowledge_graph.summary()
            self._log(f"🕸  {kg_summary}")
        except Exception:
            pass
        try:
            html_path = self.stream_logger.generate_html_report(self.memory)
            self.local_saver.save(html_path, "HTML 리포트")
        except Exception as e:
            self._log(f"⚠️  HTML 리포트 오류: {e}")

        # ── Phase 5: 로컬 저장 ───────────────────────────────────────
        self._section("Phase 5: 로컬 파일 최종 저장")
        count = self.local_saver.sync_all()
        self._log(f"✅ 저장 완료: {count}개 파일 → ./{self.local_saver.folder_name}/")

        # ── Phase 6: NEXUS Brain 업데이트 (영속 지식 저장) ───────────
        self._section("Phase 6: NEXUS Brain 업데이트 (영속 지식 저장)")
        MythosContextCompressor.compress_and_store(
            self.memory, self.brain, mode=resolved_mode,
            nim=self.nim, model=self.writer_model,
        )
        self._log(f"🧠 Brain 최신 상태: {self.brain._stats_line()}")

        self.exp_tracker.log_metric("success_rate",
            float(self.memory.get_statistics()["success_rate"].replace("%","")) / 100
        )
        self.exp_tracker.end_run("FINISHED")
        self.stream_logger.log("SESSION_END", {"stats": self.memory.get_statistics()})
        self._print_summary()
        return self.memory

    def _execute_step_with_persistence(
        self, step: ResearchStep, plan: ResearchPlan, step_index: int
    ) -> bool:
        code = ""
        for attempt in range(1, self.max_retries + 1):
            step.attempts = attempt

            if attempt == 1:
                self._log(f"   🧠 코드 생성 중...")
                code = self.harness.generate_code(step, plan, self.memory, step_index, attempt)
            else:
                strategy_name, _ = self.harness.persistence.get_strategy(attempt)
                self._log(f"   🔧 재시도 {attempt}/{self.max_retries} — 전략: {strategy_name}")
                if step.result and step.result.error:
                    code = self.harness.fix_error_persistent(
                        code, step.result.error, step, attempt
                    )

            if not code or len(code.strip()) < 30:
                self._log(f"   ⚠️  코드 생성 실패 (attempt {attempt})")
                continue

            step.code = code

            # Colab 중단점 여부 안내
            if ColabBreakpoint.is_required(code):
                self._log(f"   🖥️  GPU 코드 감지 → Colab 중단점 실행")
            else:
                self._log(f"   ▶️  로컬 실행 ({len(code.splitlines())}줄, timeout=300s)...")

            result = self.executor.run(code, timeout=300, step_id=step.id)
            step.result = result

            if result.success:
                step.succeeded = True
                out_chars = len(result.colab_output or result.stdout)
                self._log(f"   ✅ 성공 ({result.duration:.1f}s) | 출력: {out_chars} chars")
                preview = (result.colab_output.strip() or result.stdout.strip())[:400]
                for line in preview.splitlines()[:8]:
                    self._log(f"      │ {line}")
                if len(preview.splitlines()) > 8:
                    self._log(f"      │ ...")
                return True
            else:
                error_preview = (result.error or "")[:250]
                self._log(f"   ❌ 실패 (attempt {attempt}): {error_preview}")
                if result.stdout.strip():
                    self._log(f"   📝 부분 출력: {result.stdout[:150]}")
                self.memory.add_failure(
                    f"Step {step.id} attempt {attempt}: {error_preview[:80]}"
                )
                # AutoInstaller: ImportError 감지 시 자동 패키지 설치
                if result.error and self.auto_installer.auto_fix(result.error):
                    self._log(f"   🔧 패키지 자동 설치 → 즉시 재시도")
                    continue
                if attempt < self.max_retries:
                    wait = min(2 * attempt, 10)
                    self._log(f"   ⏳ {wait}초 후 재시도...")
                    time.sleep(wait)

        self._log(f"   ⛔ Step {step.id} — 최대 재시도 초과. 다음 단계로.")
        return False

    def _print_summary(self):
        if not self.memory:
            return
        stats = self.memory.get_statistics()
        nim_stats = self.nim.get_stats()
        self._banner("🎉 연구 완료", "NEXUS Innovation Engine v7.0")

        print(f"\n  📊 실행 결과: {stats['succeeded']}/{stats['total_steps']} 단계 성공 "
              f"({stats['success_rate']})")
        print(f"  ⏱️  총 실행 시간: {stats['total_time']}")
        print(f"  📡 API 호출: {nim_stats['api_calls']}회 "
              f"({nim_stats['total_tokens']:,} tokens)")
        print(f"  💡 누적 인사이트: {stats['insights']}개")
        print(f"  🌟 혁신적 발견: {stats['novel_discoveries']}개")
        print(f"  💡 창의적 분기: {stats['creative_branches']}개")
        print()

        print("  단계별 요약:")
        for step in self.memory.completed_steps:
            cs = f" [창의성 {step.creativity_score:.1f}]" if step.creativity_score >= 7 else ""
            attempts_str = f" ({step.attempts}회 시도)" if step.attempts > 1 else ""
            print(f"  {step.status_emoji()} Step {step.id}: {step.title}{attempts_str}{cs}")
            for ins in step.insights[:2]:
                print(f"       💡 {ins[:90]}")
            for nov in step.novel_findings[:1]:
                print(f"       🌟 {nov[:90]}")

        if self.memory.novel_discoveries:
            print()
            print("  🌟 혁신적 발견사항:")
            for d in self.memory.novel_discoveries[:8]:
                print(f"  ★ {d[:110]}")

        if self.memory.global_insights:
            print()
            print("  🔑 핵심 인사이트:")
            for ins in self.memory.global_insights[:6]:
                print(f"  • {ins[:110]}")

        print()
        print("  📁 저장된 파일:")
        all_files = (
            list(self.output_dir.glob("*.png"))
            + list(self.output_dir.glob("*.md"))
            + list(self.output_dir.glob("*.json"))
            + list(Path(self.local_saver.folder_name).glob("*"))
        )
        seen = set()
        for f in sorted(all_files):
            if f.name not in seen and f.is_file():
                seen.add(f.name)
                size = f.stat().st_size
                icon = "📊" if f.suffix == ".png" else "📄"
                print(f"  {icon} {f.name} ({size//1024}KB)")
        if not seen:
            print("  (파일 없음)")

        print(f"\n  📂 결과 폴더: ./{self.local_saver.folder_name}/")

        # NIM API 상세 통계
        nim_detail = self.nim.get_stats()
        print(f"  ⚡ 평균 응답: {nim_detail.get('avg_latency_s',0):.2f}s · "
              f"p95: {nim_detail.get('p95_latency_s',0):.2f}s · "
              f"추정 비용: ${nim_detail.get('total_cost_est_usd',0):.4f}")

        # Knowledge Graph 요약
        try:
            kg = HyperionKnowledgeGraph(self.brain)
            if self.brain.data.get("concept_graph"):
                hubs = kg.hub_concepts(3)
                if hubs:
                    print(f"  🕸  지식 그물망 허브 개념: " +
                          ", ".join(f"{k}({v})" for k, v in hubs))
        except Exception:
            pass

        # 실험 추적 요약
        print()
        print("  " + "─"*58)
        print(self.exp_tracker.summary_table())

        # ── ☠️  DEMON 리포트 ─────────────────────────────────────────
        if self.demon_enabled and self.demon:
            print(self.demon.get_demon_report())


    # ── 유틸리티 ────────────────────────────────────────────────────

    def _log(self, msg: str):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")

    def _section(self, title: str):
        if self.verbose:
            print(f"\n{'═'*65}")
            print(f"  {title}")
            print(f"{'═'*65}")

    def _banner(self, title: str, subtitle: str):
        print(f"\n{'╔'+'═'*63+'╗'}")
        print(f"{'║'} ⚡ {title:<59} {'║'}")
        if subtitle:
            sub = subtitle[:57]
            print(f"{'║'}   {sub:<61} {'║'}")
        print(f"{'╚'+'═'*63+'╝'}")

    # ── 편의 메서드 ─────────────────────────────────────────────────

    def generate_paper(self, title: str = None) -> str:
        assert self.memory, "먼저 run()을 실행하세요."
        return self.synthesizer.generate_paper(self.memory, title)

    def council_deliberate(self, topic: str, context: str = "") -> Dict:
        """Multi-Agent Council 토론 실행."""
        result = self.council.deliberate(topic, context)
        self.council.print_council_report(result)
        return result

    def benchmark_all(self) -> Dict:
        """메모리 내 모든 완료 스텝 벤치마크 실행."""
        assert self.memory, "먼저 run()을 실행하세요."
        return self.benchmark.run_benchmark(
            [s for s in self.memory.completed_steps if s.succeeded],
            tag=f"session_{self.memory.session_id}"
        )

    def evaluate_paper(self, paper_path: str) -> Dict:
        """생성된 논문 품질 자동 평가."""
        try:
            text = Path(paper_path).read_text(encoding="utf-8")
            result = self.evaluator.evaluate(text, "paper")
            self.evaluator.print_eval_report(result, title=Path(paper_path).name)
            return result
        except Exception as e:
            return {"error": str(e)}

    def show_knowledge_graph(self) -> str:
        """현재 Brain의 KG 요약 및 Mermaid export."""
        kg = HyperionKnowledgeGraph(self.brain)
        print(kg.summary())
        mermaid = kg.to_mermaid(max_edges=40)
        path = self.output_dir / "knowledge_graph.mmd"
        path.write_text(mermaid, encoding="utf-8")
        print(f"[KG] Mermaid 저장: {path}")
        return mermaid

    def show_experiments(self):
        """실험 추적 요약 테이블 출력."""
        print(self.exp_tracker.summary_table())

    def show_models(self):
        self.registry.print_available()

    def generate_patent(self) -> str:
        assert self.memory, "먼저 run()을 실행하세요."
        return self.synthesizer.generate_patent(self.memory)

    def generate_theory(self) -> str:
        assert self.memory, "먼저 run()을 실행하세요."
        return self.synthesizer.generate_theory(self.memory)

    def show_models(self):
        self.registry.print_available()



# ═══════════════════════════════════════════════════════════════════════
#  HYPERION KNOWLEDGE GRAPH — 개념 관계망 시각화 + 경로 탐색
# ═══════════════════════════════════════════════════════════════════════

class HyperionKnowledgeGraph:
    """
    NexusBrain의 개념 그물망을 시각화하고 탐색하는 고급 지식 그래프.
    - 개념 간 경로 탐색 (BFS/DFS)
    - 허브 개념 자동 감지 (중심성 분석)
    - 클러스터 자동 추출
    - Mermaid / DOT 형식 export
    """

    def __init__(self, brain: "NexusBrain"):
        self.graph: Dict[str, List[str]] = brain.data.get("concept_graph", {})
        self.brain = brain

    def hub_concepts(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """가장 많이 연결된 허브 개념 반환."""
        scores = {k: len(v) for k, v in self.graph.items()}
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def path(self, src: str, dst: str, max_depth: int = 5) -> Optional[List[str]]:
        """BFS로 src → dst 최단 경로 탐색."""
        if src not in self.graph:
            return None
        queue = [[src]]
        visited = {src}
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == dst:
                return path
            if len(path) > max_depth:
                continue
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def clusters(self, min_size: int = 2) -> List[List[str]]:
        """연결 컴포넌트(클러스터) 추출."""
        visited = set()
        result = []
        for node in self.graph:
            if node in visited:
                continue
            cluster = []
            stack = [node]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                cluster.append(n)
                stack.extend(self.graph.get(n, []))
            if len(cluster) >= min_size:
                result.append(cluster)
        return sorted(result, key=len, reverse=True)

    def to_mermaid(self, max_edges: int = 60) -> str:
        """Mermaid 다이어그램 형식으로 export."""
        lines = ["graph LR"]
        edge_count = 0
        for src, dsts in self.graph.items():
            for dst in dsts:
                if edge_count >= max_edges:
                    break
                src_id = re.sub(r"[^\\w]", "_", src)[:20]
                dst_id = re.sub(r"[^\\w]", "_", dst)[:20]
                lines.append(f"  {src_id}[\"{src[:25]}\"] --> {dst_id}[\"{dst[:25]}\"]")
                edge_count += 1
        return "\\n".join(lines)

    def to_dot(self) -> str:
        """Graphviz DOT 형식으로 export."""
        lines = ["digraph NexusBrain {", "  rankdir=LR;", '  node [shape=box, fontsize=10];']
        for src, dsts in self.graph.items():
            for dst in dsts[:5]:
                lines.append(f'  "{src[:30]}" -> "{dst[:30]}";')
        lines.append("}")
        return "\\n".join(lines)

    def summary(self) -> str:
        hubs = self.hub_concepts(5)
        cls = self.clusters()
        hub_str = ", ".join(f"{k}({v})" for k, v in hubs)
        return (f"[KnowledgeGraph] {len(self.graph)}개 개념 · "
                f"{sum(len(v) for v in self.graph.values())}개 엣지 · "
                f"{len(cls)}개 클러스터\\n  허브: {hub_str}")


# ═══════════════════════════════════════════════════════════════════════
#  HYPERION BENCHMARK ENGINE — 자동 실험 재현 + 성능 비교
# ═══════════════════════════════════════════════════════════════════════

class HyperionBenchmarkEngine:
    """
    이전 세션 코드를 재실행하여 성능을 비교·추적하는 벤치마크 엔진.

    기능:
    - 지정 스텝 코드 재실행 (체크포인트 기반)
    - 실행 시간 / 출력 변화량 자동 추적
    - 성능 회귀 감지 (regression detection)
    - 개선률 자동 계산 + 리포트 생성
    """

    def __init__(self, executor: "CodeExecutor", output_dir: Path):
        self.executor = executor
        self.output_dir = output_dir
        self.results: List[Dict] = []

    def run_benchmark(self, steps: List["ResearchStep"], tag: str = "") -> Dict:
        """여러 스텝을 벤치마크 실행."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {"tag": tag or ts, "ts": ts, "steps": []}
        total_duration = 0.0
        success = 0

        for step in steps:
            if not step.code:
                continue
            t0 = time.time()
            result = self.executor.run(step.code, timeout=120, step_id=step.id)
            dur = time.time() - t0
            total_duration += dur
            if result.success:
                success += 1
            entry = {
                "step_id": step.id,
                "title": step.title,
                "success": result.success,
                "duration": round(dur, 3),
                "output_len": len(result.stdout),
                "error": result.error[:100] if result.error else None,
            }
            report["steps"].append(entry)

        report["total_duration"] = round(total_duration, 2)
        report["success_rate"] = f"{success/max(len(steps),1)*100:.1f}%"
        self.results.append(report)

        # 리포트 저장
        fname = self.output_dir / f"benchmark_{ts}.json"
        fname.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[Benchmark] ✅ {success}/{len(steps)} 성공 · {total_duration:.1f}s · {fname.name}")
        return report

    def compare(self, a: Dict, b: Dict) -> str:
        """두 벤치마크 결과 비교."""
        lines = [f"벤치마크 비교: {a['tag']} vs {b['tag']}"]
        dur_change = b["total_duration"] - a["total_duration"]
        lines.append(f"  실행 시간: {a['total_duration']}s → {b['total_duration']}s "
                     f"({'▲' if dur_change > 0 else '▼'} {abs(dur_change):.2f}s)")
        lines.append(f"  성공률: {a['success_rate']} → {b['success_rate']}")
        return "\\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  HYPERION MULTI-AGENT COUNCIL — 다중 에이전트 토론 합성
# ═══════════════════════════════════════════════════════════════════════

class HyperionMultiAgentCouncil:
    """
    여러 AI 페르소나가 동시에 문제를 분석하고 최선의 답을 토론·합성하는 엔진.

    페르소나:
    - Skeptic: 모든 가정을 의심, 반증 가능성 탐색
    - Visionary: 10년 후 관점, 아직 없는 패러다임
    - Engineer: 실용성 중심, 즉시 구현 가능한 해법
    - Theorist: 수학적 형식화, 공리-정리 구조화
    - Synthesizer: 3개의 관점을 통합, 최선의 합성

    동작 방식:
    각 페르소나가 독립적으로 분석 → 상호 비판 → 합성 단계
    """

    PERSONAS = {
        "skeptic": (
            "당신은 NEXUS-SKEPTIC: 모든 주장에서 치명적 약점을 찾아내는 비판적 철학자."
            " 반증 가능성, 숨겨진 가정, 논리적 비약을 밝혀라. 3가지 핵심 반론 제시."
        ),
        "visionary": (
            "당신은 NEXUS-VISIONARY: 현재의 제약을 무시하고 10년 후 관점에서 사고하는 미래학자."
            " 아직 존재하지 않는 패러다임, 파격적 가능성, 인류 난제와의 연결을 제시."
        ),
        "engineer": (
            "당신은 NEXUS-ENGINEER: 즉시 구현 가능한 해법을 설계하는 실용주의 천재."
            " 구체적 알고리즘, 라이브러리, 성능 예측, 에러 처리 전략을 제시."
        ),
        "theorist": (
            "당신은 NEXUS-THEORIST: 모든 것을 수학적으로 형식화하는 순수 이론가."
            " 공리-정리 구조, 복잡도 분석, 수학적 증명 가능성, 형식 언어로 표현."
        ),
    }

    SYNTHESIZER_SYSTEM = (
        "당신은 NEXUS-SYNTHESIZER: 여러 관점들을 통합하여 가장 강력한 합성 해법을 만드는 통합자."
        " Skeptic의 반론, Visionary의 비전, Engineer의 실용성, Theorist의 엄밀함을"
        " 모두 통합한 새로운 접근법을 창조하라. JSON 형식:"
        ' {"synthesis": "통합 해법", "key_insight": "핵심 통찰", '
        '"next_action": "즉시 실행할 것", "open_question": "남은 미해결 질문"}'
    )

    def __init__(self, nim: "NIMClient", models: Dict[str, str]):
        """models: {"skeptic": model_id, "visionary": ..., "engineer": ..., "theorist": ..., "synthesizer": ...}"""
        self.nim = nim
        self.models = models

    def deliberate(self, topic: str, context: str = "", parallel: bool = False) -> Dict:
        """
        4개 페르소나의 분석 → Synthesizer 통합.
        parallel=True 이면 threading으로 동시 실행.
        """
        opinions: Dict[str, str] = {}
        user_msg = f"주제: {topic}\\n\\n컨텍스트:\\n{context[:1000]}" if context else f"주제: {topic}"

        def _ask(role: str):
            system = self.PERSONAS[role]
            model = self.models.get(role, self.models.get("engineer", ""))
            try:
                opinions[role] = self.nim.chat(
                    [{"role": "system", "content": system},
                     {"role": "user",   "content": user_msg}],
                    model, temperature=0.75, max_tokens=800,
                )
            except Exception as e:
                opinions[role] = f"[오류: {e}]"

        if parallel:
            threads = [threading.Thread(target=_ask, args=(r,)) for r in self.PERSONAS]
            for t in threads: t.start()
            for t in threads: t.join(timeout=60)
        else:
            for role in self.PERSONAS:
                _ask(role)

        # Synthesizer: 모든 의견 통합
        opinions_text = "\\n\\n".join(
            f"=== {role.upper()} ===\\n{text}"
            for role, text in opinions.items()
        )
        synth_model = self.models.get("synthesizer", self.models.get("engineer", ""))
        try:
            raw = self.nim.chat(
                [{"role": "system", "content": self.SYNTHESIZER_SYSTEM},
                 {"role": "user",   "content": f"주제: {topic}\n\n각 관점:\n{opinions_text}"}],
                synth_model, temperature=0.5, max_tokens=1200,
            )
            cleaned = NIMClient._extract_json(raw)
            synth = json.loads(cleaned)
            if not isinstance(synth, dict):
                raise ValueError("synthesis가 dict가 아님")
        except (json.JSONDecodeError, ValueError):
            synth = {"synthesis": opinions_text[:500], "key_insight": "", "next_action": "", "open_question": ""}
        except Exception:
            synth = {"synthesis": opinions_text[:500], "key_insight": "", "next_action": "", "open_question": ""}

        return {"opinions": opinions, "synthesis": synth}

    def print_council_report(self, result: Dict):
        print("\\n╔" + "═"*63 + "╗")
        print("║  🏛️  HYPERION COUNCIL DELIBERATION                           ║")
        print("╚" + "═"*63 + "╝")
        for role, opinion in result["opinions"].items():
            emoji = {"skeptic":"🔍","visionary":"🔭","engineer":"⚙️","theorist":"📐"}.get(role,"💬")
            print(f"\\n  {emoji} {role.upper()}:")
            for line in opinion[:300].splitlines()[:5]:
                print(f"    {line}")
        synth = result.get("synthesis", {})
        print("\\n  🌟 SYNTHESIS:")
        print(f"    {synth.get('synthesis','')[:400]}")
        print(f"\\n  ⚡ NEXT ACTION: {synth.get('next_action','')[:150]}")
        print(f"  ❓ OPEN QUESTION: {synth.get('open_question','')[:150]}")


# ═══════════════════════════════════════════════════════════════════════
#  HYPERION SELF-EVALUATION ENGINE — 자동 자기평가 + 품질 보증
# ═══════════════════════════════════════════════════════════════════════

class HyperionSelfEvaluator:
    """
    생성된 코드·이론·논문의 품질을 AI가 스스로 평가하는 자기평가 엔진.

    평가 차원:
    - Correctness  : 로직이 맞는가? 엣지케이스?
    - Novelty      : 기존과 얼마나 다른가?
    - Clarity      : 코드/글이 얼마나 명확한가?
    - Impact       : 인류 난제에 얼마나 기여하는가?
    - Reproducibility: 재현 가능한가?

    출력: 5차원 점수 (0~10) + 개선 제안 + 최종 판정
    """

    EVAL_SYSTEM = """당신은 NEXUS-HYPERION EVALUATOR v7: 세계 최고 수준의 AI 품질 감독관.
편견 없이 다음 5개 차원으로 평가하라 (각 0-10점):
- correctness : 논리/알고리즘/수학적 정확성
- novelty     : 기존 대비 독창성·혁신성
- clarity     : 가독성·명확성·문서화 품질
- impact      : 인류 또는 도메인 문제 해결 기여도
- reproducibility: 재현 가능성·테스트 가능성

JSON 형식으로만 반환:
{
  "scores": {"correctness": N, "novelty": N, "clarity": N, "impact": N, "reproducibility": N},
  "total": 평균,
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"],
  "improvements": ["개선1", "개선2", "개선3"],
  "verdict": "PUBLISH|REVISE|REJECT"
}"""

    def __init__(self, nim: "NIMClient", model: str):
        self.nim = nim
        self.model = model

    def evaluate(self, artifact: str, artifact_type: str = "code") -> Dict:
        """아티팩트 평가. artifact_type: 'code' | 'theory' | 'paper'"""
        messages = [
            {"role": "system", "content": self.EVAL_SYSTEM},
            {"role": "user", "content": (
                f"평가 대상 ({artifact_type}):\\n```\\n{artifact[:3000]}\\n```\\n\\n"
                "위 아티팩트를 5개 차원으로 엄밀하게 평가하라."
            )},
        ]
        try:
            raw = self.nim.chat(messages, self.model, temperature=0.2, max_tokens=1000)
            cleaned = NIMClient._extract_json(raw)
            result = json.loads(cleaned)
            if not isinstance(result, dict):
                raise ValueError(f"평가 결과가 dict가 아님: {type(result)}")
            return result
        except json.JSONDecodeError as e:
            return {"scores": {}, "total": 0, "verdict": "ERROR", "error": f"JSON 파싱 실패: {e}"}
        except Exception as e:
            return {"scores": {}, "total": 0, "verdict": "ERROR", "error": str(e)}

    def evaluate_step(self, step: "ResearchStep", result: "ExecutionResult") -> Dict:
        """스텝 결과 평가."""
        artifact = f"목표: {step.objective}\\n코드:\\n{step.code[:1500]}\\n출력:\\n{(result.stdout or '')[:800]}"
        return self.evaluate(artifact, "code")

    def print_eval_report(self, result: Dict, title: str = ""):
        scores = result.get("scores", {})
        total = result.get("total", sum(scores.values()) / max(len(scores), 1))
        verdict = result.get("verdict", "?")
        verdict_emoji = {"PUBLISH": "🟢", "REVISE": "🟡", "REJECT": "🔴"}.get(verdict, "⚪")
        print(f"\\n  📊 평가 결과 {f'— {title}' if title else ''}")
        print(f"  {'─'*50}")
        for dim, score in scores.items():
            bar = "█" * int(score) + "░" * (10 - int(score))
            print(f"  {dim:18s} [{bar}] {score:.1f}/10")
        print(f"  {'─'*50}")
        print(f"  종합 점수: {total:.1f}/10  판정: {verdict_emoji} {verdict}")
        for s in result.get("strengths", []):
            print(f"  ✅ {s[:80]}")
        for w in result.get("weaknesses", []):
            print(f"  ⚠️  {w[:80]}")
        for i in result.get("improvements", []):
            print(f"  💡 {i[:80]}")


# ═══════════════════════════════════════════════════════════════════════
#  HYPERION STREAMING LOGGER — 실시간 스트리밍 출력 + 구조화 로그
# ═══════════════════════════════════════════════════════════════════════

class HyperionStreamingLogger:
    """
    실행 중 모든 이벤트를 구조화된 JSONL 형식으로 기록하고
    실시간 대시보드를 터미널에 렌더링하는 로거.

    기능:
    - JSONL 이벤트 스트림 파일 저장
    - 실행 진행률 바 렌더링
    - 단계별 시간 추적
    - 에러 패턴 자동 분류
    - 세션 요약 HTML 자동 생성
    """

    EVENT_TYPES = {
        "SESSION_START", "SESSION_END",
        "STEP_START", "STEP_SUCCESS", "STEP_FAIL", "STEP_RETRY",
        "INSIGHT", "DISCOVERY", "THEORY", "PARADIGM_BREAK",
        "CHECKPOINT", "BENCHMARK", "EVAL",
    }

    def __init__(self, output_dir: Path, session_id: str):
        self.output_dir = output_dir
        self.session_id = session_id
        self.log_path = output_dir / f"nexus_log_{session_id}.jsonl"
        self.events: List[Dict] = []
        self.step_times: Dict[int, float] = {}
        self._session_start = time.time()

    def log(self, event_type: str, data: Dict):
        entry = {
            "ts": datetime.now().isoformat(),
            "elapsed": round(time.time() - self._session_start, 2),
            "type": event_type,
            "session": self.session_id,
            **data,
        }
        self.events.append(entry)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\\n")
        except Exception:
            pass

    def render_progress(self, current: int, total: int, title: str = "", success: bool = True):
        pct = current / max(total, 1)
        filled = int(40 * pct)
        bar = "█" * filled + "░" * (40 - filled)
        status = "✅" if success else "❌"
        elapsed = time.time() - self._session_start
        eta = (elapsed / max(current, 1)) * (total - current) if current > 0 else 0
        print(f"\\r  {status} [{bar}] {current}/{total} ({pct*100:.0f}%) "
              f"| {title[:30]:30s} | ⏱ {elapsed:.0f}s ETA {eta:.0f}s", end="", flush=True)
        if current >= total:
            print()

    def generate_html_report(self, memory: "ResearchMemory") -> str:
        """세션 결과를 HTML 리포트로 저장."""
        steps_html = ""
        for step in memory.completed_steps:
            status_color = "#2d9" if step.succeeded else "#d44"
            insights_html = "".join(f"<li>{i}</li>" for i in step.insights[:3])
            novel_html = "".join(f"<li>★ {n}</li>" for n in step.novel_findings[:2])
            steps_html += f"""
            <div class="step {'success' if step.succeeded else 'fail'}">
                <h3 style="color:{status_color}">
                    {'✅' if step.succeeded else '❌'} Step {step.id}: {step.title}
                    <small style="font-weight:normal;color:#888">
                        ({step.attempts} 시도 · {step.result.duration:.1f}s if step.result else "")
                    </small>
                </h3>
                <p><b>목표:</b> {step.objective[:200]}</p>
                <ul>{insights_html}</ul>
                <ul style="color:#f0a">{novel_html}</ul>
            </div>"""

        discoveries_html = "".join(f"<li>★ {d}</li>" for d in memory.novel_discoveries[:10])
        stats = memory.get_statistics()

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>NEXUS v7 — {memory.prompt[:60]}</title>
    <style>
        body{{background:#0d0d18;color:#e8e8f8;font-family:monospace;padding:2rem;}}
        h1{{color:#7af;}} h2{{color:#af7;border-bottom:1px solid #333;padding-bottom:.4rem;}}
        .step{{background:#111;border:1px solid #222;border-radius:6px;padding:1rem;margin:.6rem 0;}}
        .success{{border-left:3px solid #2d9;}} .fail{{border-left:3px solid #d44;}}
        .stat{{display:inline-block;background:#1a1a2e;padding:.4rem .8rem;
                border-radius:4px;margin:.2rem;color:#af7;}}
        ul{{color:#ccc;}} li{{margin:.2rem 0;}}
    </style>
</head>
<body>
    <h1>⚡ NEXUS v7 HYPERION — 연구 리포트</h1>
    <p style="color:#888">{datetime.now().strftime('%Y-%m-%d %H:%M')} · 세션 {self.session_id}</p>
    <h2>📋 연구 주제</h2>
    <p>{memory.prompt}</p>
    <h2>📊 통계</h2>
    <span class="stat">성공 {stats['succeeded']}/{stats['total_steps']}</span>
    <span class="stat">성공률 {stats['success_rate']}</span>
    <span class="stat">⏱ {stats['total_time']}</span>
    <span class="stat">💡 {stats['insights']} 인사이트</span>
    <span class="stat">🌟 {stats['novel_discoveries']} 발견</span>
    <h2>🌟 혁신적 발견</h2>
    <ul>{discoveries_html}</ul>
    <h2>🔬 단계별 결과</h2>
    {steps_html}
</body>
</html>"""

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"nexus_report_{ts}.html"
        path.write_text(html, encoding="utf-8")
        print(f"[StreamingLogger] HTML 리포트 저장: {path.name}")
        return str(path)


# ═══════════════════════════════════════════════════════════════════════
#  HYPERION AUTO-INSTALLER — 지능형 패키지 의존성 해결
# ═══════════════════════════════════════════════════════════════════════

class HyperionAutoInstaller:
    """
    에러 메시지에서 누락된 패키지를 자동 감지하고 설치하는 지능형 인스톨러.

    기능:
    - ImportError/ModuleNotFoundError 자동 파싱
    - 패키지명 자동 추론 (예: 'cv2' → 'opencv-python')
    - 버전 충돌 자동 해결 시도
    - 설치 결과 캐시 (재설치 방지)
    """

    # import명 → pip 패키지명 매핑
    IMPORT_TO_PKG: Dict[str, str] = {
        "cv2":           "opencv-python",
        "PIL":           "Pillow",
        "sklearn":       "scikit-learn",
        "skimage":       "scikit-image",
        "bs4":           "beautifulsoup4",
        "yaml":          "PyYAML",
        "dotenv":        "python-dotenv",
        "torch":         "torch",
        "torchvision":   "torchvision",
        "tensorflow":    "tensorflow",
        "tf":            "tensorflow",
        "xgboost":       "xgboost",
        "lightgbm":      "lightgbm",
        "catboost":      "catboost",
        "plotly":        "plotly",
        "bokeh":         "bokeh",
        "seaborn":       "seaborn",
        "statsmodels":   "statsmodels",
        "sympy":         "sympy",
        "networkx":      "networkx",
        "nltk":          "nltk",
        "spacy":         "spacy",
        "transformers":  "transformers",
        "datasets":      "datasets",
        "gym":           "gymnasium",
        "gymnasium":     "gymnasium",
        "optuna":        "optuna",
        "numba":         "numba",
        "cupy":          "cupy-cuda12x",
        "faiss":         "faiss-cpu",
    }

    def __init__(self):
        self._installed: set = set()
        self._failed: set = set()

    def extract_missing_package(self, error: str) -> Optional[str]:
        """에러 메시지에서 누락 패키지 추출."""
        patterns = [
            r"No module named \\'([\\w\\.]+)\\'",
            r"No module named \"([\\w\\.]+)\"",
            r"ImportError.*\\'([\\w]+)\\'",
            r"ModuleNotFoundError.*\\'([\\w\\.]+)\\'",
        ]
        for pat in patterns:
            m = re.search(pat, error)
            if m:
                raw = m.group(1).split(".")[0]
                return self.IMPORT_TO_PKG.get(raw, raw)
        return None

    def auto_fix(self, error: str) -> bool:
        """에러에서 패키지 추출 후 자동 설치. 성공 여부 반환."""
        pkg = self.extract_missing_package(error)
        if not pkg or pkg in self._installed or pkg in self._failed:
            return False
        print(f"  [AutoInstaller] 🔧 누락 패키지 감지: {pkg} → 자동 설치 중...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", pkg],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                self._installed.add(pkg)
                print(f"  [AutoInstaller] ✅ {pkg} 설치 완료")
                return True
            else:
                self._failed.add(pkg)
                print(f"  [AutoInstaller] ❌ {pkg} 설치 실패: {result.stderr[:200]}")
        except Exception as e:
            self._failed.add(pkg)
            print(f"  [AutoInstaller] ❌ 예외: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
#  HYPERION EXPERIMENT TRACKER — MLflow 스타일 실험 추적
# ═══════════════════════════════════════════════════════════════════════

class HyperionExperimentTracker:
    """
    MLflow 스타일의 실험 추적기.
    세션 간 하이퍼파라미터, 메트릭, 아티팩트를 추적합니다.

    기능:
    - run 단위 메트릭 로깅
    - 파라미터 비교 테이블
    - 최적 run 자동 선택
    - 실험 히스토리 시각화 코드 생성
    """

    TRACKER_FILE = Path.home() / ".nexus_experiments.json"

    def __init__(self):
        self._runs: List[Dict] = self._load()
        self._active_run: Optional[Dict] = None

    def _load(self) -> List[Dict]:
        try:
            if self.TRACKER_FILE.exists():
                return json.loads(self.TRACKER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save(self):
        try:
            self.TRACKER_FILE.write_text(
                json.dumps(self._runs, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    def start_run(self, name: str, params: Dict = None) -> str:
        run_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
        self._active_run = {
            "id": run_id, "name": name,
            "params": params or {},
            "metrics": {},
            "artifacts": [],
            "start_ts": datetime.now().isoformat(),
            "status": "RUNNING",
        }
        return run_id

    def log_metric(self, key: str, value: float, step: int = 0):
        if self._active_run:
            self._active_run["metrics"].setdefault(key, []).append({"step": step, "value": value})

    def log_param(self, key: str, value):
        if self._active_run:
            self._active_run["params"][key] = value

    def log_artifact(self, path: str):
        if self._active_run:
            self._active_run["artifacts"].append(path)

    def end_run(self, status: str = "FINISHED"):
        if self._active_run:
            self._active_run["status"] = status
            self._active_run["end_ts"] = datetime.now().isoformat()
            self._runs.append(self._active_run)
            self._save()
            self._active_run = None

    def best_run(self, metric: str, mode: str = "max") -> Optional[Dict]:
        """지정 메트릭 기준 최적 run 반환."""
        candidates = []
        for run in self._runs:
            vals = run.get("metrics", {}).get(metric, [])
            if vals:
                final_val = vals[-1]["value"]
                candidates.append((final_val, run))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=(mode == "max"))
        return candidates[0][1]

    def summary_table(self) -> str:
        """최근 실험 요약 테이블."""
        if not self._runs:
            return "[ExperimentTracker] 기록된 실험 없음"
        lines = [f"{'ID':8s} {'Name':20s} {'Status':10s} {'Metrics':30s}"]
        lines.append("─" * 70)
        for run in self._runs[-10:]:
            metric_str = ", ".join(
                f"{k}={v[-1]['value']:.3f}" if v else f"{k}=?"
                for k, v in list(run.get("metrics", {}).items())[:2]
            )
            lines.append(f"{run['id']:8s} {run['name'][:20]:20s} "
                         f"{run['status']:10s} {metric_str[:30]}")
        return "\\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def quick_research(
    prompt: str,
    api_key: str,
    steps: int = 10,
    mode: str = "innovate",
    creativity: float = 0.97,
    synthesize: bool = True,
) -> "ResearchMemory":
    """원라이너 혁신 연구 시작."""
    agent = NexusAgent(
        api_key=api_key,
        max_steps=steps,
        mode=mode,
        creativity_level=creativity,
        synthesize=synthesize,
    )
    return agent.run(prompt)


def resume_research(
    checkpoint_path: str,
    api_key: str,
    additional_steps: int = 10,
) -> "ResearchMemory":
    """중단된 연구 재시작."""
    mem, resume_from = ResearchMemory.load_checkpoint(checkpoint_path)
    agent = NexusAgent(
        api_key=api_key,
        max_steps=resume_from + additional_steps,
        resume_checkpoint=checkpoint_path,
    )
    return agent.run(mem.prompt)


def list_nim_models(api_key: str):
    """NIM에서 사용 가능한 모든 모델 출력."""
    registry = ModelRegistry(api_key, verbose=False)
    registry.print_available()


# ═══════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT — 터미널 기반 대화형 인터페이스
# ═══════════════════════════════════════════════════════════════════════

def _print_cli_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   ⚡ NEXUS Research Agent v7.0 — HYPERION Edition                    ║
║   🌍 인류 난제를 해결하는 천재 AI 에이전트 워크플로우               ║
║   🖥️  완전 로컬 터미널 CLI · Colab 중단점은 GPU 필요 시에만         ║
║   ☠️  DEMON Algorithm — 신랄한 비평·보강·불가능→가능 엔진            ║
╚══════════════════════════════════════════════════════════════════════╝
""")


def _interactive_cli():
    """대화형 CLI — 인수 없이 실행 시 사용"""
    _print_cli_banner()

    # API 키
    api_key = os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        print("  NVIDIA NIM API 키를 입력하세요.")
        print("  발급: https://build.nvidia.com")
        print()
        api_key = input("  API Key (nvapi-...): ").strip()
        if not api_key:
            print("  ❌ API 키가 필요합니다. 종료합니다.")
            sys.exit(1)

    # 연구 주제
    print()
    print("  연구 주제를 입력하세요.")
    print("  예시: '암 단백질 접힘 패턴에서 새로운 치료 표적 발견'")
    print("  예시: '기후변화 대응을 위한 탄소 포집 알고리즘 개발'")
    print("  예시: '세상에 없던 새로운 그래프 신경망 아키텍처 발명'")
    print()
    topic = input("  연구 주제: ").strip()
    if not topic:
        print("  ❌ 연구 주제가 필요합니다. 종료합니다.")
        sys.exit(1)

    # 모드 선택
    print()
    print("  연구 모드를 선택하세요 (기본: innovate):")
    for k, (label, desc) in RESEARCH_MODES.items():
        print(f"  [{k:10s}] {label:12s} — {desc[:55]}")
    print()
    mode_input = input("  모드 [innovate]: ").strip() or "innovate"
    if mode_input not in RESEARCH_MODES:
        print(f"  ⚠️  알 수 없는 모드 '{mode_input}', innovate 사용")
        mode_input = "innovate"

    # 단계 수
    steps_input = input("  최대 단계 수 [200]: ").strip() or "200"
    try:
        max_steps = int(steps_input)
    except ValueError:
        max_steps = 200

    print()
    print(f"  ✅ 설정 확인:")
    print(f"     주제  : {topic}")
    print(f"     모드  : {mode_input} ({RESEARCH_MODES[mode_input][0]})")
    print(f"     단계  : {max_steps}")
    print()
    print()
    print("  [고급 옵션]")
    use_council = input("  Multi-Agent Council 활성화? [y/N]: ").strip().lower() == "y"
    export_brain = input("  세션 후 Brain Markdown export? [y/N]: ").strip().lower() == "y"
    print()

    confirm = input("  시작하시겠습니까? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("  취소되었습니다.")
        sys.exit(0)

    print()
    agent = NexusAgent(
        api_key=api_key,
        max_steps=max_steps,
        mode=mode_input,
    )
    try:
        memory = agent.run(topic)
        if use_council and memory:
            print("\n  🏛️  Council 토론 실행 중...")
            agent.council_deliberate(topic, context=memory.get_context_for_next_step(500))
        if export_brain:
            agent.brain.export_markdown()
    except KeyboardInterrupt:
        print("\n\n  ⏸️  사용자 중단. 체크포인트가 저장되었습니다.")
        if agent.memory:
            path = agent.memory.save_checkpoint(len(agent.memory.completed_steps))
            print(f"  체크포인트: {path}")
            print(f"  재시작: python nexus_agent_v7.py --resume {path} -k <API_KEY>")


def _run_cli(args):
    """argparse 인수로 직접 실행"""
    _print_cli_banner()

    api_key = args.api_key or os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        print("  ❌ API 키가 필요합니다. -k 또는 환경변수 NVIDIA_API_KEY를 설정하세요.")
        sys.exit(1)

    if args.list_models:
        list_nim_models(api_key)
        return

    if not args.topic and not args.resume:
        print("  ❌ 연구 주제(-t)가 필요합니다.")
        sys.exit(1)

    if args.resume:
        print(f"  ♻️  체크포인트 복구: {args.resume}")
        try:
            resume_research(args.resume, api_key, additional_steps=args.steps)
        except KeyboardInterrupt:
            print("\n  ⏸️  중단됨.")
        return

    # --merge-brain: run 전에 처리
    if hasattr(args, "merge_brain") and args.merge_brain:
        brain = NexusBrain(verbose=True)
        brain.merge_from(args.merge_brain)
        if not args.topic and not args.resume:
            return

    agent = NexusAgent(
        api_key=api_key,
        max_steps=args.steps,
        mode=args.mode,
        creativity_level=args.creativity,
        synthesize=not args.no_synthesize,
        demon_enabled=not getattr(args, "no_demon", False),
        demon_max_iterations=getattr(args, "demon_iterations", 3),
        demon_on_steps=not getattr(args, "demon_only_plan", False),
        demon_on_plan=True,
    )
    try:
        memory = agent.run(args.topic)
        if hasattr(args, "council") and args.council and memory:
            print("\n  🏛️  Council 토론 실행 중...")
            agent.council_deliberate(args.topic, context=memory.get_context_for_next_step(500))
        if hasattr(args, "benchmark") and args.benchmark:
            agent.benchmark_all()
        if hasattr(args, "eval_paper") and args.eval_paper:
            papers = list(agent.output_dir.glob("nexus_paper_*.md"))
            if papers:
                agent.evaluate_paper(str(sorted(papers)[-1]))
        if hasattr(args, "export_brain") and args.export_brain:
            agent.brain.export_markdown()
    except KeyboardInterrupt:
        print("\n\n  ⏸️  사용자 중단.")
        if agent.memory:
            path = agent.memory.save_checkpoint(len(agent.memory.completed_steps))
            print(f"  체크포인트: {path}")
            print(f"  재시작: python nexus_agent_v7.py --resume {path} -k <API_KEY>")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="NEXUS Research Agent v7.0 — 인류 난제를 해결하는 천재 AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python nexus_agent_v7.py                          # 대화형 CLI
  python nexus_agent_v7.py -k nvapi-... -t "주제"   # 직접 실행
  python nexus_agent_v7.py -k nvapi-... -t "암 치료 알고리즘" -m grand -s 30
  python nexus_agent_v7.py -k nvapi-... --resume .nexus_checkpoints/ckpt_xxx.json
  python nexus_agent_v7.py -k nvapi-... --list-models

연구 모드:
  explore   자율 탐구      experiment  실험 설계
  innovate  혁신 탐색      invent      발명 창조
  theory    이론 창조      paper       논문 작성
  patent    발명 특허      grand       인류 난제 직접 공략
  build     프로젝트 빌드  analyze     데이터 분석
        """,
    )
    parser.add_argument("-k", "--api-key", metavar="KEY",
                        help="NVIDIA NIM API 키 (또는 환경변수 NVIDIA_API_KEY)")
    parser.add_argument("-t", "--topic", metavar="TOPIC",
                        help="연구 주제")
    parser.add_argument("-m", "--mode", default="innovate",
                        choices=list(RESEARCH_MODES.keys()),
                        help="연구 모드 (기본: innovate)")
    parser.add_argument("-s", "--steps", type=int, default=200,
                        help="최대 단계 수 (기본: 200)")
    parser.add_argument("-c", "--creativity", type=float, default=0.97,
                        help="창의성 수준 0.0~1.0 (기본: 0.97)")
    parser.add_argument("--resume", metavar="CHECKPOINT",
                        help="체크포인트 파일 경로로 연구 재시작")
    parser.add_argument("--no-synthesize", action="store_true",
                        help="논문/이론/README 생성 비활성화")
    parser.add_argument("--list-models", action="store_true",
                        help="사용 가능한 NIM 모델 목록 출력")
    parser.add_argument("--council", action="store_true",
                        help="완료 후 Multi-Agent Council 토론 실행")
    parser.add_argument("--export-brain", action="store_true",
                        help="완료 후 Brain을 Markdown으로 export")
    parser.add_argument("--benchmark", action="store_true",
                        help="완료 후 성공 스텝 전체 벤치마크 실행")
    parser.add_argument("--eval-paper", action="store_true",
                        help="완료 후 생성된 논문 자동 품질 평가")
    parser.add_argument("--merge-brain", metavar="BRAIN_PATH",
                        help="다른 Brain JSON 파일과 지식 병합")
    parser.add_argument("--no-demon", action="store_true",
                        help="DEMON 알고리즘 비활성화 (기본: 활성화)")
    parser.add_argument("--demon-iterations", type=int, default=3,
                        help="DEMON 자동 재이터레이션 최대 횟수 (기본: 3)")
    parser.add_argument("--demon-only-plan", action="store_true",
                        help="DEMON을 계획 단계에서만 실행 (스텝별 비평 생략)")

    # 인수 없이 실행 시 대화형 CLI
    if len(sys.argv) == 1:
        _interactive_cli()
    else:
        args = parser.parse_args()
        _run_cli(args)