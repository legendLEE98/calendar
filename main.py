import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid
from datetime import datetime
import calendar

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

C = {
    "bg":       "#F0F2F5",
    "panel":    "#FFFFFF",
    "border":   "#DDE1E7",
    "primary":  "#3B82F6",
    "소비":     "#EF4444",
    "저축":     "#10B981",
    "text":     "#1E293B",
    "sub":      "#94A3B8",
    "today_bg": "#FEF9C3",
    "sel_bg":   "#3B82F6",
    "sun":      "#EF4444",
    "sat":      "#3B82F6",
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"transactions": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("가계부")
        self.root.geometry("1060x680")
        self.root.minsize(860, 580)
        self.root.configure(bg=C["bg"])

        self.data = load_data()
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.selected = now.strftime("%Y-%m-%d")

        self._build_layout()
        self._render_calendar()
        self._render_detail()

    # ─── Layout ───────────────────────────────────────────────────────────────

    def _build_layout(self):
        # Header
        hdr = tk.Frame(self.root, bg=C["primary"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="가계부", font=("맑은 고딕", 15, "bold"),
                 bg=C["primary"], fg="white").pack(side="left", padx=22, pady=14)
        self.lbl_hdr_sum = tk.Label(hdr, text="", font=("맑은 고딕", 10),
                                    bg=C["primary"], fg="#BFDBFE")
        self.lbl_hdr_sum.pack(side="right", padx=22)

        # Body
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=14)

        # Left panel – calendar
        self.frm_cal = tk.Frame(body, bg=C["panel"],
                                highlightbackground=C["border"], highlightthickness=1)
        self.frm_cal.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Right panel – detail (fixed width)
        self.frm_det = tk.Frame(body, bg=C["panel"], width=350,
                                highlightbackground=C["border"], highlightthickness=1)
        self.frm_det.pack(side="right", fill="y")
        self.frm_det.pack_propagate(False)

        self._build_cal_header()
        self._build_detail_panel()

    def _build_cal_header(self):
        nav = tk.Frame(self.frm_cal, bg=C["panel"])
        nav.pack(fill="x", padx=14, pady=12)

        btn_cfg = dict(font=("맑은 고딕", 13), bg=C["panel"], fg=C["text"],
                       relief="flat", bd=0, cursor="hand2",
                       activebackground=C["bg"])
        tk.Button(nav, text="◀", command=self._prev_month, **btn_cfg).pack(side="left")
        self.lbl_month = tk.Label(nav, text="", font=("맑은 고딕", 13, "bold"),
                                  bg=C["panel"], fg=C["text"])
        self.lbl_month.pack(side="left", padx=14)
        tk.Button(nav, text="▶", command=self._next_month, **btn_cfg).pack(side="left")

        tk.Button(nav, text="오늘", command=self._go_today,
                  font=("맑은 고딕", 9, "bold"), bg=C["primary"], fg="white",
                  relief="flat", bd=0, cursor="hand2", padx=10, pady=3,
                  activebackground="#2563EB").pack(side="right")

        # Day-of-week header
        dow = tk.Frame(self.frm_cal, bg=C["panel"])
        dow.pack(fill="x", padx=10, pady=(0, 4))
        labels = ["일", "월", "화", "수", "목", "금", "토"]
        fg_list = [C["sun"]] + [C["sub"]] * 5 + [C["sat"]]
        for i, (lbl, fg) in enumerate(zip(labels, fg_list)):
            dow.columnconfigure(i, weight=1)
            tk.Label(dow, text=lbl, font=("맑은 고딕", 9, "bold"),
                     bg=C["panel"], fg=fg).grid(row=0, column=i, pady=4)

        self.frm_grid = tk.Frame(self.frm_cal, bg=C["panel"])
        self.frm_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_detail_panel(self):
        pad = dict(padx=16)

        self.lbl_det_date = tk.Label(self.frm_det, text="날짜를 선택하세요",
                                     font=("맑은 고딕", 12, "bold"),
                                     bg=C["panel"], fg=C["text"])
        self.lbl_det_date.pack(anchor="w", pady=(16, 2), **pad)

        self.lbl_det_sum = tk.Label(self.frm_det, text="",
                                    font=("맑은 고딕", 9), bg=C["panel"], fg=C["sub"])
        self.lbl_det_sum.pack(anchor="w", **pad)

        ttk.Separator(self.frm_det).pack(fill="x", padx=16, pady=10)

        # Transaction list (scrollable)
        self.frm_txlist = tk.Frame(self.frm_det, bg=C["panel"])
        self.frm_txlist.pack(fill="both", expand=True, **pad)

        ttk.Separator(self.frm_det).pack(fill="x", padx=16, pady=10)

        # ── Add form ──────────────────────────────────────────────────────────
        frm_form = tk.Frame(self.frm_det, bg=C["panel"])
        frm_form.pack(fill="x", padx=16, pady=(0, 16))

        tk.Label(frm_form, text="새 항목 추가", font=("맑은 고딕", 10, "bold"),
                 bg=C["panel"], fg=C["text"]).pack(anchor="w", pady=(0, 8))

        # Type toggle
        tf = tk.Frame(frm_form, bg=C["panel"])
        tf.pack(fill="x", pady=(0, 8))
        self.tx_type = tk.StringVar(value="소비")
        self._btn_소비 = tk.Button(tf, text="소비", font=("맑은 고딕", 9, "bold"),
                                   bg=C["소비"], fg="white", relief="flat", bd=0,
                                   cursor="hand2", padx=14, pady=5,
                                   command=lambda: self._set_type("소비"))
        self._btn_소비.pack(side="left", padx=(0, 6))
        self._btn_저축 = tk.Button(tf, text="저축", font=("맑은 고딕", 9, "bold"),
                                   bg=C["border"], fg=C["text"], relief="flat", bd=0,
                                   cursor="hand2", padx=14, pady=5,
                                   command=lambda: self._set_type("저축"))
        self._btn_저축.pack(side="left")

        # Description
        tk.Label(frm_form, text="내용", font=("맑은 고딕", 8),
                 bg=C["panel"], fg=C["sub"]).pack(anchor="w", pady=(4, 2))
        self.ent_desc = tk.Entry(frm_form, font=("맑은 고딕", 10),
                                 relief="solid", bd=1,
                                 highlightcolor=C["primary"], highlightthickness=1)
        self.ent_desc.pack(fill="x", pady=(0, 6))
        self.ent_desc.bind("<Return>", lambda e: self.ent_amount.focus())

        # Amount
        tk.Label(frm_form, text="금액 (원)", font=("맑은 고딕", 8),
                 bg=C["panel"], fg=C["sub"]).pack(anchor="w", pady=(0, 2))
        self.ent_amount = tk.Entry(frm_form, font=("맑은 고딕", 10),
                                   relief="solid", bd=1,
                                   highlightcolor=C["primary"], highlightthickness=1)
        self.ent_amount.pack(fill="x", pady=(0, 10))
        self.ent_amount.bind("<Return>", lambda e: self._add_transaction())

        tk.Button(frm_form, text="＋  추가하기", command=self._add_transaction,
                  font=("맑은 고딕", 10, "bold"), bg=C["primary"], fg="white",
                  relief="flat", bd=0, cursor="hand2", pady=9,
                  activebackground="#2563EB").pack(fill="x")

    # ─── Calendar ─────────────────────────────────────────────────────────────

    def _render_calendar(self):
        for w in self.frm_grid.winfo_children():
            w.destroy()

        self.lbl_month.configure(text=f"{self.year}년 {self.month}월")
        self._update_header_sum()

        for c in range(7):
            self.frm_grid.columnconfigure(c, weight=1)

        today = datetime.now().strftime("%Y-%m-%d")
        weeks = calendar.monthcalendar(self.year, self.month)

        for r, week in enumerate(weeks):
            self.frm_grid.rowconfigure(r, weight=1)
            for c, day in enumerate(week):
                if day == 0:
                    tk.Frame(self.frm_grid, bg=C["panel"]).grid(
                        row=r, column=c, sticky="nsew", padx=2, pady=2)
                    continue

                date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                is_sel = date_str == self.selected
                is_today = date_str == today

                if is_sel:
                    bg = C["sel_bg"]
                elif is_today:
                    bg = C["today_bg"]
                else:
                    bg = C["panel"]

                cell = tk.Frame(self.frm_grid, bg=bg, cursor="hand2",
                                highlightbackground=C["border"], highlightthickness=1)
                cell.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

                # Day number color
                if is_sel:
                    num_fg = "white"
                elif c == 0:
                    num_fg = C["sun"]
                elif c == 6:
                    num_fg = C["sat"]
                else:
                    num_fg = C["text"]

                tk.Label(cell, text=str(day), font=("맑은 고딕", 10, "bold"),
                         bg=bg, fg=num_fg).pack(anchor="nw", padx=5, pady=(4, 0))

                소비, 저축 = self._day_sum(date_str)
                if 소비:
                    fg = "#FCA5A5" if is_sel else C["소비"]
                    tk.Label(cell, text=f"-{소비:,}", font=("맑은 고딕", 7),
                             bg=bg, fg=fg).pack(anchor="se", padx=4, pady=0)
                if 저축:
                    fg = "#6EE7B7" if is_sel else C["저축"]
                    tk.Label(cell, text=f"+{저축:,}", font=("맑은 고딕", 7),
                             bg=bg, fg=fg).pack(anchor="se", padx=4, pady=(0, 2))

                self._bind_cell(cell, date_str, bg)

    def _bind_cell(self, cell, date_str, orig_bg):
        hover_bg = "#DBEAFE" if orig_bg == C["panel"] else orig_bg

        def on_click(e):
            self.selected = date_str
            self._render_calendar()
            self._render_detail()

        def on_enter(e):
            if orig_bg == C["panel"]:
                cell.configure(bg=hover_bg)
                for w in cell.winfo_children():
                    w.configure(bg=hover_bg)

        def on_leave(e):
            if orig_bg == C["panel"]:
                cell.configure(bg=orig_bg)
                for w in cell.winfo_children():
                    w.configure(bg=orig_bg)

        for w in [cell] + list(cell.winfo_children()):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    # ─── Detail panel ─────────────────────────────────────────────────────────

    def _render_detail(self):
        if not self.selected:
            return

        dt = datetime.strptime(self.selected, "%Y-%m-%d")
        self.lbl_det_date.configure(
            text=f"{dt.year}년 {dt.month}월 {dt.day}일 ({['월','화','수','목','금','토','일'][dt.weekday()]})")

        소비, 저축 = self._day_sum(self.selected)
        parts = []
        if 소비:
            parts.append(f"소비  -{소비:,}원")
        if 저축:
            parts.append(f"저축  +{저축:,}원")
        self.lbl_det_sum.configure(text="  |  ".join(parts) if parts else "내역 없음")

        for w in self.frm_txlist.winfo_children():
            w.destroy()

        txs = [t for t in self.data["transactions"] if t["date"] == self.selected]

        if not txs:
            tk.Label(self.frm_txlist, text="이 날의 내역이 없습니다.",
                     font=("맑은 고딕", 9), bg=C["panel"], fg=C["sub"]).pack(pady=16)
            return

        # Scrollable list
        canvas = tk.Canvas(self.frm_txlist, bg=C["panel"], highlightthickness=0)
        sb = ttk.Scrollbar(self.frm_txlist, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=C["panel"])

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for tx in sorted(txs, key=lambda x: x.get("created_at", "")):
            self._tx_row(inner, tx)

    def _tx_row(self, parent, tx):
        color = C[tx["type"]]
        sign = "-" if tx["type"] == "소비" else "+"

        row = tk.Frame(parent, bg=C["bg"],
                       highlightbackground=C["border"], highlightthickness=1)
        row.pack(fill="x", pady=3)

        badge = tk.Label(row, text=tx["type"], font=("맑은 고딕", 8, "bold"),
                         bg=color, fg="white", padx=6, pady=3)
        badge.pack(side="left", padx=(6, 0), pady=6)

        tk.Label(row, text=tx.get("description", ""),
                 font=("맑은 고딕", 9), bg=C["bg"], fg=C["text"]).pack(
            side="left", padx=8)

        tk.Label(row, text=f"{sign}{tx['amount']:,}원",
                 font=("맑은 고딕", 9, "bold"), bg=C["bg"], fg=color).pack(
            side="right", padx=10)

        tk.Button(row, text="✕", font=("맑은 고딕", 8), bg=C["bg"], fg=C["sub"],
                  relief="flat", bd=0, cursor="hand2", pady=0,
                  command=lambda tid=tx["id"]: self._delete(tid)).pack(
            side="right", padx=(0, 4))

    # ─── Actions ──────────────────────────────────────────────────────────────

    def _set_type(self, t):
        self.tx_type.set(t)
        if t == "소비":
            self._btn_소비.configure(bg=C["소비"], fg="white")
            self._btn_저축.configure(bg=C["border"], fg=C["text"])
        else:
            self._btn_저축.configure(bg=C["저축"], fg="white")
            self._btn_소비.configure(bg=C["border"], fg=C["text"])

    def _add_transaction(self):
        if not self.selected:
            messagebox.showwarning("알림", "날짜를 먼저 선택하세요.")
            return

        desc = self.ent_desc.get().strip()
        raw = self.ent_amount.get().strip().replace(",", "")

        if not desc:
            messagebox.showwarning("알림", "내용을 입력하세요.")
            self.ent_desc.focus()
            return
        try:
            amount = int(raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("알림", "올바른 금액을 입력하세요. (양의 정수)")
            self.ent_amount.focus()
            return

        self.data["transactions"].append({
            "id": str(uuid.uuid4()),
            "date": self.selected,
            "type": self.tx_type.get(),
            "amount": amount,
            "description": desc,
            "created_at": datetime.now().isoformat(),
        })
        save_data(self.data)

        self.ent_desc.delete(0, "end")
        self.ent_amount.delete(0, "end")
        self.ent_desc.focus()

        self._render_calendar()
        self._render_detail()

    def _delete(self, tid):
        if not messagebox.askyesno("삭제 확인", "이 항목을 삭제하시겠습니까?"):
            return
        self.data["transactions"] = [
            t for t in self.data["transactions"] if t["id"] != tid
        ]
        save_data(self.data)
        self._render_calendar()
        self._render_detail()

    # ─── Navigation ───────────────────────────────────────────────────────────

    def _prev_month(self):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1
        self._render_calendar()

    def _go_today(self):
        now = datetime.now()
        self.year, self.month = now.year, now.month
        self.selected = now.strftime("%Y-%m-%d")
        self._render_calendar()
        self._render_detail()

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _day_sum(self, date_str):
        txs = [t for t in self.data["transactions"] if t["date"] == date_str]
        소비 = sum(t["amount"] for t in txs if t["type"] == "소비")
        저축 = sum(t["amount"] for t in txs if t["type"] == "저축")
        return 소비, 저축

    def _update_header_sum(self):
        prefix = f"{self.year}-{self.month:02d}-"
        txs = [t for t in self.data["transactions"] if t["date"].startswith(prefix)]
        소비 = sum(t["amount"] for t in txs if t["type"] == "소비")
        저축 = sum(t["amount"] for t in txs if t["type"] == "저축")
        parts = []
        if 소비:
            parts.append(f"소비  -{소비:,}원")
        if 저축:
            parts.append(f"저축  +{저축:,}원")
        self.lbl_hdr_sum.configure(
            text="  |  ".join(parts) if parts else f"{self.year}년 {self.month}월")


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.25)
    except Exception:
        pass
    app = BudgetApp(root)
    root.mainloop()
