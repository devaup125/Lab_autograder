"""
============================================================
Lab Auto Grader
Compiler Module
============================================================
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ==========================================================
# LANGUAGE CONSTANTS
# ==========================================================

PYTHON = "Python"
C = "C"
CPP = "C++"
JAVA = "Java"
JAVASCRIPT = "JavaScript"

SUPPORTED_LANGUAGES = (
    PYTHON,
    C,
    CPP,
    JAVA,
    JAVASCRIPT
)

# ==========================================================
# EXECUTABLES
# ==========================================================

PYTHON_EXECUTABLE = "python3"
GCC = "gcc"
GPP = "g++"
JAVAC = "javac"
NODE = "node"

DEFAULT_COMPILE_TIMEOUT = 30
MAX_SOURCE_SIZE = 2 * 1024 * 1024

# ==========================================================
# RESULT MODEL
# ==========================================================

@dataclass
class CompilationResult:

    success: bool = False
    language: str = ""

    source_file: str = ""
    executable: str = ""
    workdir: str = ""

    compile_output: str = ""
    error_output: str = ""

    return_code: int = -1
    compile_time: float = 0.0

# ==========================================================
# LANGUAGE CONFIG
# ==========================================================

LANGUAGE_CONFIG = {

    PYTHON: {
        "extension": ".py",
        "source": "main.py",
        "output": "main.py",
        "compile": False
    },

    C: {
        "extension": ".c",
        "source": "main.c",
        "output": "main",
        "compile": True
    },

    CPP: {
        "extension": ".cpp",
        "source": "main.cpp",
        "output": "main",
        "compile": True
    },

    JAVA: {
        "extension": ".java",
        "source": "Main.java",
        "output": "Main.class",
        "compile": True
    },

    JAVASCRIPT: {
        "extension": ".js",
        "source": "main.js",
        "output": "main.js",
        "compile": False
    }

}

# ==========================================================
# VALIDATION
# ==========================================================

def validate_language(language):

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}"
        )


def validate_source(source_code):

    if source_code is None:
        raise ValueError("Source code is None.")

    if source_code.strip() == "":
        raise ValueError("Source code is empty.")

    if len(source_code.encode()) > MAX_SOURCE_SIZE:
        raise ValueError(
            "Source code exceeds maximum size."
        )

# ==========================================================
# WORKSPACE
# ==========================================================

def create_workspace():

    return tempfile.mkdtemp(
        prefix="judge_compile_"
    )


def cleanup_workspace(path):

    if path and os.path.exists(path):

        shutil.rmtree(
            path,
            ignore_errors=True
        )

# ==========================================================
# FILE HELPERS
# ==========================================================

def source_filename(language):

    validate_language(language)

    return LANGUAGE_CONFIG[language]["source"]


def output_filename(language):

    validate_language(language)

    return LANGUAGE_CONFIG[language]["output"]


def write_source(
    workspace,
    language,
    source_code
):

    validate_language(language)
    validate_source(source_code)

    filename = source_filename(language)

    filepath = Path(workspace) / filename

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(source_code)

    return str(filepath)

# ==========================================================
# COMMON RESULT
# ==========================================================

def make_result(
    language,
    workspace,
    source_file
):

    executable = str(

        Path(workspace)

        / output_filename(language)

    )

    return CompilationResult(

        language=language,

        workdir=workspace,

        source_file=source_file,

        executable=executable

    )
# ==========================================================
# COMPILER COMMANDS
# ==========================================================

def compiler_command(
    language,
    source_file,
    executable
):
    """
    Return compiler command.
    """

    validate_language(language)

    if language == PYTHON:

        return None

    if language == JAVASCRIPT:

        return None

    if language == C:

        return [

            GCC,

            source_file,

            "-O2",

            "-std=c11",

            "-o",

            executable

        ]

    if language == CPP:

        return [

            GPP,

            source_file,

            "-O2",

            "-std=c++17",

            "-o",

            executable

        ]

    if language == JAVA:

        return [

            JAVAC,

            source_file

        ]


# ==========================================================
# PYTHON
# ==========================================================

def compile_python(
    workspace,
    source_code
):

    source_file = write_source(

        workspace,

        PYTHON,

        source_code

    )

    result = make_result(

        PYTHON,

        workspace,

        source_file

    )

    result.success = True

    result.return_code = 0

    return result


# ==========================================================
# JAVASCRIPT
# ==========================================================

def compile_javascript(
    workspace,
    source_code
):

    source_file = write_source(

        workspace,

        JAVASCRIPT,

        source_code

    )

    result = make_result(

        JAVASCRIPT,

        workspace,

        source_file

    )

    result.success = True

    result.return_code = 0

    return result


# ==========================================================
# C
# ==========================================================

def compile_c(
    workspace,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    source_file = write_source(

        workspace,

        C,

        source_code

    )

    result = make_result(

        C,

        workspace,

        source_file

    )

    command = compiler_command(

        C,

        source_file,

        result.executable

    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.compile_time = round(

            time.perf_counter() - start,

            4

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = (

            process.returncode == 0

        )

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timeout."

        return result


# ==========================================================
# C++
# ==========================================================

def compile_cpp(
    workspace,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    source_file = write_source(

        workspace,

        CPP,

        source_code

    )

    result = make_result(

        CPP,

        workspace,

        source_file

    )

    command = compiler_command(

        CPP,

        source_file,

        result.executable

    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.compile_time = round(

            time.perf_counter() - start,

            4

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = (

            process.returncode == 0

        )

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timeout."

        return result


# ==========================================================
# JAVA
# ==========================================================

def compile_java(
    workspace,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    source_file = write_source(

        workspace,

        JAVA,

        source_code

    )

    result = make_result(

        JAVA,

        workspace,

        source_file

    )

    command = compiler_command(

        JAVA,

        source_file,

        result.executable

    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,

            cwd=workspace,

            timeout=timeout

        )

        result.compile_time = round(

            time.perf_counter() - start,

            4

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = (

            process.returncode == 0

        )

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timeout."

        return result
# ==========================================================
# COMPILER DISPATCHER
# ==========================================================

def compile_source(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):
    """
    Compile source code for any supported language.
    """

    validate_language(language)

    workspace = create_workspace()

    if language == PYTHON:

        return compile_python(

            workspace,

            source_code

        )

    elif language == C:

        return compile_c(

            workspace,

            source_code,

            timeout

        )

    elif language == CPP:

        return compile_cpp(

            workspace,

            source_code,

            timeout

        )

    elif language == JAVA:

        return compile_java(

            workspace,

            source_code,

            timeout

        )

    elif language == JAVASCRIPT:

        return compile_javascript(

            workspace,

            source_code

        )

    raise ValueError(

        f"Unsupported language: {language}"

    )


# ==========================================================
# EXECUTABLE VALIDATION
# ==========================================================

def executable_exists(
    result: CompilationResult
):
    """
    Verify compiled executable exists.
    """

    if result.language in (

        PYTHON,

        JAVASCRIPT

    ):

        return os.path.exists(

            result.source_file

        )

    return os.path.exists(

        result.executable

    )


# ==========================================================
# COMPILATION VALIDATION
# ==========================================================

def compilation_success(
    result: CompilationResult
):
    """
    Check if compilation succeeded.
    """

    return (

        result.success

        and

        executable_exists(

            result

        )

    )


def compilation_failed(
    result: CompilationResult
):

    return not compilation_success(

        result

    )


# ==========================================================
# COMPILER CHECKS
# ==========================================================

def compiler_exists(
    language
):
    """
    Verify compiler/interpreter exists.
    """

    validate_language(language)

    executable = {

        PYTHON:

            PYTHON_EXECUTABLE,

        C:

            GCC,

        CPP:

            GPP,

        JAVA:

            JAVAC,

        JAVASCRIPT:

            NODE

    }[language]

    return shutil.which(

        executable

    ) is not None


def verify_environment():
    """
    Check all required compilers.
    """

    report = {}

    for language in SUPPORTED_LANGUAGES:

        report[language] = compiler_exists(

            language

        )

    return report


# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_result(
    result: CompilationResult
):
    """
    Remove compilation workspace.
    """

    cleanup_workspace(

        result.workdir

    )


# ==========================================================
# SAFE CLEANUP
# ==========================================================

def safe_cleanup(
    result: CompilationResult
):

    try:

        cleanup_result(

            result

        )

    except Exception:

        pass


# ==========================================================
# QUICK COMPILE
# ==========================================================

def quick_compile(
    language,
    source_code
):
    """
    Compile only.
    """

    return compile_source(

        language,

        source_code

    )


# ==========================================================
# COMPILE & CLEANUP
# ==========================================================

def compile_once(
    language,
    source_code
):

    result = compile_source(

        language,

        source_code

    )

    if not result.success:

        safe_cleanup(

            result

        )

    return result
# ==========================================================
# LOGGING
# ==========================================================

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def log_compilation(result: CompilationResult):
    """
    Log compilation result.
    """

    if result.success:

        logger.info(

            "Compilation Success | "
            "Language=%s | "
            "Time=%.4fs",

            result.language,

            result.compile_time

        )

    else:

        logger.error(

            "Compilation Failed | "
            "Language=%s | "
            "Error=%s",

            result.language,

            result.error_output

        )


# ==========================================================
# COMPILATION SUMMARY
# ==========================================================

def compilation_summary(
    result: CompilationResult
):

    return {

        "language":

            result.language,

        "success":

            result.success,

        "compile_time":

            result.compile_time,

        "return_code":

            result.return_code,

        "source_file":

            result.source_file,

        "executable":

            result.executable

    }


# ==========================================================
# JSON REPORT
# ==========================================================

def compilation_report(
    result: CompilationResult
):

    return {

        "summary":

            compilation_summary(

                result

            ),

        "compile_output":

            result.compile_output,

        "error_output":

            result.error_output,

        "generated_at":

            datetime.utcnow().isoformat()

    }


def export_report(
    result,
    filename
):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            compilation_report(

                result

            ),

            fp,

            indent=4

        )

    return filename


# ==========================================================
# BENCHMARK
# ==========================================================

def benchmark_compiler(
    language,
    source_code,
    runs=5
):

    timings = []

    for _ in range(runs):

        result = compile_source(

            language,

            source_code

        )

        timings.append(

            result.compile_time

        )

        safe_cleanup(

            result

        )

    return {

        "runs":

            runs,

        "minimum":

            round(

                min(timings),

                4

            ),

        "maximum":

            round(

                max(timings),

                4

            ),

        "average":

            round(

                sum(timings)

                /

                len(timings),

                4

            )

    }


# ==========================================================
# DIAGNOSTICS
# ==========================================================

def diagnostics():

    return {

        "supported_languages":

            SUPPORTED_LANGUAGES,

        "environment":

            verify_environment(),

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# PERFORMANCE GRADE
# ==========================================================

def compilation_grade(
    compile_time
):

    if compile_time <= 0.05:

        return "Excellent"

    elif compile_time <= 0.20:

        return "Very Good"

    elif compile_time <= 0.50:

        return "Good"

    elif compile_time <= 1.00:

        return "Average"

    return "Slow"


# ==========================================================
# METADATA
# ==========================================================

def compiler_metadata():

    return {

        "name":

            "Lab Auto Grader Compiler",

        "version":

            "1.0.0",

        "languages":

            SUPPORTED_LANGUAGES,

        "default_timeout":

            DEFAULT_COMPILE_TIMEOUT

    }


# ==========================================================
# HEALTH
# ==========================================================

def compiler_health():

    env = verify_environment()

    return {

        "healthy":

            all(

                env.values()

            ),

        "environment":

            env,

        "metadata":

            compiler_metadata()

    }
# ==========================================================
# PARALLEL COMPILATION
# ==========================================================

from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics


def compile_parallel(
    jobs,
    max_workers=4
):
    """
    Compile multiple source codes.

    jobs = [
        {
            "language": "...",
            "source_code": "..."
        }
    ]
    """

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = [

            executor.submit(

                compile_source,

                job["language"],

                job["source_code"]

            )

            for job in jobs

        ]

        for future in as_completed(futures):

            try:

                results.append(

                    future.result()

                )

            except Exception as e:

                logger.exception(e)

    return results


# ==========================================================
# BATCH COMPILATION
# ==========================================================

def compile_batch(
    jobs
):
    """
    Wrapper for batch compilation.
    """

    return compile_parallel(

        jobs

    )


# ==========================================================
# COMPILATION STATISTICS
# ==========================================================

def compilation_statistics(
    results
):

    if not results:

        return {}

    successful = sum(

        1

        for r in results

        if r.success

    )

    failed = len(results) - successful

    compile_times = [

        r.compile_time

        for r in results

    ]

    return {

        "total":

            len(results),

        "successful":

            successful,

        "failed":

            failed,

        "minimum":

            round(

                min(compile_times),

                4

            ),

        "maximum":

            round(

                max(compile_times),

                4

            ),

        "average":

            round(

                statistics.mean(

                    compile_times

                ),

                4

            ),

        "median":

            round(

                statistics.median(

                    compile_times

                ),

                4

            )

    }


# ==========================================================
# RETRY COMPILATION
# ==========================================================

def retry_compile(
    language,
    source_code,
    retries=3
):

    last = None

    for _ in range(retries):

        last = compile_source(

            language,

            source_code

        )

        if last.success:

            return last

    return last


# ==========================================================
# HISTORY
# ==========================================================

class CompilationHistory:

    def __init__(self):

        self.results = []

    def add(

        self,

        result

    ):

        self.results.append(

            result

        )

    def latest(self):

        if not self.results:

            return None

        return self.results[-1]

    def successful(self):

        return [

            r

            for r in self.results

            if r.success

        ]

    def failed(self):

        return [

            r

            for r in self.results

            if not r.success

        ]

    def clear(self):

        self.results.clear()

    def count(self):

        return len(

            self.results

        )


# ==========================================================
# VALIDATION
# ==========================================================

def validate_result(
    result
):

    return (

        isinstance(

            result,

            CompilationResult

        )

        and

        result.language

        in

        SUPPORTED_LANGUAGES

    )


# ==========================================================
# SAFE COMPILE
# ==========================================================

def safe_compile(
    language,
    source_code
):

    try:

        return compile_source(

            language,

            source_code

        )

    except Exception as e:

        result = CompilationResult()

        result.language = language

        result.error_output = str(e)

        return result


# ==========================================================
# COMPILE WITH LOGGING
# ==========================================================

def compile_logged(
    language,
    source_code
):

    result = safe_compile(

        language,

        source_code

    )

    log_compilation(

        result

    )

    return result


# ==========================================================
# COMPILATION SCORE
# ==========================================================

def compilation_score(
    result
):

    if not result.success:

        return 0

    score = 100

    if result.compile_time > 0.2:

        score -= 5

    if result.compile_time > 0.5:

        score -= 10

    if result.compile_time > 1:

        score -= 20

    return max(

        score,

        0

    )
# ==========================================================
# AUDIT LOGGING
# ==========================================================

import hashlib
from datetime import datetime


def compilation_id(result: CompilationResult):
    """
    Generate unique compilation ID.
    """

    data = (

        f"{result.language}"

        f"{result.source_file}"

        f"{result.compile_time}"

        f"{datetime.utcnow()}"

    )

    return hashlib.sha256(

        data.encode("utf-8")

    ).hexdigest()


# ==========================================================
# AUDIT REPORT
# ==========================================================

def compilation_audit(
    result: CompilationResult
):

    return {

        "compilation_id":

            compilation_id(

                result

            ),

        "language":

            result.language,

        "success":

            result.success,

        "compile_time":

            result.compile_time,

        "return_code":

            result.return_code,

        "source_file":

            result.source_file,

        "executable":

            result.executable,

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# EXPORT AUDIT
# ==========================================================

def export_audit(
    result,
    filename
):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            compilation_audit(

                result

            ),

            fp,

            indent=4

        )

    return filename


# ==========================================================
# PERFORMANCE MONITOR
# ==========================================================

class CompilerMonitor:

    def __init__(self):

        self.total = 0

        self.success = 0

        self.failed = 0

        self.total_time = 0.0

    def update(
        self,
        result
    ):

        self.total += 1

        self.total_time += (

            result.compile_time

        )

        if result.success:

            self.success += 1

        else:

            self.failed += 1

    def report(self):

        average = 0

        if self.total:

            average = round(

                self.total_time

                /

                self.total,

                4

            )

        return {

            "total":

                self.total,

            "success":

                self.success,

            "failed":

                self.failed,

            "average_compile_time":

                average

        }


# ==========================================================
# BENCHMARK SUITE
# ==========================================================

class CompilerBenchmark:

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

                r.compile_time

                for r in self.results

            )

            /

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

                compilation_statistics(

                    self.results

                )

        }


# ==========================================================
# COMPILATION DIAGNOSTICS
# ==========================================================

def compilation_diagnostics(
    result
):

    return {

        "language":

            result.language,

        "success":

            result.success,

        "compile_time":

            result.compile_time,

        "return_code":

            result.return_code,

        "compiler_available":

            compiler_exists(

                result.language

            ),

        "executable_exists":

            executable_exists(

                result

            )

    }


# ==========================================================
# EXECUTION READY
# ==========================================================

def execution_ready(
    result
):

    return (

        result.success

        and

        executable_exists(

            result

        )

    )


# ==========================================================
# COMPILER REPORT
# ==========================================================

def compiler_report():

    return {

        "metadata":

            compiler_metadata(),

        "health":

            compiler_health(),

        "environment":

            verify_environment(),

        "generated_at":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# SELF TEST
# ==========================================================

def self_test():

    return {

        "compiler":

            "Ready",

        "environment":

            verify_environment(),

        "languages":

            SUPPORTED_LANGUAGES

    }
# ==========================================================
# WORKSPACE MANAGER
# ==========================================================

class WorkspaceManager:
    """
    Manage compiler workspaces.
    """

    def __init__(self):

        self.workspaces = []

    def create(self):

        workspace = create_workspace()

        self.workspaces.append(

            workspace

        )

        return workspace

    def remove(
        self,
        workspace
    ):

        cleanup_workspace(

            workspace

        )

        if workspace in self.workspaces:

            self.workspaces.remove(

                workspace

            )

    def cleanup_all(self):

        for workspace in list(

            self.workspaces

        ):

            self.remove(

                workspace

            )

# ==========================================================
# COMPILATION MANAGER
# ==========================================================

class CompilationManager:

    def __init__(self):

        self.monitor = CompilerMonitor()

        self.history = CompilationHistory()

        self.workspace_manager = WorkspaceManager()

    def compile(
        self,
        language,
        source_code
    ):

        result = compile_source(

            language,

            source_code

        )

        self.monitor.update(

            result

        )

        self.history.add(

            result

        )

        return result

    def statistics(self):

        return self.monitor.report()

    def cleanup(self):

        self.workspace_manager.cleanup_all()

# ==========================================================
# PARALLEL MANAGER
# ==========================================================

class ParallelCompiler:

    def __init__(
        self,
        workers=4
    ):

        self.workers = workers

    def compile_jobs(
        self,
        jobs
    ):

        return compile_parallel(

            jobs,

            self.workers

        )

# ==========================================================
# RECOVERY
# ==========================================================

def recover_workspace(
    result
):

    if not os.path.exists(

        result.workdir

    ):

        os.makedirs(

            result.workdir,

            exist_ok=True

        )

    return result.workdir


def recover_failed_compilation(
    language,
    source_code
):

    return retry_compile(

        language,

        source_code,

        retries=3

    )

# ==========================================================
# RESOURCE INFORMATION
# ==========================================================

def runtime_information():

    return {

        "python":

            shutil.which(

                PYTHON_EXECUTABLE

            ),

        "gcc":

            shutil.which(

                GCC

            ),

        "g++":

            shutil.which(

                GPP

            ),

        "javac":

            shutil.which(

                JAVAC

            ),

        "node":

            shutil.which(

                NODE

            ),

        "workspace_prefix":

            "judge_compile_"

    }

# ==========================================================
# SYSTEM STATUS
# ==========================================================

def compiler_status():

    health = compiler_health()

    return {

        "status":

            "Ready"

            if health["healthy"]

            else "Unavailable",

        "environment":

            verify_environment(),

        "runtime":

            runtime_information()

    }

# ==========================================================
# EXECUTION PIPELINE
# ==========================================================

def compile_pipeline(
    language,
    source_code
):

    result = compile_logged(

        language,

        source_code

    )

    return {

        "result":

            result,

        "summary":

            compilation_summary(

                result

            ),

        "audit":

            compilation_audit(

                result

            )

    }

# ==========================================================
# SAFE PIPELINE
# ==========================================================

def safe_pipeline(
    language,
    source_code
):

    try:

        return compile_pipeline(

            language,

            source_code

        )

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }

# ==========================================================
# CLEANUP UTILITIES
# ==========================================================

def cleanup_results(
    results
):

    for result in results:

        safe_cleanup(

            result

        )

# ==========================================================
# ENGINE SUMMARY
# ==========================================================

def summary():

    return {

        "metadata":

            compiler_metadata(),

        "health":

            compiler_health(),

        "runtime":

            runtime_information(),

        "supported_languages":

            SUPPORTED_LANGUAGES

    }
# ==========================================================
# VERSION INFORMATION
# ==========================================================

COMPILER_NAME = "Lab Auto Grader Compiler"

COMPILER_VERSION = "1.0.0"

COMPILER_AUTHOR = "Devanshu Ranjan Upadhyay"


def version():
    """
    Compiler version information.
    """

    return {

        "name": COMPILER_NAME,

        "version": COMPILER_VERSION,

        "author": COMPILER_AUTHOR,

        "supported_languages": list(

            SUPPORTED_LANGUAGES

        )

    }


# ==========================================================
# INITIALIZE
# ==========================================================

def initialize():
    """
    Initialize compiler module.
    """

    report = verify_environment()

    logger.info(

        "Compiler initialized."

    )

    return report


# ==========================================================
# VERIFY INSTALLATION
# ==========================================================

def verify_installation():
    """
    Verify all required compilers/interpreters.
    """

    report = verify_environment()

    return all(

        report.values()

    )


# ==========================================================
# READY
# ==========================================================

def ready():

    return verify_installation()


# ==========================================================
# MAIN API
# ==========================================================

def compile(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):
    """
    Public compiler API.
    """

    return compile_source(

        language,

        source_code,

        timeout

    )


# ==========================================================
# COMPILE WITH REPORT
# ==========================================================

def compile_with_report(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    result = compile(

        language,

        source_code,

        timeout

    )

    return {

        "result":

            result,

        "summary":

            compilation_summary(

                result

            ),

        "audit":

            compilation_audit(

                result

            )

    }


# ==========================================================
# COMPILE & EXPORT
# ==========================================================

def compile_export(
    language,
    source_code,
    report_file,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    result = compile(

        language,

        source_code,

        timeout

    )

    export_report(

        result,

        report_file

    )

    return result


# ==========================================================
# SHUTDOWN
# ==========================================================

def shutdown():
    """
    Cleanup compiler resources.
    """

    logger.info(

        "Compiler shutdown."

    )

    return True


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    # Constants

    "PYTHON",

    "C",

    "CPP",

    "JAVA",

    "JAVASCRIPT",

    "SUPPORTED_LANGUAGES",

    # Models

    "CompilationResult",

    # Main APIs

    "compile",

    "compile_source",

    "compile_once",

    "quick_compile",

    "compile_parallel",

    "compile_batch",

    "retry_compile",

    "safe_compile",

    "compile_logged",

    "compile_pipeline",

    "safe_pipeline",

    # Managers

    "WorkspaceManager",

    "CompilationManager",

    "ParallelCompiler",

    "CompilationHistory",

    "CompilerMonitor",

    "CompilerBenchmark",

    # Reports

    "compilation_summary",

    "compilation_report",

    "compilation_audit",

    "compiler_report",

    "compiler_health",

    "compiler_metadata",

    "diagnostics",

    "summary",

    "compiler_status",

    # Utilities

    "cleanup_result",

    "cleanup_results",

    "safe_cleanup",

    "verify_environment",

    "verify_installation",

    "execution_ready",

    "runtime_information",

    "initialize",

    "shutdown",

    "ready",

    "version"

]