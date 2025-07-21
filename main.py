import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime

# Глобальная переменная для хранения результатов
calc_data = {}


def calculate():
    global calc_data
    try:
        # === Получение данных из полей ввода ===
        C_акб = float(entry_C.get() or 130)
        U_акб = float(entry_U.get() or 24)
        N_акб = float(entry_N.get() or 2)
        dod = float(entry_DoD.get() or 85) / 100

        I_зар = float(entry_I_cc.get() or 40)
        U_cc = float(entry_U_cc.get() or 26.7)

        U_cv = float(entry_U_cv.get() or 26.75)
        I_cv = float(entry_I_cv.get() or 4)

        eta_inv = float(entry_eta.get() or 92) / 100
        q = float(entry_q.get() or 0.5)

        P_нагрузка = float(entry_P.get() or 170)

        # === РАСЧЁТЫ ===
        E_акб_общ = N_акб * C_акб * U_акб
        E_нужно = E_акб_общ * dod

        # Режим CC
        P_зар_cc = U_cc * I_зар
        t_зар_cc = (E_нужно * 0.6) / P_зар_cc
        P_потр_ген_cc = P_зар_cc / eta_inv

        # Режим CV
        P_зар_cv = U_cv * I_cv
        t_зар_cv = (E_нужно * 0.2) / P_зар_cv
        P_потр_ген_cv = P_зар_cv / eta_inv

        # Общее время и топливо
        t_зар_общ = t_зар_cc + t_зар_cv

        V_топливо_cc = t_зар_cc * (P_потр_ген_cc / 1000) * q
        V_топливо_cv = t_зар_cv * (P_потр_ген_cv / 1000) * q
        V_топливо_общ = V_топливо_cc + V_топливо_cv

        t_автономия = E_нужно / P_нагрузка

        # === Сохранение в переменные для графика и сохранения ===
        calc_data = {
            "Общая энергоёмкость АКБ": E_акб_общ,
            "Энергия для заряда (DoD)": E_нужно,
            "Мощность заряда (CC)": P_зар_cc,
            "Потребление от генератора (CC)": P_потр_ген_cc,
            "Время заряда (CC)": t_зар_cc,
            "Расход топлива (CC)": V_топливо_cc,
            "Мощность заряда (CV)": P_зар_cv,
            "Потребление от генератора (CV)": P_потр_ген_cv,
            "Время заряда (CV)": t_зар_cv,
            "Расход топлива (CV)": V_топливо_cv,
            "Общее время заряда": t_зар_общ,
            "Общий расход топлива": V_топливо_общ,
            "Время автономной работы": t_автономия
        }

        # === Вывод результатов ===
        result_text = (
            f"🔋 Общая энергоёмкость АКБ: {E_акб_общ:.0f} Вт·ч\n"
            f"⚡ Энергия для заряда (DoD={dod*100:.0f}%): {E_нужно:.0f} Вт·ч\n"
            f"--- 🔄 Режим CC ---\n"
            f"🔌 Мощность заряда (CC): {P_зар_cc:.0f} Вт\n"
            f"⚡ Потребление от генератора (CC): {P_потр_ген_cc:.0f} Вт\n"
            f"⏱️ Время заряда (CC): {t_зар_cc:.2f} ч\n"
            f"⛽ Расход топлива (CC): {V_топливо_cc:.2f} л\n"
            f"--- ⚡ Режим CV ---\n"
            f"🔌 Мощность заряда (CV): {P_зар_cv:.0f} Вт\n"
            f"⚡ Потребление от генератора (CV): {P_потр_ген_cv:.0f} Вт\n"
            f"⏱️ Время заряда (CV): {t_зар_cv:.2f} ч\n"
            f"⛽ Расход топлива (CV): {V_топливо_cv:.2f} л\n"
            f"--- 📊 ИТОГО ---\n"
            f"⏱️ Общее время заряда: {t_зар_общ:.2f} ч\n"
            f"⛽ Общий расход топлива: {V_топливо_общ:.2f} л\n"
            f"⏱️ Время автономной работы от АКБ: {t_автономия:.2f} ч"
        )

        result_label.config(text=result_text)

        # === Построение графика ===
        plot_charge_curve(t_зар_cc, t_зар_cv, U_cc, U_cv)

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа.")
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль. Проверьте значения КПД или тока.")


def plot_charge_curve(t_cc, t_cv, u_cc, u_cv):
    """Построение графика заряда АКБ"""
    # Очистка предыдущего графика
    for widget in plot_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)

    time_cc = [0, t_cc]
    voltage_cc = [22.5, u_cc]  # Напряжение растёт
    time_cv = [t_cc, t_cc + t_cv]
    voltage_cv = [u_cc, u_cv]  # Уровень

    ax.plot(time_cc, voltage_cc, label="CC режим", marker='o')
    ax.plot(time_cv, voltage_cv, label="CV режим", linestyle='--', marker='o')
    ax.set_title("Заряд АКБ (время vs напряжение)")
    ax.set_xlabel("Время (ч)")
    ax.set_ylabel("Напряжение (В)")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def save_to_file():
    """Сохранение результатов в файл"""
    if not calc_data:
        messagebox.showwarning("Предупреждение", "Нет данных для сохранения. Сначала выполните расчёт.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Текстовые файлы", "*.txt"),
                                                        ("CSV файлы", "*.csv")])
    if not file_path:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {**{"Дата и время": timestamp}, **calc_data}

    if file_path.endswith(".txt"):
        with open(file_path, "w", encoding="utf-8") as f:
            for key, value in data.items():
                f.write(f"{key}: {value:.2f}\n")
        messagebox.showinfo("Сохранено", f"Результаты сохранены в:\n{file_path}")

    elif file_path.endswith(".csv"):
        df = pd.DataFrame(list(data.items()), columns=["Параметр", "Значение"])
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Сохранено", f"Результаты сохранены в:\n{file_path}")


def on_exit():
    """Завершение работы приложения"""
    if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
        root.destroy()


# === GUI ===
root = tk.Tk()
root.title("🔋 Расчёт заряда АКБ — с графиком слева")
root.geometry("1000x700")
root.grid_rowconfigure(0, weight=1)  # для основного контента
root.grid_rowconfigure(1, weight=0)  # для графика
root.grid_rowconfigure(2, weight=0)  # для кнопок
root.grid_rowconfigure(3, weight=1)  # опционально
root.resizable(False, False)

# Обработчик закрытия окна
root.protocol("WM_DELETE_WINDOW", on_exit)

# === Разделение на левую и правую части ===
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(0, weight=1)

# === Левая часть — график ===
plot_frame = ttk.Frame(root, width=300, height=300)
plot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# === Правая часть — ввод данных ===
frame_input = ttk.Frame(root, padding=10)
frame_input.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# --- Поля ввода ---
ttk.Label(frame_input, text="🔋 Параметры АКБ").grid(row=0, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Ёмкость АКБ (А·ч)").grid(row=1, column=0, sticky="w")
entry_C = ttk.Entry(frame_input, width=10)
entry_C.insert(0, "130")
entry_C.grid(row=1, column=1)

ttk.Label(frame_input, text="Напряжение АКБ (В)").grid(row=2, column=0, sticky="w")
entry_U = ttk.Entry(frame_input, width=10)
entry_U.insert(0, "24")
entry_U.grid(row=2, column=1)

ttk.Label(frame_input, text="Количество АКБ").grid(row=3, column=0, sticky="w")
entry_N = ttk.Entry(frame_input, width=10)
entry_N.insert(0, "2")
entry_N.grid(row=3, column=1)

ttk.Label(frame_input, text="Глубина разряда (DoD, %)").grid(row=4, column=0, sticky="w")
entry_DoD = ttk.Entry(frame_input, width=10)
entry_DoD.insert(0, "85")
entry_DoD.grid(row=4, column=1)

# --- Заряд (CC) ---
ttk.Label(frame_input, text="🔄 Параметры заряда (CC)").grid(row=5, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Ток заряда (CC, А)").grid(row=6, column=0, sticky="w")
entry_I_cc = ttk.Entry(frame_input, width=10)
entry_I_cc.insert(0, "40")
entry_I_cc.grid(row=6, column=1)

ttk.Label(frame_input, text="Напряжение при CC (В)").grid(row=7, column=0, sticky="w")
entry_U_cc = ttk.Entry(frame_input, width=10)
entry_U_cc.insert(0, "26.7")
entry_U_cc.grid(row=7, column=1)

# --- Заряд (CV) ---
ttk.Label(frame_input, text="⚡ Параметры заряда (CV)").grid(row=8, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Напряжение при CV (В)").grid(row=9, column=0, sticky="w")
entry_U_cv = ttk.Entry(frame_input, width=10)
entry_U_cv.insert(0, "26.75")
entry_U_cv.grid(row=9, column=1)

ttk.Label(frame_input, text="Ток при CV (А)").grid(row=10, column=0, sticky="w")
entry_I_cv = ttk.Entry(frame_input, width=10)
entry_I_cv.insert(0, "4")
entry_I_cv.grid(row=10, column=1)

# --- Электропитание ---
ttk.Label(frame_input, text="🔌 Параметры электропитания").grid(row=11, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="КПД инвертора (%)").grid(row=12, column=0, sticky="w")
entry_eta = ttk.Entry(frame_input, width=10)
entry_eta.insert(0, "92")
entry_eta.grid(row=12, column=1)

ttk.Label(frame_input, text="Расход топлива (л/кВт·ч)").grid(row=13, column=0, sticky="w")
entry_q = ttk.Entry(frame_input, width=10)
entry_q.insert(0, "0.5")
entry_q.grid(row=13, column=1)

# --- Нагрузка ---
ttk.Label(frame_input, text="⏱️ Нагрузка").grid(row=14, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Мощность нагрузки (Вт)").grid(row=15, column=0, sticky="w")
entry_P = ttk.Entry(frame_input, width=10)
entry_P.insert(0, "170")
entry_P.grid(row=15, column=1)

# === Кнопки ===
btn_frame = ttk.Frame(root, padding=10)
btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

calc_button = ttk.Button(btn_frame, text="📊 Рассчитать", command=calculate)
calc_button.pack(side="left", padx=5)

save_button = ttk.Button(btn_frame, text="💾 Сохранить", command=save_to_file)
save_button.pack(side="left", padx=5)

exit_button = ttk.Button(btn_frame, text="🚪 Выход", command=on_exit)
exit_button.pack(side="left", padx=5)

# === Вывод результатов ===
result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), bg="white", anchor="nw", relief="sunken", padx=10, pady=10, wraplength=850)
result_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# === Запуск приложения ===
root.mainloop()