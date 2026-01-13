import streamlit as st
import pandas as pd

# -----------------------------
# Patient Task Class
# -----------------------------
class Patient:
    def __init__(self, pid, arrival, burst, emergency):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.emergency = emergency

        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None

# -----------------------------
# SRTF Scheduling Algorithm
# -----------------------------
def srtf_scheduling(patients):
    time = 0
    completed = 0
    n = len(patients)
    timeline = []
    log = []

    while completed < n:
        # Get arrived patients
        ready_queue = [
            p for p in patients
            if p.arrival <= time and p.remaining > 0
        ]

        if ready_queue:
            # Emergency patients get highest priority
            for p in ready_queue:
                if p.emergency:
                    p.remaining -= 0.0001

            # Select patient with shortest remaining time
            current = min(ready_queue, key=lambda x: x.remaining)

            if current.start_time is None:
                current.start_time = time
                current.response_time = time - current.arrival

            timeline.append(current.pid)
            current.remaining -= 1

            if current.emergency:
                log.append(f"🚨 Emergency Patient {current.pid} is being monitored")

            if current.remaining <= 0:
                current.completion_time = time + 1
                current.turnaround_time = current.completion_time - current.arrival
                current.waiting_time = current.turnaround_time - current.burst
                completed += 1
                log.append(f"✅ Monitoring Completed for Patient {current.pid}")

        else:
            timeline.append("Idle")

        time += 1

    return patients, timeline, log

# -----------------------------
# Streamlit GUI
# -----------------------------
st.set_page_config(page_title="Emergency Healthcare SRTF", layout="wide")

st.title("🩺 Emergency Healthcare Task Scheduling")
st.subheader("Preemptive SRTF Scheduling Simulation")

if "patients" not in st.session_state:
    st.session_state.patients = []

# -----------------------------
# Input Section
# -----------------------------
with st.sidebar:
    st.header("Add Patient Task")

    pid = st.text_input("Patient Name / ID")
    arrival = st.number_input("Arrival Time", min_value=0, step=1)
    burst = st.number_input("Monitoring Time (Burst)", min_value=1, step=1)
    emergency = st.checkbox("Emergency Patient")

    if st.button("Add Patient"):
        st.session_state.patients.append(
            Patient(pid, arrival, burst, emergency)
        )
        st.success(f"Patient {pid} added")

# -----------------------------
# Display Patients
# -----------------------------
st.subheader("📋 Patient Monitoring Tasks")

if st.session_state.patients:
    patient_table = pd.DataFrame([
        {
            "Patient ID": p.pid,
            "Arrival Time": p.arrival,
            "Burst Time": p.burst,
            "Emergency": "Yes" if p.emergency else "No"
        }
        for p in st.session_state.patients
    ])
    st.table(patient_table)

# -----------------------------
# Start Scheduling
# -----------------------------
if st.button("▶ Start Scheduling"):
    result, timeline, logs = srtf_scheduling(st.session_state.patients)

    st.subheader("⏱ Scheduling Timeline")
    st.write(timeline)

    st.subheader("📢 Execution Log")
    for msg in logs:
        st.write(msg)

    # -------------------------
    # Final Table
    # -------------------------
    st.subheader("📊 Final Scheduling Table")

    final_table = pd.DataFrame([
        {
            "Patient": p.pid,
            "Arrival": p.arrival,
            "Burst": p.burst,
            "Completion": p.completion_time,
            "Waiting Time": p.waiting_time,
            "Turnaround Time": p.turnaround_time,
            "Response Time": p.response_time,
            "Emergency": "Yes" if p.emergency else "No"
        }
        for p in result
    ])

    st.table(final_table)

    # -------------------------
    # Averages
    # -------------------------
    avg_response = sum(p.response_time for p in result) / len(result)
    avg_turnaround = sum(p.turnaround_time for p in result) / len(result)

    st.subheader("📈 Performance Metrics")
    st.write(f"**Average Response Time:** {avg_response:.2f}")
    st.write(f"**Average Turnaround Time:** {avg_turnaround:.2f}")
