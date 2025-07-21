import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime

# Глобальная переменная для хранения результатов
calc_data = {}

def calculate():
    """Рассчитывает параметры заряда АКБ и выводит результаты"""
    global calc_data
    try:
        # === Получение данных из полей ввода ===
        battery_capacity = float(entry_capacity.get() or 130)  # Ёмкость АКБ
        battery_voltage = float(entry_voltage.get() or 24)     # Напряжение АКБ
        battery_count = float(entry_count.get() or 2)          # Количество АКБ
        depth_of_discharge = float(entry_dod.get() or 85) / 100  # Глубина разряда
        charge_current_cc = float(entry_current_cc.get() or 40)  # Ток заряда (CC)
        charge_voltage_cc = float(entry_voltage_cc.get() or 26.7)  # Напряжение (CC)
        charge_voltage_cv = float(entry_voltage_cv.get() or 26.75)  # Напряжение (CV)
        charge_current_cv = float(entry_current_cv.get() or 4)  # Ток (CV)
        inverter_efficiency = float(entry_efficiency.get() or 92) / 100  # КПД инвертора
        fuel_consumption_rate = float(entry_fuel_rate.get() or 0.5)  # Расход топлива
        load_power = float(entry_load_power.get() or 170)  # Мощность нагрузки

        # === Расчёты ===
        total_energy = battery_count * battery_capacity * battery_voltage
        needed_energy = total_energy * depth_of_discharge

        # Режим CC
        power_charge_cc = charge_voltage_cc * charge_current_cc
        time_charge_cc = (needed_energy * 0.6) / power_charge_cc
        power_from_generator_cc = power_charge_cc / inverter_efficiency

        # Режим CV
        power_charge_cv = charge_voltage_cv * charge_current_cv
        time_charge_cv = (needed_energy * 0.2) / power_charge_cv
        power_from_generator_cv = power_charge_cv / inverter_efficiency

        # Общие параметры
        total_charge_time = time_charge_cc + time_charge_cv
        fuel_consumption_cc = time_charge_cc * (power_from_generator_cc / 1000) * fuel_consumption_rate * time_charge_cc
        fuel_consumption_cv = time_charge_cv * (power_from_generator_cv / 1000) * fuel_consumption_rate * time_charge_cv
        total_fuel_consumption = fuel_consumption_cc + fuel_consumption_cv
        autonomy_time = needed_energy / load_power

        # === Сохранение результатов для графика и вывода ===
        calc_data = {
            "Общая энергоёмкость АКБ (Вт·ч)": total_energy,
            "Энергия для заряда (DoD)": needed_energy,
            "Мощность заряда (CC)": power_charge_cc,
            "Потребление от генератора (CC)": power_from_generator_cc,
            "Время заряда (CC)": time_charge_cc,
            "Расход топлива (CC)": fuel_consumption_cc,
            "Мощность заряда (CV)": power_charge_cv,
            "Потребление от генератора (CV)": power_from_generator_cv,
            "Время заряда (CV)": time_charge_cv,
            "Расход топлива (CV)": fuel_consumption_cv,
            "Общее время заряда": total_charge_time,
            "Общий расход топлива": total_fuel_consumption,
            "Время автономии": autonomy_time,
        }

        # === Вывод результатов ===
        result_text = (
            f"🔋 Общая энергоёмкость АКБ: {total_energy:.0f} Вт·ч\n"
            f"⚡ Энергия для заряда (DoD={depth_of_discharge * 100:.0f}%): {needed_energy:.0f} Вт·ч\n"
            f"--- 🔄 Режим CC ---\n"
            f"🔌 Мощность заряда (CC): {power_charge_cc:.0f} Вт\n"
            f"⚡ Потребление от генератора (CC): {power_from_generator_cc:.0f} Вт\n"
            f"⏱️ Время заряда (CC): {time_charge_cc:.2f} ч\n"
            f"⛽ Расход топлива (CC): {fuel_consumption_cc:.2f} л\n"
            f"--- ⚡ Режим CV ---\n"
            f"🔌 Мощность заряда (CV): {power_charge_cv:.0f} Вт\n"
            f"⚡ Потребление от генератора (CV): {power_from_generator_cv:.0f} Вт\n"
            f"⏱️ Время заряда (CV): {time_charge_cv:.2f} ч\n"
            f"⛽ Расход топлива (CV): {fuel_consumption_cv:.2f} л\n"
            f"--- 📊 ИТОГО ---\n"
            f"⏱️ Общее время заряда: {total_charge_time:.2f} ч\n"
            f"⛽ Общий расход топлива: {total_fuel_consumption:.2f} л\n"
            f"⏱️ Время автономной работы: {autonomy_time:.2f} ч"
        )
        result_textbox.delete("1.0", tk.END)
        result_textbox.insert(tk.END, result_text)

        # === Построение графика ===
        plot_charge_curve(time_charge_cc, time_charge_cv, charge_voltage_cc, charge_voltage_cv)

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа.")
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль. Проверьте значения КПД или тока.")

def plot_charge_curve(time_cc, time_cv, voltage_cc, voltage_cv):
    """Построение графика заряда АКБ"""
    for widget in plot_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    time_cc_values = [0, time_cc]
    voltage_cc_values = [22.5, voltage_cc]
    time_cv_values = [time_cc, time_cc + time_cv]
    voltage_cv_values = [voltage_cc, voltage_cv]

    ax.plot(time_cc_values, voltage_cc_values, label="CC режим", marker="o")
    ax.plot(time_cv_values, voltage_cv_values, label="CV режим", linestyle="--", marker="o")
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

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[
        ("Текстовые файлы", "*.txt"),
        ("CSV файлы", "*.csv")
    ])

    if not file_path:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"Дата и время": timestamp, **calc_data}

    if file_path.endswith(".txt"):
        with open(file_path, "w", encoding="utf-8") as file:
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    file.write(f"{key}: {value:.2f}\n")
                else:
                    file.write(f"{key}: {value}\n")
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
root.title("🔋 Расчёт заряда АКБ")
root.geometry("1000x700")
root.resizable(False, False)

# Обработчик закрытия окна
root.protocol("WM_DELETE_WINDOW", on_exit)

# === Разделение на левую и правую части ===
root.grid_columnconfigure(0, weight=1)  # Левая часть — форма ввода
root.grid_columnconfigure(1, weight=2)  # Правая часть — график
root.grid_rowconfigure(0, weight=1)     # Форма и график
root.grid_rowconfigure(1, weight=0)     # Кнопки
root.grid_rowconfigure(2, weight=0)     # Результаты
root.grid_rowconfigure(3, weight=1)     # Пустое пространство внизу

# === Левая часть — ввод данных ===
frame_input = ttk.Frame(root, padding=10)
frame_input.grid(row=0, column=0, padx=10, pady=0, sticky="nsew")

# --- Поля ввода ---
ttk.Label(frame_input, text="🔋 Параметры АКБ").grid(row=0, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Ёмкость АКБ (А·ч)").grid(row=1, column=0, sticky="w")
entry_capacity = ttk.Entry(frame_input, width=10)
entry_capacity.insert(0, "130")
entry_capacity.grid(row=1, column=1)

ttk.Label(frame_input, text="Напряжение АКБ (В)").grid(row=2, column=0, sticky="w")
entry_voltage = ttk.Entry(frame_input, width=10)
entry_voltage.insert(0, "24")
entry_voltage.grid(row=2, column=1)

ttk.Label(frame_input, text="Количество АКБ").grid(row=3, column=0, sticky="w")
entry_count = ttk.Entry(frame_input, width=10)
entry_count.insert(0, "2")
entry_count.grid(row=3, column=1)

ttk.Label(frame_input, text="Глубина разряда (DoD, %)").grid(row=4, column=0, sticky="w")
entry_dod = ttk.Entry(frame_input, width=10)
entry_dod.insert(0, "85")
entry_dod.grid(row=4, column=1)

# --- Заряд (CC) ---
ttk.Label(frame_input, text="🔄 Параметры заряда (CC)").grid(row=5, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Ток заряда (CC, А)").grid(row=6, column=0, sticky="w")
entry_current_cc = ttk.Entry(frame_input, width=10)
entry_current_cc.insert(0, "40")
entry_current_cc.grid(row=6, column=1)

ttk.Label(frame_input, text="Напряжение при CC (В)").grid(row=7, column=0, sticky="w")
entry_voltage_cc = ttk.Entry(frame_input, width=10)
entry_voltage_cc.insert(0, "26.7")
entry_voltage_cc.grid(row=7, column=1)

# --- Заряд (CV) ---
ttk.Label(frame_input, text="⚡ Параметры заряда (CV)").grid(row=8, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Напряжение при CV (В)").grid(row=9, column=0, sticky="w")
entry_voltage_cv = ttk.Entry(frame_input, width=10)
entry_voltage_cv.insert(0, "26.75")
entry_voltage_cv.grid(row=9, column=1)

ttk.Label(frame_input, text="Ток при CV (А)").grid(row=10, column=0, sticky="w")
entry_current_cv = ttk.Entry(frame_input, width=10)
entry_current_cv.insert(0, "4")
entry_current_cv.grid(row=10, column=1)

# --- Электропитание ---
ttk.Label(frame_input, text="🔌 Параметры электропитания").grid(row=11, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="КПД инвертора (%)").grid(row=12, column=0, sticky="w")
entry_efficiency = ttk.Entry(frame_input, width=10)
entry_efficiency.insert(0, "92")
entry_efficiency.grid(row=12, column=1)

ttk.Label(frame_input, text="Расход топлива (л/кВт·ч)").grid(row=13, column=0, sticky="w")
entry_fuel_rate = ttk.Entry(frame_input, width=10)
entry_fuel_rate.insert(0, "0.5")
entry_fuel_rate.grid(row=13, column=1)

# --- Нагрузка ---
ttk.Label(frame_input, text="⏱️ Нагрузка").grid(row=14, column=0, sticky="w", pady=5)
ttk.Label(frame_input, text="Мощность нагрузки (Вт)").grid(row=15, column=0, sticky="w")
entry_load_power = ttk.Entry(frame_input, width=10)
entry_load_power.insert(0, "170")
entry_load_power.grid(row=15, column=1)

# === Кнопки ===
btn_frame = ttk.Frame(frame_input)
btn_frame.grid(row=16, column=0, columnspan=2, pady=10)

ttk.Button(btn_frame, text="📊 Рассчитать", command=calculate).pack(side="left", padx=5)
ttk.Button(btn_frame, text="💾 Сохранить", command=save_to_file).pack(side="left", padx=5)
ttk.Button(btn_frame, text="🚪 Выход", command=on_exit).pack(side="left", padx=5)

# === Правая часть — график ===
plot_frame = ttk.Frame(root, width=300, height=300)
plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
plot_frame.grid_propagate(False)

# === Вывод результатов с прокруткой ===
result_textbox = tk.Text(
    root,
    font=("Courier", 10),
    bg="white",
    wrap="word",
    padx=10,
    pady=10,
    height=12,
    relief="sunken"
)
result_textbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# === Прокрутка ===
scrollbar = ttk.Scrollbar(root, orient="vertical", command=result_textbox.yview)
scrollbar.grid(row=2, column=2, sticky="ns")
result_textbox.configure(yscrollcommand=scrollbar.set)

# === Запуск приложения ===
root.mainloop()