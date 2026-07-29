"""
==========================================================
Lab Auto Grader
Execution Engine
Part 1
==========================================================
"""

import os
import time
import shutil
import signal
import subprocess
import tempfile

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from .compiler import (
    CompilationResult,
    compile_source,
    cleanup_result,
    PYTHON,
    C,
    CPP,
    JAVA,
    JAVASCRIPT
)

# ==========================================================
# EXECUTION CONSTANTS
# ==========================================================

DEFAULT_TIME_LIMIT = 2          # seconds
DEFAULT_MEMORY_LIMIT = 256      # MB
DEFAULT_OUTPUT_LIMIT = 1024 * 1024   # 1 MB
DEFAULT_CPU_LIMIT = 1
DEFAULT_PROCESS_LIMIT = 20

# ==========================================================
# EXECUTION RESULT
# ==========================================================

@dataclass
class ExecutionResult:
    """
    Result returned after program execution.
    """

    success: bool = False

    language: str = ""

    stdout: str = ""

    stderr: str = ""

    return_code: int = -1

    verdict: str = "Pending"

    execution_time: float = 0.0

    memory_used: float = 0.0

    cpu_time: float = 0.0

    timed_out: bool = False

    runtime_error: bool = False

    output_limit_exceeded: bool = False

    executable: Optional[str] = None

    workdir: str = ""

    custom_input: str = ""

    compile_result: Optional[CompilationResult] = None


# ==========================================================
# VERDICTS
# ==========================================================

VERDICT_ACCEPTED = "Accepted"

VERDICT_RUNTIME_ERROR = "Runtime Error"

VERDICT_TIME_LIMIT = "Time Limit Exceeded"

VERDICT_MEMORY_LIMIT = "Memory Limit Exceeded"

VERDICT_COMPILATION_ERROR = "Compilation Error"

VERDICT_INTERNAL_ERROR = "Internal Error"

# ==========================================================
# EXECUTION COMMANDS
# ==========================================================

def execution_command(result: CompilationResult):

    if result.language == PYTHON:

        return [

            "python3",

            result.source_file

        ]

    if result.language == C:

        return [

            result.executable

        ]

    if result.language == CPP:

        return [

            result.executable

        ]

    if result.language == JAVA:

        return [

            "java",

            "-cp",

            result.workdir,

            "Main"

        ]

    if result.language == JAVASCRIPT:

        return [

            "node",

            result.source_file

        ]

    raise ValueError(

        f"Unsupported language: {result.language}"

    )


# ==========================================================
# OUTPUT VALIDATION
# ==========================================================

def output_size(output: str):

    return len(

        output.encode("utf-8")

    )


def output_limit_exceeded(output):

    return (

        output_size(output)

        >

        DEFAULT_OUTPUT_LIMIT

    )


# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_execution(result: ExecutionResult):

    if result.compile_result:

        cleanup_result(

            result.compile_result

        )


# ==========================================================
# HELPER
# ==========================================================

def create_execution_result(

    compile_result: CompilationResult

):

    return ExecutionResult(

        language=compile_result.language,

        executable=compile_result.executable,

        workdir=compile_result.workdir,

        compile_result=compile_result

    )
# ==========================================================
# PYTHON EXECUTION
# ==========================================================

def execute_python(
    compile_result: CompilationResult,
    custom_input: str = "",
    time_limit: int = DEFAULT_TIME_LIMIT
):
    """
    Execute a Python program.
    """

    result = create_execution_result(
        compile_result
    )

    command = execution_command(
        compile_result
    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            input=custom_input,

            capture_output=True,

            text=True,

            cwd=compile_result.workdir,

            timeout=time_limit

        )

        end = time.perf_counter()

        result.success = process.returncode == 0

        result.return_code = process.returncode

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.execution_time = round(
            end - start,
            4
        )

        result.custom_input = custom_input

        if output_limit_exceeded(
            result.stdout
        ):

            result.output_limit_exceeded = True

            result.success = False

            result.verdict = VERDICT_RUNTIME_ERROR

            return result

        if process.returncode == 0:

            result.verdict = VERDICT_ACCEPTED

        else:

            result.runtime_error = True

            result.verdict = VERDICT_RUNTIME_ERROR

        return result

    except subprocess.TimeoutExpired as e:

        result.execution_time = time_limit

        result.stdout = e.stdout or ""

        result.stderr = e.stderr or ""

        result.success = False

        result.timed_out = True

        result.verdict = VERDICT_TIME_LIMIT

        return result

    except Exception as e:

        result.success = False

        result.stderr = str(e)

        result.runtime_error = True

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# GENERIC EXECUTION WRAPPER
# ==========================================================

def execute_program(
    compile_result: CompilationResult,
    custom_input: str = "",
    time_limit: int = DEFAULT_TIME_LIMIT
):
    """
    Dispatch execution based on language.
    """

    if compile_result.language == PYTHON:

        return execute_python(

            compile_result,

            custom_input,

            time_limit

        )

    raise NotImplementedError(

        f"{compile_result.language} execution "

        "will be implemented in later parts."

    )


# ==========================================================
# SAFE EXECUTION
# ==========================================================

def safe_execute(
    compile_result: CompilationResult,
    custom_input: str = "",
    time_limit: int = DEFAULT_TIME_LIMIT
):
    """
    Execute safely without propagating exceptions.
    """

    try:

        return execute_program(

            compile_result,

            custom_input,

            time_limit

        )

    except Exception as e:

        result = create_execution_result(
            compile_result
        )

        result.success = False

        result.stderr = str(e)

        result.runtime_error = True

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# EXECUTION SUMMARY
# ==========================================================

def execution_summary(
    result: ExecutionResult
):
    """
    Convert execution result into a dictionary.
    """

    return {

        "language": result.language,

        "success": result.success,

        "verdict": result.verdict,

        "execution_time": result.execution_time,

        "return_code": result.return_code,

        "stdout": result.stdout,

        "stderr": result.stderr,

        "timed_out": result.timed_out,

        "runtime_error": result.runtime_error,

        "output_limit_exceeded":
            result.output_limit_exceeded

    }
# ==========================================================
# EXECUTABLE VALIDATION
# ==========================================================

def executable_ready(
    compile_result: CompilationResult
):
    """
    Verify executable exists.
    """

    if compile_result.language in (

        PYTHON,

        JAVASCRIPT

    ):

        return os.path.isfile(

            compile_result.source_file

        )

    return (

        compile_result.executable is not None

        and

        os.path.isfile(

            compile_result.executable

        )

    )


# ==========================================================
# C EXECUTION
# ==========================================================

def execute_c(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):

    result = create_execution_result(
        compile_result
    )

    if not executable_ready(
        compile_result
    ):

        result.verdict = VERDICT_COMPILATION_ERROR

        result.stderr = "Executable not found."

        return result

    command = execution_command(
        compile_result
    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            input=custom_input,

            capture_output=True,

            text=True,

            cwd=compile_result.workdir,

            timeout=time_limit

        )

        end = time.perf_counter()

        result.execution_time = round(

            end - start,

            4

        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.return_code = process.returncode

        result.success = (

            process.returncode == 0

        )

        result.custom_input = custom_input

        if output_limit_exceeded(
            result.stdout
        ):

            result.output_limit_exceeded = True

            result.success = False

            result.verdict = VERDICT_RUNTIME_ERROR

            return result

        if process.returncode == 0:

            result.verdict = VERDICT_ACCEPTED

        else:

            result.runtime_error = True

            result.verdict = VERDICT_RUNTIME_ERROR

        return result

    except subprocess.TimeoutExpired:

        result.timed_out = True

        result.execution_time = time_limit

        result.verdict = VERDICT_TIME_LIMIT

        return result

    except Exception as e:

        result.stderr = str(e)

        result.runtime_error = True

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# C++ EXECUTION
# ==========================================================

def execute_cpp(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):

    result = create_execution_result(
        compile_result
    )

    if not executable_ready(
        compile_result
    ):

        result.verdict = VERDICT_COMPILATION_ERROR

        result.stderr = "Executable not found."

        return result

    command = execution_command(
        compile_result
    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            input=custom_input,

            capture_output=True,

            text=True,

            cwd=compile_result.workdir,

            timeout=time_limit

        )

        end = time.perf_counter()

        result.execution_time = round(

            end - start,

            4

        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.return_code = process.returncode

        result.success = (

            process.returncode == 0

        )

        result.custom_input = custom_input

        if output_limit_exceeded(
            result.stdout
        ):

            result.output_limit_exceeded = True

            result.success = False

            result.verdict = VERDICT_RUNTIME_ERROR

            return result

        if process.returncode == 0:

            result.verdict = VERDICT_ACCEPTED

        else:

            result.runtime_error = True

            result.verdict = VERDICT_RUNTIME_ERROR

        return result

    except subprocess.TimeoutExpired:

        result.timed_out = True

        result.execution_time = time_limit

        result.verdict = VERDICT_TIME_LIMIT

        return result

    except Exception as e:

        result.stderr = str(e)

        result.runtime_error = True

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# UPDATE DISPATCHER
# ==========================================================

def execute_program(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):

    if compile_result.language == PYTHON:

        return execute_python(

            compile_result,

            custom_input,

            time_limit

        )

    if compile_result.language == C:

        return execute_c(

            compile_result,

            custom_input,

            time_limit

        )

    if compile_result.language == CPP:

        return execute_cpp(

            compile_result,

            custom_input,

            time_limit

        )

    raise NotImplementedError(

        f"{compile_result.language} execution "
        "not implemented."

    )
# ==========================================================
# JAVA EXECUTION
# ==========================================================

def execute_java(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):
    """
    Execute compiled Java program.
    """

    result = create_execution_result(
        compile_result
    )

    command = execution_command(
        compile_result
    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            input=custom_input,

            capture_output=True,

            text=True,

            cwd=compile_result.workdir,

            timeout=time_limit

        )

        end = time.perf_counter()

        result.execution_time = round(
            end - start,
            4
        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.return_code = process.returncode

        result.success = process.returncode == 0

        result.custom_input = custom_input

        if output_limit_exceeded(
            result.stdout
        ):

            result.output_limit_exceeded = True

            result.success = False

            result.verdict = VERDICT_RUNTIME_ERROR

            return result

        if process.returncode == 0:

            result.verdict = VERDICT_ACCEPTED

        else:

            result.runtime_error = True

            result.verdict = VERDICT_RUNTIME_ERROR

        return result

    except subprocess.TimeoutExpired:

        result.timed_out = True

        result.execution_time = time_limit

        result.verdict = VERDICT_TIME_LIMIT

        return result

    except Exception as e:

        result.stderr = str(e)

        result.runtime_error = True

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# JAVASCRIPT EXECUTION
# ==========================================================

def execute_javascript(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):
    """
    Execute JavaScript using Node.js.
    """

    result = create_execution_result(
        compile_result
    )

    command = execution_command(
        compile_result
    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            input=custom_input,

            capture_output=True,

            text=True,

            cwd=compile_result.workdir,

            timeout=time_limit

        )

        end = time.perf_counter()

        result.execution_time = round(
            end - start,
            4
        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.return_code = process.returncode

        result.success = process.returncode == 0

        result.custom_input = custom_input

        if output_limit_exceeded(
            result.stdout
        ):

            result.output_limit_exceeded = True

            result.success = False

            result.verdict = VERDICT_RUNTIME_ERROR

            return result

        if process.returncode == 0:

            result.verdict = VERDICT_ACCEPTED

        else:

            result.runtime_error = True

            result.verdict = VERDICT_RUNTIME_ERROR

        return result

    except subprocess.TimeoutExpired:

        result.timed_out = True

        result.execution_time = time_limit

        result.verdict = VERDICT_TIME_LIMIT

        return result

    except Exception as e:

        result.stderr = str(e)

        result.runtime_error = True

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# UPDATE EXECUTION DISPATCHER
# ==========================================================

def execute_program(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):
    """
    Universal execution dispatcher.
    """

    language = compile_result.language

    if language == PYTHON:

        return execute_python(
            compile_result,
            custom_input,
            time_limit
        )

    elif language == C:

        return execute_c(
            compile_result,
            custom_input,
            time_limit
        )

    elif language == CPP:

        return execute_cpp(
            compile_result,
            custom_input,
            time_limit
        )

    elif language == JAVA:

        return execute_java(
            compile_result,
            custom_input,
            time_limit
        )

    elif language == JAVASCRIPT:

        return execute_javascript(
            compile_result,
            custom_input,
            time_limit
        )

    result = create_execution_result(
        compile_result
    )

    result.success = False

    result.verdict = VERDICT_INTERNAL_ERROR

    result.stderr = (
        f"Unsupported language: {language}"
    )

    return result


# ==========================================================
# EXECUTION VALIDATION
# ==========================================================

def execution_success(
    result: ExecutionResult
):

    return (

        result.success

        and

        result.verdict == VERDICT_ACCEPTED

    )


def execution_failed(
    result: ExecutionResult
):

    return not execution_success(result)


# ==========================================================
# EXECUTION INFORMATION
# ==========================================================

def execution_info(
    result: ExecutionResult
):

    return {

        "language": result.language,

        "verdict": result.verdict,

        "execution_time": result.execution_time,

        "memory_used": result.memory_used,

        "return_code": result.return_code,

        "stdout": result.stdout,

        "stderr": result.stderr

    }
# ==========================================================
# DOCKER EXECUTION (PLACEHOLDER)
# ==========================================================

def execute_in_docker(
    compile_result: CompilationResult,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT,
    memory_limit=DEFAULT_MEMORY_LIMIT
):
    """
    Execute inside Docker sandbox.

    NOTE:
    Replace this implementation after
    docker_runner.py is completed.
    """

    return execute_program(
        compile_result,
        custom_input,
        time_limit
    )


# ==========================================================
# MEMORY LIMIT
# ==========================================================

def check_memory_limit(
    result: ExecutionResult,
    memory_limit=DEFAULT_MEMORY_LIMIT
):
    """
    Check memory usage.
    """

    if result.memory_used > memory_limit:

        result.success = False

        result.verdict = VERDICT_MEMORY_LIMIT

        return False

    return True


# ==========================================================
# CPU LIMIT
# ==========================================================

def check_cpu_limit(
    result: ExecutionResult,
    cpu_limit=DEFAULT_CPU_LIMIT
):
    """
    Validate CPU usage.
    """

    if result.cpu_time > cpu_limit:

        result.success = False

        result.verdict = VERDICT_TIME_LIMIT

        return False

    return True


# ==========================================================
# PROCESS LIMIT
# ==========================================================

def check_process_limit(
    process_count,
    process_limit=DEFAULT_PROCESS_LIMIT
):
    """
    Validate child process count.
    """

    return process_count <= process_limit


# ==========================================================
# RUNTIME VALIDATION
# ==========================================================

def validate_execution(
    result: ExecutionResult,
    memory_limit=DEFAULT_MEMORY_LIMIT,
    cpu_limit=DEFAULT_CPU_LIMIT
):
    """
    Validate execution statistics.
    """

    check_memory_limit(

        result,

        memory_limit

    )

    check_cpu_limit(

        result,

        cpu_limit

    )

    return result


# ==========================================================
# EXECUTE & VALIDATE
# ==========================================================

def execute_and_validate(
    compile_result,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT,
    memory_limit=DEFAULT_MEMORY_LIMIT
):

    result = execute_program(

        compile_result,

        custom_input,

        time_limit

    )

    validate_execution(

        result,

        memory_limit

    )

    return result


# ==========================================================
# SANDBOX EXECUTION
# ==========================================================

class SandboxExecutor:
    """
    Execution wrapper.
    Docker support can later replace
    execute_program().
    """

    def __init__(
        self,
        time_limit=DEFAULT_TIME_LIMIT,
        memory_limit=DEFAULT_MEMORY_LIMIT
    ):

        self.time_limit = time_limit

        self.memory_limit = memory_limit

    def execute(
        self,
        compile_result,
        custom_input=""
    ):

        return execute_and_validate(

            compile_result,

            custom_input,

            self.time_limit,

            self.memory_limit

        )


# ==========================================================
# EXECUTION CONTEXT
# ==========================================================

class ExecutionContext:

    def __init__(
        self,
        compile_result,
        custom_input=""
    ):

        self.compile_result = compile_result

        self.custom_input = custom_input

        self.result = None

    def __enter__(self):

        self.result = execute_program(

            self.compile_result,

            self.custom_input

        )

        return self.result

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):

        cleanup_execution(

            self.result

        )

        return False


# ==========================================================
# BENCHMARK
# ==========================================================

def benchmark_execution(
    compile_result,
    runs=5
):

    execution_times = []

    for _ in range(runs):

        result = execute_program(

            compile_result

        )

        execution_times.append(

            result.execution_time

        )

    return {

        "runs": runs,

        "average_execution_time":

            round(

                sum(execution_times) /

                len(execution_times),

                4

            ),

        "minimum":

            min(execution_times),

        "maximum":

            max(execution_times)

    }
# ==========================================================
# EXECUTION LOGGER
# ==========================================================

import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def log_execution(result: ExecutionResult):
    """
    Log execution result.
    """

    if result.success:

        logger.info(

            "Execution Successful | "
            "Language=%s | "
            "Time=%.4fs | "
            "Verdict=%s",

            result.language,

            result.execution_time,

            result.verdict

        )

    else:

        logger.error(

            "Execution Failed | "
            "Language=%s | "
            "Verdict=%s | "
            "Error=%s",

            result.language,

            result.verdict,

            result.stderr

        )


# ==========================================================
# AUDIT LOG
# ==========================================================

def execution_audit(
    result: ExecutionResult
):
    """
    Return execution audit information.
    """

    return {

        "language":

            result.language,

        "verdict":

            result.verdict,

        "success":

            result.success,

        "execution_time":

            result.execution_time,

        "memory_used":

            result.memory_used,

        "cpu_time":

            result.cpu_time,

        "return_code":

            result.return_code,

        "stdout_size":

            len(result.stdout),

        "stderr_size":

            len(result.stderr),

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# EXPORT EXECUTION LOG
# ==========================================================

def export_execution_log(
    result: ExecutionResult,
    filepath
):
    """
    Save execution log as JSON.
    """

    with open(

        filepath,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            execution_audit(result),

            fp,

            indent=4

        )

    return filepath


# ==========================================================
# RUNTIME DIAGNOSTICS
# ==========================================================

def runtime_diagnostics(
    result: ExecutionResult
):
    """
    Generate runtime diagnostics.
    """

    return {

        "execution_time":

            result.execution_time,

        "memory_used":

            result.memory_used,

        "cpu_time":

            result.cpu_time,

        "timed_out":

            result.timed_out,

        "runtime_error":

            result.runtime_error,

        "output_limit_exceeded":

            result.output_limit_exceeded,

        "return_code":

            result.return_code

    }


# ==========================================================
# PERFORMANCE GRADE
# ==========================================================

def execution_grade(
    result: ExecutionResult
):

    t = result.execution_time

    if t <= 0.20:

        return "Excellent"

    elif t <= 0.50:

        return "Very Good"

    elif t <= 1.00:

        return "Good"

    elif t <= 2.00:

        return "Average"

    return "Slow"


# ==========================================================
# EXECUTION REPORT
# ==========================================================

def execution_report(
    result: ExecutionResult
):
    """
    Complete execution report.
    """

    return {

        "audit":

            execution_audit(result),

        "diagnostics":

            runtime_diagnostics(result),

        "grade":

            execution_grade(result)

    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

def executor_health():
    """
    Check execution environment.
    """

    return {

        "python":

            shutil.which("python3") is not None,

        "gcc":

            shutil.which("gcc") is not None,

        "g++":

            shutil.which("g++") is not None,

        "java":

            shutil.which("java") is not None,

        "node":

            shutil.which("node") is not None,

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# SAFE CLEANUP
# ==========================================================

def cleanup_execution_resources(
    result: ExecutionResult
):
    """
    Cleanup execution workspace.
    """

    try:

        cleanup_execution(result)

    except Exception:

        pass


# ==========================================================
# EXECUTE WITH LOGGING
# ==========================================================

def execute_with_logging(
    compile_result,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):
    """
    Execute and log automatically.
    """

    result = execute_program(

        compile_result,

        custom_input,

        time_limit

    )

    log_execution(result)

    return result
# ==========================================================
# BATCH EXECUTION
# ==========================================================

from concurrent.futures import ThreadPoolExecutor, as_completed


def execute_batch(
    compilation_results,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT,
    max_workers=4
):
    """
    Execute multiple compiled programs in parallel.
    """

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = [

            executor.submit(

                execute_with_logging,

                compile_result,

                custom_input,

                time_limit

            )

            for compile_result in compilation_results

        ]

        for future in as_completed(futures):

            try:

                results.append(

                    future.result()

                )

            except Exception as e:

                failed = ExecutionResult(

                    success=False,

                    verdict=VERDICT_INTERNAL_ERROR,

                    stderr=str(e)

                )

                results.append(failed)

    return results


# ==========================================================
# EXECUTION STATISTICS
# ==========================================================

def execution_statistics(results):
    """
    Aggregate execution statistics.
    """

    total = len(results)

    accepted = sum(

        1

        for r in results

        if r.verdict == VERDICT_ACCEPTED

    )

    runtime_errors = sum(

        1

        for r in results

        if r.verdict == VERDICT_RUNTIME_ERROR

    )

    time_limits = sum(

        1

        for r in results

        if r.verdict == VERDICT_TIME_LIMIT

    )

    internal_errors = sum(

        1

        for r in results

        if r.verdict == VERDICT_INTERNAL_ERROR

    )

    average_time = 0

    if total:

        average_time = round(

            sum(

                r.execution_time

                for r in results

            ) / total,

            4

        )

    return {

        "total": total,

        "accepted": accepted,

        "runtime_errors": runtime_errors,

        "time_limit_exceeded": time_limits,

        "internal_errors": internal_errors,

        "average_execution_time": average_time

    }


# ==========================================================
# EXECUTION BENCHMARK
# ==========================================================

def benchmark_program(
    compile_result,
    custom_input="",
    runs=10
):
    """
    Benchmark one compiled program.
    """

    timings = []

    verdict = None

    for _ in range(runs):

        result = execute_program(

            compile_result,

            custom_input

        )

        timings.append(

            result.execution_time

        )

        verdict = result.verdict

    return {

        "runs": runs,

        "minimum": round(min(timings), 4),

        "maximum": round(max(timings), 4),

        "average": round(

            sum(timings) / len(timings),

            4

        ),

        "verdict": verdict

    }


# ==========================================================
# RETRY EXECUTION
# ==========================================================

def retry_execution(
    compile_result,
    custom_input="",
    retries=3
):
    """
    Retry execution if an internal error occurs.
    """

    last_result = None

    for _ in range(retries):

        last_result = execute_program(

            compile_result,

            custom_input

        )

        if last_result.success:

            return last_result

        if last_result.verdict != VERDICT_INTERNAL_ERROR:

            return last_result

    return last_result


# ==========================================================
# PERFORMANCE MONITOR
# ==========================================================

def performance_monitor(results):
    """
    Performance monitoring summary.
    """

    if not results:

        return {}

    fastest = min(

        results,

        key=lambda x: x.execution_time

    )

    slowest = max(

        results,

        key=lambda x: x.execution_time

    )

    return {

        "fastest_execution":

            fastest.execution_time,

        "slowest_execution":

            slowest.execution_time,

        "fastest_language":

            fastest.language,

        "slowest_language":

            slowest.language

    }


# ==========================================================
# FILTER RESULTS
# ==========================================================

def filter_results(
    results,
    verdict
):
    """
    Filter execution results by verdict.
    """

    return [

        r

        for r in results

        if r.verdict == verdict

    ]


# ==========================================================
# SUCCESS RATE
# ==========================================================

def success_rate(results):
    """
    Calculate execution success percentage.
    """

    if not results:

        return 0.0

    success = sum(

        1

        for r in results

        if r.success

    )

    return round(

        (success / len(results)) * 100,

        2

    )


# ==========================================================
# EXECUTION SCORE
# ==========================================================

def execution_score(result):
    """
    Generate execution score out of 100.
    """

    if result.verdict != VERDICT_ACCEPTED:

        return 0

    score = 100

    if result.execution_time > 1:

        score -= 10

    if result.execution_time > 2:

        score -= 20

    if result.memory_used > 128:

        score -= 10

    return max(score, 0)
# ==========================================================
# DOCKER SANDBOX SUPPORT
# ==========================================================

import tempfile
import uuid


class DockerSandbox:
    """
    Docker sandbox configuration.

    NOTE:
    This class prepares Docker execution.
    Actual docker commands should be implemented
    in docker_runner.py.
    """

    def __init__(
        self,
        image="python:3.11-slim",
        memory_limit="256m",
        cpu_limit=1,
        network_disabled=True
    ):

        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.network_disabled = network_disabled

        self.container_name = (
            f"judge_{uuid.uuid4().hex}"
        )

    def docker_command(
        self,
        host_directory,
        command
    ):

        docker = [

            "docker",

            "run",

            "--rm",

            "--name",

            self.container_name,

            "--memory",

            self.memory_limit,

            "--cpus",

            str(self.cpu_limit)

        ]

        if self.network_disabled:

            docker.extend(

                [

                    "--network",

                    "none"

                ]

            )

        docker.extend(

            [

                "-v",

                f"{host_directory}:/workspace",

                "-w",

                "/workspace",

                self.image

            ]

        )

        docker.extend(command)

        return docker


# ==========================================================
# DOCKER EXECUTION
# ==========================================================

def execute_in_docker(
    compile_result,
    custom_input="",
    time_limit=DEFAULT_TIME_LIMIT
):
    """
    Execute inside Docker.

    docker_runner.py should later replace
    this implementation.
    """

    sandbox = DockerSandbox()

    command = execution_command(
        compile_result
    )

    docker_command = sandbox.docker_command(

        compile_result.workdir,

        command

    )

    result = create_execution_result(
        compile_result
    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            docker_command,

            input=custom_input,

            capture_output=True,

            text=True,

            timeout=time_limit

        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.return_code = process.returncode

        result.execution_time = round(

            time.perf_counter() - start,

            4

        )

        result.success = (

            process.returncode == 0

        )

        result.verdict = (

            VERDICT_ACCEPTED

            if result.success

            else VERDICT_RUNTIME_ERROR

        )

        return result

    except subprocess.TimeoutExpired:

        result.timed_out = True

        result.verdict = VERDICT_TIME_LIMIT

        return result

    except Exception as e:

        result.stderr = str(e)

        result.verdict = VERDICT_INTERNAL_ERROR

        return result


# ==========================================================
# MEMORY MONITOR
# ==========================================================

def monitor_memory(
    result,
    limit=DEFAULT_MEMORY_LIMIT
):

    if result.memory_used > limit:

        result.success = False

        result.verdict = VERDICT_MEMORY_LIMIT

    return result


# ==========================================================
# PROCESS ISOLATION
# ==========================================================

def isolated_execution(
    compile_result,
    custom_input=""
):
    """
    Execute inside Docker sandbox.
    """

    result = execute_in_docker(

        compile_result,

        custom_input

    )

    return monitor_memory(result)


# ==========================================================
# SECURITY VALIDATION
# ==========================================================

FORBIDDEN_MODULES = {

    "socket",

    "requests",

    "urllib",

    "subprocess",

    "multiprocessing",

    "threading",

    "asyncio"

}


def security_check(source_code):

    detected = []

    lower = source_code.lower()

    for module in FORBIDDEN_MODULES:

        if module in lower:

            detected.append(module)

    return {

        "safe":

            len(detected) == 0,

        "detected":

            detected

    }


# ==========================================================
# SANDBOX REPORT
# ==========================================================

def sandbox_report(result):

    return {

        "verdict":

            result.verdict,

        "execution_time":

            result.execution_time,

        "memory_used":

            result.memory_used,

        "success":

            result.success,

        "timed_out":

            result.timed_out

    }


# ==========================================================
# EXECUTION PIPELINE
# ==========================================================

def execute_secure(
    compile_result,
    source_code,
    custom_input=""
):
    """
    Secure execution pipeline.
    """

    report = security_check(
        source_code
    )

    if not report["safe"]:

        result = create_execution_result(
            compile_result
        )

        result.success = False

        result.stderr = (

            "Forbidden modules detected."

        )

        result.verdict = VERDICT_RUNTIME_ERROR

        return result

    return isolated_execution(

        compile_result,

        custom_input

    )
# ==========================================================
# EXECUTION AUDIT
# ==========================================================

import hashlib
import json
from datetime import datetime


def execution_id(result: ExecutionResult):
    """
    Generate unique execution ID.
    """

    data = (

        f"{result.language}"

        f"{result.execution_time}"

        f"{datetime.utcnow()}"

    )

    return hashlib.sha256(

        data.encode("utf-8")

    ).hexdigest()


# ==========================================================
# EXECUTION AUDIT REPORT
# ==========================================================

def execution_audit_report(
    result: ExecutionResult
):

    return {

        "execution_id":

            execution_id(result),

        "language":

            result.language,

        "verdict":

            result.verdict,

        "success":

            result.success,

        "return_code":

            result.return_code,

        "execution_time":

            result.execution_time,

        "memory_used":

            result.memory_used,

        "cpu_time":

            result.cpu_time,

        "timed_out":

            result.timed_out,

        "runtime_error":

            result.runtime_error,

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# EXPORT AUDIT
# ==========================================================

def export_execution_report(
    result: ExecutionResult,
    filename
):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            execution_audit_report(result),

            fp,

            indent=4

        )

    return filename


# ==========================================================
# EXECUTION DIAGNOSTICS
# ==========================================================

def diagnostics(result: ExecutionResult):

    return {

        "execution":

            execution_summary(result),

        "audit":

            execution_audit_report(result),

        "sandbox":

            sandbox_report(result)

    }


# ==========================================================
# PERFORMANCE SCORE
# ==========================================================

def performance_score(
    result: ExecutionResult
):

    score = 100

    if result.verdict != VERDICT_ACCEPTED:

        return 0

    if result.execution_time > 0.5:

        score -= 5

    if result.execution_time > 1:

        score -= 10

    if result.execution_time > 2:

        score -= 20

    if result.memory_used > 128:

        score -= 10

    if result.memory_used > 200:

        score -= 10

    return max(

        score,

        0

    )


# ==========================================================
# EXECUTION HISTORY
# ==========================================================

class ExecutionHistory:

    def __init__(self):

        self.history = []

    def add(

        self,

        result

    ):

        self.history.append(

            result

        )

    def latest(self):

        if not self.history:

            return None

        return self.history[-1]

    def clear(self):

        self.history.clear()

    def statistics(self):

        return execution_statistics(

            self.history

        )


# ==========================================================
# BENCHMARK SUITE
# ==========================================================

class BenchmarkSuite:

    def __init__(self):

        self.results = []

    def add(

        self,

        result

    ):

        self.results.append(

            result

        )

    def average(self):

        if not self.results:

            return 0

        return round(

            sum(

                r.execution_time

                for r in self.results

            ) /

            len(self.results),

            4

        )

    def report(self):

        return {

            "runs":

                len(

                    self.results

                ),

            "average":

                self.average(),

            "statistics":

                execution_statistics(

                    self.results

                )

        }


# ==========================================================
# EXECUTION METADATA
# ==========================================================

def executor_metadata():

    return {

        "name":

            "Lab Auto Grader Executor",

        "version":

            "1.0.0",

        "supported_languages": [

            PYTHON,

            C,

            CPP,

            JAVA,

            JAVASCRIPT

        ],

        "default_time_limit":

            DEFAULT_TIME_LIMIT,

        "default_memory_limit":

            DEFAULT_MEMORY_LIMIT

    }


# ==========================================================
# HEALTH REPORT
# ==========================================================

def executor_report():

    return {

        "metadata":

            executor_metadata(),

        "environment":

            executor_health(),

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# QUICK SELF TEST
# ==========================================================

def self_test():

    return {

        "executor":

            "Ready",

        "health":

            executor_health(),

        "supported_languages": [

            PYTHON,

            C,

            CPP,

            JAVA,

            JAVASCRIPT

        ]

    }
# ==========================================================
# VERSION INFORMATION
# ==========================================================

EXECUTOR_NAME = "Lab Auto Grader Executor"

EXECUTOR_VERSION = "1.0.0"

EXECUTOR_AUTHOR = "Lab Auto Grader"


def version():
    """
    Return executor version information.
    """

    return {

        "name": EXECUTOR_NAME,

        "version": EXECUTOR_VERSION,

        "author": EXECUTOR_AUTHOR,

        "supported_languages": [

            PYTHON,

            C,

            CPP,

            JAVA,

            JAVASCRIPT

        ]

    }


# ==========================================================
# INITIALIZE EXECUTOR
# ==========================================================

def initialize():
    """
    Verify execution environment.
    """

    report = executor_health()

    if not any(report.values()):

        raise RuntimeError(

            "No runtime environment detected."

        )

    logger.info(

        "Executor initialized successfully."

    )

    return report


# ==========================================================
# MAIN EXECUTION API
# ==========================================================

def execute(
    language,
    source_code,
    custom_input="",
    compile_timeout=30,
    execution_timeout=DEFAULT_TIME_LIMIT
):
    """
    Compile and execute a program.
    """

    compile_result = compile_source(

        language,

        source_code,

        compile_timeout

    )

    if not compile_result.success:

        result = ExecutionResult(

            success=False,

            language=language,

            verdict=VERDICT_COMPILATION_ERROR,

            compile_result=compile_result,

            stderr=compile_result.error_output

        )

        return result

    return execute_program(

        compile_result,

        custom_input,

        execution_timeout

    )


# ==========================================================
# EXECUTE ONCE
# ==========================================================

def execute_once(
    language,
    source_code,
    custom_input=""
):
    """
    Compile, execute and cleanup.
    """

    result = execute(

        language,

        source_code,

        custom_input

    )

    if result.compile_result:

        cleanup_result(

            result.compile_result

        )

    return result


# ==========================================================
# VERIFY INSTALLATION
# ==========================================================

def verify_installation():
    """
    Verify required runtimes.
    """

    report = executor_health()

    return all(

        report.values()

    )


# ==========================================================
# PUBLIC API
# ==========================================================

__all__ = [

    # Models

    "ExecutionResult",

    # Main APIs

    "execute",

    "execute_once",

    "execute_program",

    "safe_execute",

    "execute_with_logging",

    "execute_batch",

    "execute_secure",

    # Language Executors

    "execute_python",

    "execute_c",

    "execute_cpp",

    "execute_java",

    "execute_javascript",

    # Utilities

    "cleanup_execution",

    "execution_summary",

    "execution_statistics",

    "execution_report",

    "execution_info",

    "performance_score",

    "benchmark_program",

    "retry_execution",

    "executor_health",

    "executor_report",

    "executor_metadata",

    "verify_installation",

    "initialize",

    "version"

]