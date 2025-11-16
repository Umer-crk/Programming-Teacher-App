import streamlit as st
import textwrap
import subprocess
import tempfile
import sys
import os

st.set_page_config(page_title="Code & Logic Teacher", layout="wide")

LESSONS = {
    "Python Basics": {
        "content": """
Python Basics: variables, types, control flow, functions.

Example:
""",
        "challenge": {
            "prompt": "Write a function `is_prime(n)` that returns True if n is prime and False otherwise.",
            "starter": "def is_prime(n):\n    # your code here\n    pass\n",
            "tests": [
                ("is_prime(2)", "True"),
                ("is_prime(15)", "False"),
                ("is_prime(17)", "True"),
            ],
            "solution": """
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True
""",
        },
    },
    "Logic Puzzles": {
        "content": """
Logic-building: boolean logic, truth tables, small puzzles.

Example: return True if exactly one of a,b is True (XOR).
""",
        "challenge": {
            "prompt": "Write `xor(a, b)` that returns True when exactly one is True.",
            "starter": "def xor(a, b):\n    # your code here\n    pass\n",
            "tests": [
                ("xor(True, False)", "True"),
                ("xor(True, True)", "False"),
                ("xor(False, False)", "False"),
            ],
            "solution": """
def xor(a, b):
    return (a and not b) or (b and not a)
""",
        },
    },
}

def run_python_code(code, timeout=5):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        name = f.name
        f.write(code)
    try:
        proc = subprocess.run(
            [sys.executable, name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        out = proc.stdout.decode()
        err = proc.stderr.decode()
    except subprocess.TimeoutExpired:
        out, err = "", "Execution timed out."
    finally:
        os.remove(name)
    return out, err

def grade(fn_code, tests):
    runner = fn_code + "\n\nif __name__ == '__main__':\n"
    for expr, _ in tests:
        runner += f"    try:\n        _r = {expr}\n        print(repr(_r))\n    except Exception as e:\n        print('<<ERROR>>'+str(e))\n"
    out, err = run_python_code(runner)
    lines = out.strip().splitlines()
    score, feedback = 0, []
    for (expr, expected), line in zip(tests, lines):
        if line.startswith("<<ERROR>>"):
            feedback.append(f"{expr} -> ERROR ({expected})")
        elif line == expected or line == repr(eval(expected)):
            feedback.append(f"{expr} -> PASS")
            score += 1
        else:
            feedback.append(f"{expr} -> FAIL (got {line}, expected {expected})")
    return score, feedback

st.title("🧠 Code & Logic Teacher")

language = st.sidebar.selectbox("Lesson", list(LESSONS.keys()))
lesson = LESSONS[language]

st.header(language)
st.markdown(lesson["content"])

st.subheader("Try it")
user_code = st.text_area("Your Code", lesson["challenge"]["starter"], height=250)

if st.button("Run ▶"):
    st.warning("This executes Python code on your machine. Avoid untrusted code.")
    out, err = run_python_code(user_code)
    if out:
        st.subheader("Output")
        st.code(out)
    if err:
        st.subheader("Errors")
        st.code(err)

st.subheader("Challenge")
st.write(lesson["challenge"]["prompt"])

if st.button("Run Tests"):
    score, fb = grade(user_code, lesson["challenge"]["tests"])
    st.success(f"Score: {score} / {len(fb)}")
    for line in fb:
        st.write(line)

if st.checkbox("Show Solution"):
    st.code(lesson["challenge"]["solution"])
