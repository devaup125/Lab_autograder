"""
==========================================================
Lab Auto Grader
Compiler Module
Part 1
==========================================================
"""

import os
import shutil
import subprocess
import tempfile
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
    JAVASCRIPT,
)

# ==========================================================
# EXECUTABLES
# ==========================================================

PYTHON_EXECUTABLE = "python3"
GCC = "gcc"
GPP = "g++"
JAVAC = "javac"
NODE = "node"

# ==========================================================
# LIMITS
# ==========================================================

DEFAULT_COMPILE_TIMEOUT = 30
MAX_SOURCE_SIZE = 2 * 1024 * 1024  # 2 MB

# ==========================================================
# COMPILATION RESULT
# ==========================================================

@dataclass
class CompilationResult:

    success: bool = False

    language: str = ""

    executable: Optional[str] = None

    compile_output: str = ""

    error_output: str = ""

    compile_time: float = 0.0

    workdir: str = ""

    source_file: str = ""

    return_code: int = -1


# ==========================================================
# LANGUAGE CONFIGURATION
# ==========================================================

LANGUAGE_CONFIG = {

    PYTHON: {

        "extension": ".py",

        "compile": False,

        "source": "main.py",

        "output": "main.py"

    },

    C: {

        "extension": ".c",

        "compile": True,

        "source": "main.c",

        "output": "main"

    },

    CPP: {

        "extension": ".cpp",

        "compile": True,

        "source": "main.cpp",

        "output": "main"

    },

    JAVA: {

        "extension": ".java",

        "compile": True,

        "source": "Main.java",

        "output": "Main.class"

    },

    JAVASCRIPT: {

        "extension": ".js",

        "compile": False,

        "source": "main.js",

        "output": "main.js"

    }

}

# ==========================================================
# HELPERS
# ==========================================================

def validate_language(language: str):

    if language not in SUPPORTED_LANGUAGES:

        raise ValueError(

            f"Unsupported language: {language}"

        )


def validate_source(source_code: str):

    if source_code is None:

        raise ValueError(

            "Source code cannot be None."

        )

    if not source_code.strip():

        raise ValueError(

            "Source code cannot be empty."

        )

    if len(source_code.encode("utf-8")) > MAX_SOURCE_SIZE:

        raise ValueError(

            "Source code exceeds maximum allowed size."

        )


def create_workdir():

    return tempfile.mkdtemp(

        prefix="lab_autograder_"

    )


def cleanup_workdir(path):

    if path and os.path.exists(path):

        shutil.rmtree(

            path,

            ignore_errors=True

        )


def get_source_filename(language):

    validate_language(language)

    return LANGUAGE_CONFIG[language]["source"]


def get_output_filename(language):

    validate_language(language)

    return LANGUAGE_CONFIG[language]["output"]


def compiler_required(language):

    validate_language(language)

    return LANGUAGE_CONFIG[language]["compile"]


def source_extension(language):

    validate_language(language)

    return LANGUAGE_CONFIG[language]["extension"]


def write_source_file(

    workdir,

    language,

    source_code

):

    validate_language(language)

    validate_source(source_code)

    filename = get_source_filename(language)

    filepath = Path(workdir) / filename

    with open(

        filepath,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(source_code)

    return str(filepath)
# ==========================================================
# PYTHON COMPILER
# ==========================================================

def compile_python(

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    Python doesn't require compilation.
    We only validate syntax.
    """

    workdir = create_workdir()

    source_path = write_source_file(

        workdir,

        PYTHON,

        source_code

    )

    result = CompilationResult(

        language=PYTHON,

        workdir=workdir,

        source_file=source_path,

        executable=source_path

    )

    try:

        process = subprocess.run(

            [

                PYTHON_EXECUTABLE,

                "-m",

                "py_compile",

                source_path

            ],

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = process.returncode == 0

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timed out."

        return result

    except Exception as e:

        result.error_output = str(e)

        return result


# ==========================================================
# C COMPILER
# ==========================================================

def compile_c(

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    Compile C source code using gcc.
    """

    workdir = create_workdir()

    source_path = write_source_file(

        workdir,

        C,

        source_code

    )

    executable = str(

        Path(workdir)

        / get_output_filename(C)

    )

    result = CompilationResult(

        language=C,

        workdir=workdir,

        source_file=source_path,

        executable=executable

    )

    command = [

        GCC,

        source_path,

        "-O2",

        "-std=c11",

        "-Wall",

        "-Wextra",

        "-o",

        executable

    ]

    try:

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = process.returncode == 0

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timed out."

        return result

    except FileNotFoundError:

        result.error_output = (

            "gcc compiler not found."

        )

        return result

    except Exception as e:

        result.error_output = str(e)

        return result


# ==========================================================
# COMMON HELPER
# ==========================================================

def compilation_success(

    result: CompilationResult

):

    return (

        result.success

        and

        result.return_code == 0

    )


def compilation_failed(

    result: CompilationResult

):

    return not compilation_success(result)
# ==========================================================
# C++ COMPILER
# ==========================================================

def compile_cpp(

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    Compile C++ source code using g++.
    """

    workdir = create_workdir()

    source_path = write_source_file(

        workdir,

        CPP,

        source_code

    )

    executable = str(

        Path(workdir)

        / get_output_filename(CPP)

    )

    result = CompilationResult(

        language=CPP,

        workdir=workdir,

        source_file=source_path,

        executable=executable

    )

    command = [

        GPP,

        source_path,

        "-O2",

        "-std=c++17",

        "-Wall",

        "-Wextra",

        "-o",

        executable

    ]

    try:

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = process.returncode == 0

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timed out."

        return result

    except FileNotFoundError:

        result.error_output = "g++ compiler not found."

        return result

    except Exception as e:

        result.error_output = str(e)

        return result


# ==========================================================
# JAVA COMPILER
# ==========================================================

def compile_java(

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    Compile Java source code using javac.
    """

    workdir = create_workdir()

    source_path = write_source_file(

        workdir,

        JAVA,

        source_code

    )

    result = CompilationResult(

        language=JAVA,

        workdir=workdir,

        source_file=source_path,

        executable=str(

            Path(workdir) / "Main.class"

        )

    )

    command = [

        JAVAC,

        source_path

    ]

    try:

        process = subprocess.run(

            command,

            cwd=workdir,

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = process.returncode == 0

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timed out."

        return result

    except FileNotFoundError:

        result.error_output = "javac compiler not found."

        return result

    except Exception as e:

        result.error_output = str(e)

        return result


# ==========================================================
# COMPILER OUTPUT HELPERS
# ==========================================================

def has_compilation_error(

    result: CompilationResult

):

    return (

        not result.success

    )


def compiler_message(

    result: CompilationResult

):

    if result.success:

        return "Compilation successful."

    return (

        result.error_output

        or

        result.compile_output

        or

        "Compilation failed."

    )


# ==========================================================
# VERIFY EXECUTABLE
# ==========================================================

def executable_exists(

    result: CompilationResult

):

    if not result.executable:

        return False

    return os.path.exists(

        result.executable

    )
# ==========================================================
# JAVASCRIPT COMPILER
# ==========================================================

def compile_javascript(

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    JavaScript does not require compilation.
    Verify syntax using Node.js.
    """

    workdir = create_workdir()

    source_path = write_source_file(

        workdir,

        JAVASCRIPT,

        source_code

    )

    result = CompilationResult(

        language=JAVASCRIPT,

        workdir=workdir,

        source_file=source_path,

        executable=source_path

    )

    try:

        process = subprocess.run(

            [

                NODE,

                "--check",

                source_path

            ],

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.return_code = process.returncode

        result.compile_output = process.stdout

        result.error_output = process.stderr

        result.success = process.returncode == 0

        return result

    except subprocess.TimeoutExpired:

        result.error_output = "Compilation timed out."

        return result

    except FileNotFoundError:

        result.error_output = "Node.js not installed."

        return result

    except Exception as e:

        result.error_output = str(e)

        return result


# ==========================================================
# UNIVERSAL COMPILER
# ==========================================================

def compile_source(

    language,

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    Universal compilation dispatcher.
    """

    validate_language(language)

    validate_source(source_code)

    compiler_map = {

        PYTHON: compile_python,

        C: compile_c,

        CPP: compile_cpp,

        JAVA: compile_java,

        JAVASCRIPT: compile_javascript

    }

    compiler = compiler_map.get(language)

    if compiler is None:

        raise ValueError(

            f"No compiler available for {language}"

        )

    return compiler(

        source_code,

        timeout

    )


# ==========================================================
# SAFE COMPILATION
# ==========================================================

def safe_compile(

    language,

    source_code,

    timeout=DEFAULT_COMPILE_TIMEOUT

):
    """
    Never raises exceptions.
    Always returns CompilationResult.
    """

    try:

        return compile_source(

            language,

            source_code,

            timeout

        )

    except Exception as e:

        return CompilationResult(

            success=False,

            language=language,

            error_output=str(e)

        )


# ==========================================================
# LANGUAGE INFORMATION
# ==========================================================

def supported_languages():

    return list(

        SUPPORTED_LANGUAGES

    )


def language_supported(

    language

):

    return language in SUPPORTED_LANGUAGES


def compiler_name(

    language

):

    mapping = {

        PYTHON: PYTHON_EXECUTABLE,

        C: GCC,

        CPP: GPP,

        JAVA: JAVAC,

        JAVASCRIPT: NODE

    }

    return mapping.get(

        language,

        "Unknown"

    )


# ==========================================================
# COMPILER VERSION
# ==========================================================

def compiler_version(

    language

):

    executable = compiler_name(language)

    commands = {

        PYTHON: [

            executable,

            "--version"

        ],

        C: [

            executable,

            "--version"

        ],

        CPP: [

            executable,

            "--version"

        ],

        JAVA: [

            executable,

            "-version"

        ],

        JAVASCRIPT: [

            executable,

            "--version"

        ]

    }

    try:

        process = subprocess.run(

            commands[language],

            capture_output=True,

            text=True,

            timeout=5

        )

        output = (

            process.stdout

            or

            process.stderr

        )

        return output.strip()

    except Exception:

        return "Unknown"


# ==========================================================
# COMPILER HEALTH CHECK
# ==========================================================

def compiler_available(

    language

):

    executable = compiler_name(

        language

    )

    return shutil.which(

        executable

    ) is not None
# ==========================================================
# DOCKER COMPILATION SUPPORT
# ==========================================================

import logging
import time

logger = logging.getLogger(__name__)


def compile_in_docker(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):
    """
    Wrapper for Docker compilation.

    Currently forwards to the local compiler.
    This function can later be replaced by
    docker_runner.compile().
    """

    logger.info(
        "Compiling %s source inside sandbox.",
        language
    )

    return safe_compile(
        language=language,
        source_code=source_code,
        timeout=timeout
    )


# ==========================================================
# COMPILATION LOGGER
# ==========================================================

def log_compilation(result: CompilationResult):

    if result.success:

        logger.info(

            "Compilation successful | "
            "Language=%s | "
            "File=%s",

            result.language,

            result.source_file

        )

    else:

        logger.error(

            "Compilation failed | "
            "Language=%s | "
            "Error=%s",

            result.language,

            result.error_output

        )


# ==========================================================
# COMPILATION TIMER
# ==========================================================

def timed_compile(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    start = time.perf_counter()

    result = safe_compile(

        language,

        source_code,

        timeout

    )

    result.compile_time = round(

        time.perf_counter() - start,

        4

    )

    return result


# ==========================================================
# COMPILE AND LOG
# ==========================================================

def compile_with_logging(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):

    result = timed_compile(

        language,

        source_code,

        timeout

    )

    log_compilation(result)

    return result


# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_result(

    result: CompilationResult

):

    if result and result.workdir:

        cleanup_workdir(

            result.workdir

        )


# ==========================================================
# CONTEXT MANAGER
# ==========================================================

class CompilerContext:
    """
    Automatically cleans temporary
    compilation directory.
    """

    def __init__(
        self,
        language,
        source_code,
        timeout=DEFAULT_COMPILE_TIMEOUT
    ):

        self.language = language

        self.source_code = source_code

        self.timeout = timeout

        self.result = None

    def __enter__(self):

        self.result = compile_with_logging(

            self.language,

            self.source_code,

            self.timeout

        )

        return self.result

    def __exit__(

        self,

        exc_type,

        exc_val,

        exc_tb

    ):

        if self.result:

            cleanup_result(

                self.result

            )

        return False


# ==========================================================
# COMPILATION STATISTICS
# ==========================================================

def compilation_statistics(
    result: CompilationResult
):

    return {

        "language": result.language,

        "success": result.success,

        "return_code": result.return_code,

        "compile_time": result.compile_time,

        "workdir": result.workdir,

        "source_file": result.source_file,

        "executable": result.executable

    }


# ==========================================================
# VALIDATE RESULT
# ==========================================================

def validate_compilation(
    result: CompilationResult
):

    if not isinstance(

        result,

        CompilationResult

    ):

        raise TypeError(

            "Expected CompilationResult."

        )

    return result


# ==========================================================
# FORMAT COMPILER OUTPUT
# ==========================================================

def formatted_output(
    result: CompilationResult
):

    if result.success:

        return {

            "status": "Success",

            "message": "Compilation completed.",

            "time": result.compile_time

        }

    return {

        "status": "Compilation Error",

        "message": result.error_output,

        "time": result.compile_time

    }
# ==========================================================
# ERROR PARSING UTILITIES
# ==========================================================

import re


def extract_errors(result: CompilationResult):
    """
    Extract compiler errors.
    """

    if result.success:
        return []

    errors = []

    for line in result.error_output.splitlines():

        line = line.strip()

        if not line:
            continue

        if (
            "error:" in line.lower()
            or "fatal error" in line.lower()
            or "exception" in line.lower()
        ):
            errors.append(line)

    return errors


def extract_warnings(result: CompilationResult):
    """
    Extract compiler warnings.
    """

    warnings = []

    for line in result.error_output.splitlines():

        line = line.strip()

        if "warning:" in line.lower():
            warnings.append(line)

    return warnings


# ==========================================================
# LANGUAGE SPECIFIC PARSERS
# ==========================================================

def parse_gcc_output(result: CompilationResult):

    diagnostics = []

    pattern = re.compile(
        r"^(.*?):(\d+):(\d+):\s*(warning|error):\s*(.*)$"
    )

    for line in result.error_output.splitlines():

        match = pattern.match(line)

        if match:

            diagnostics.append({

                "file": match.group(1),

                "line": int(match.group(2)),

                "column": int(match.group(3)),

                "type": match.group(4),

                "message": match.group(5)

            })

    return diagnostics


def parse_javac_output(result: CompilationResult):

    diagnostics = []

    lines = result.error_output.splitlines()

    current = None

    for line in lines:

        if ".java:" in line:

            parts = line.split(":")

            if len(parts) >= 3:

                current = {

                    "file": parts[0],

                    "line": int(parts[1]),

                    "message": ":".join(parts[2:]).strip()

                }

                diagnostics.append(current)

    return diagnostics


def parse_python_output(result: CompilationResult):

    diagnostics = []

    for line in result.error_output.splitlines():

        if "File" in line:

            diagnostics.append({

                "message": line

            })

    return diagnostics


def parse_node_output(result: CompilationResult):

    diagnostics = []

    for line in result.error_output.splitlines():

        diagnostics.append({

            "message": line

        })

    return diagnostics


# ==========================================================
# UNIVERSAL PARSER
# ==========================================================

def parse_diagnostics(result: CompilationResult):

    if result.language == C:

        return parse_gcc_output(result)

    if result.language == CPP:

        return parse_gcc_output(result)

    if result.language == JAVA:

        return parse_javac_output(result)

    if result.language == PYTHON:

        return parse_python_output(result)

    if result.language == JAVASCRIPT:

        return parse_node_output(result)

    return []


# ==========================================================
# SUMMARY
# ==========================================================

def compilation_summary(result: CompilationResult):

    return {

        "language": result.language,

        "success": result.success,

        "errors": extract_errors(result),

        "warnings": extract_warnings(result),

        "diagnostics": parse_diagnostics(result),

        "compile_time": result.compile_time,

        "return_code": result.return_code

    }


# ==========================================================
# PRINT HELPERS
# ==========================================================

def pretty_print(result: CompilationResult):

    summary = compilation_summary(result)

    print("=" * 60)

    print("Language :", summary["language"])

    print("Success  :", summary["success"])

    print("Time     :", summary["compile_time"])

    print("Return   :", summary["return_code"])

    print("-" * 60)

    if summary["warnings"]:

        print("Warnings:")

        for warning in summary["warnings"]:

            print(f"  • {warning}")

    if summary["errors"]:

        print("Errors:")

        for error in summary["errors"]:

            print(f"  • {error}")

    print("=" * 60)
# ==========================================================
# BATCH COMPILATION
# ==========================================================

from concurrent.futures import ThreadPoolExecutor, as_completed


def compile_multiple(
    submissions,
    timeout=DEFAULT_COMPILE_TIMEOUT,
    max_workers=4
):
    """
    Compile multiple source codes concurrently.

    submissions = [
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

                compile_with_logging,

                submission["language"],

                submission["source_code"],

                timeout

            )

            for submission in submissions

        ]

        for future in as_completed(futures):

            try:

                results.append(

                    future.result()

                )

            except Exception as e:

                results.append(

                    CompilationResult(

                        success=False,

                        error_output=str(e)

                    )

                )

    return results


# ==========================================================
# VERIFY ENVIRONMENT
# ==========================================================

def verify_environment():
    """
    Check whether all required compilers
    are available.
    """

    report = {}

    for language in SUPPORTED_LANGUAGES:

        report[language] = {

            "compiler":

                compiler_name(language),

            "available":

                compiler_available(language),

            "version":

                compiler_version(language)

                if compiler_available(language)

                else "Unavailable"

        }

    return report


# ==========================================================
# COMPILER REPORT
# ==========================================================

def compiler_report():

    report = verify_environment()

    successful = sum(

        1

        for value in report.values()

        if value["available"]

    )

    return {

        "total":

            len(report),

        "available":

            successful,

        "missing":

            len(report) - successful,

        "details":

            report

    }


# ==========================================================
# BENCHMARK
# ==========================================================

def benchmark_compiler(
    language,
    source_code,
    runs=5
):

    times = []

    last_result = None

    for _ in range(runs):

        result = timed_compile(

            language,

            source_code

        )

        last_result = result

        times.append(

            result.compile_time

        )

        cleanup_result(result)

    average = round(

        sum(times) / len(times),

        4

    )

    return {

        "language":

            language,

        "runs":

            runs,

        "average_compile_time":

            average,

        "last_result":

            last_result.success

            if last_result

            else False

    }


# ==========================================================
# CACHE (OPTIONAL)
# ==========================================================

_compile_cache = {}


def cached_compile(
    language,
    source_code
):

    key = (

        language,

        hash(source_code)

    )

    if key in _compile_cache:

        return _compile_cache[key]

    result = compile_with_logging(

        language,

        source_code

    )

    _compile_cache[key] = result

    return result


def clear_compile_cache():

    _compile_cache.clear()


# ==========================================================
# COMPILER METADATA
# ==========================================================

def compiler_metadata():

    return {

        "supported_languages":

            list(

                SUPPORTED_LANGUAGES

            ),

        "default_timeout":

            DEFAULT_COMPILE_TIMEOUT,

        "maximum_source_size":

            MAX_SOURCE_SIZE,

        "cache_size":

            len(

                _compile_cache

            )

    }


# ==========================================================
# QUICK SELF TEST
# ==========================================================

def self_test():

    tests = {

        PYTHON:

            "print('Hello')",

        C:

            "#include<stdio.h>\n"

            "int main(){return 0;}",

        CPP:

            "#include<iostream>\n"

            "int main(){return 0;}",

        JAVA:

            "public class Main{"

            "public static void main"

            "(String[]args){}}",

        JAVASCRIPT:

            "console.log('Hello');"

    }

    report = {}

    for language, code in tests.items():

        result = safe_compile(

            language,

            code

        )

        report[language] = {

            "success":

                result.success,

            "time":

                result.compile_time

        }

        cleanup_result(result)

    return report
# ==========================================================
# WORKSPACE VALIDATION
# ==========================================================

def workspace_exists(path):
    """
    Check whether a workspace exists.
    """

    return (

        path is not None

        and

        os.path.isdir(path)

    )


def workspace_empty(path):
    """
    Check whether workspace is empty.
    """

    if not workspace_exists(path):

        return True

    return len(os.listdir(path)) == 0


# ==========================================================
# BUILD ARTIFACTS
# ==========================================================

def build_artifacts(result: CompilationResult):
    """
    Return all generated files.
    """

    if not workspace_exists(result.workdir):

        return []

    artifacts = []

    for root, _, files in os.walk(result.workdir):

        for file in files:

            artifacts.append(

                os.path.join(

                    root,

                    file

                )

            )

    return artifacts


# ==========================================================
# REMOVE BUILD FILES
# ==========================================================

def remove_build_artifacts(result: CompilationResult):
    """
    Remove generated executable/class files
    but preserve source code.
    """

    if not workspace_exists(result.workdir):

        return

    extensions = {

        ".o",

        ".out",

        ".exe",

        ".class"

    }

    for root, _, files in os.walk(result.workdir):

        for file in files:

            path = os.path.join(

                root,

                file

            )

            if (

                Path(path).suffix

                in extensions

            ):

                try:

                    os.remove(path)

                except OSError:

                    pass

            elif (

                os.access(path, os.X_OK)

                and

                Path(path).suffix == ""

            ):

                try:

                    os.remove(path)

                except OSError:

                    pass


# ==========================================================
# SAFE CLEANUP
# ==========================================================

def safe_cleanup(result: CompilationResult):
    """
    Remove artifacts and workspace.
    """

    try:

        remove_build_artifacts(result)

    except Exception:

        pass

    try:

        cleanup_result(result)

    except Exception:

        pass


# ==========================================================
# RESET WORKSPACE
# ==========================================================

def reset_workspace(path):
    """
    Delete and recreate workspace.
    """

    cleanup_workdir(path)

    os.makedirs(

        path,

        exist_ok=True

    )

    return path


# ==========================================================
# COPY SOURCE
# ==========================================================

def copy_source(result: CompilationResult, destination):
    """
    Backup source code.
    """

    os.makedirs(

        destination,

        exist_ok=True

    )

    target = os.path.join(

        destination,

        os.path.basename(

            result.source_file

        )

    )

    shutil.copy2(

        result.source_file,

        target

    )

    return target


# ==========================================================
# WORKSPACE SIZE
# ==========================================================

def workspace_size(path):
    """
    Workspace size in bytes.
    """

    if not workspace_exists(path):

        return 0

    total = 0

    for root, _, files in os.walk(path):

        for file in files:

            file_path = os.path.join(

                root,

                file

            )

            try:

                total += os.path.getsize(

                    file_path

                )

            except OSError:

                pass

    return total


# ==========================================================
# CLEAN OLD WORKSPACES
# ==========================================================

def clean_old_workspaces(
    base_dir,
    max_age_hours=24
):
    """
    Remove temporary workspaces older than
    max_age_hours.
    """

    if not os.path.isdir(base_dir):

        return 0

    removed = 0

    current = time.time()

    limit = max_age_hours * 3600

    for name in os.listdir(base_dir):

        path = os.path.join(

            base_dir,

            name

        )

        if not os.path.isdir(path):

            continue

        try:

            age = current - os.path.getmtime(path)

            if age > limit:

                shutil.rmtree(

                    path,

                    ignore_errors=True

                )

                removed += 1

        except Exception:

            pass

    return removed


# ==========================================================
# TEMP DIRECTORY INFORMATION
# ==========================================================

def workspace_information(path):
    """
    Return workspace metadata.
    """

    return {

        "exists":

            workspace_exists(path),

        "empty":

            workspace_empty(path),

        "size":

            workspace_size(path),

        "files":

            len(

                build_artifacts(

                    CompilationResult(

                        workdir=path

                    )

                )

            )

    }
# ==========================================================
# SOURCE HASHING
# ==========================================================

import hashlib
import json
from datetime import datetime


def source_hash(source_code):
    """
    SHA-256 hash of source code.
    """

    return hashlib.sha256(

        source_code.encode("utf-8")

    ).hexdigest()


def compilation_id(result: CompilationResult):
    """
    Unique compilation identifier.
    """

    return hashlib.md5(

        f"{result.language}"
        f"{result.source_file}"
        f"{time.time()}".encode()

    ).hexdigest()


# ==========================================================
# AUDIT LOG
# ==========================================================

def compilation_audit(result: CompilationResult):
    """
    Audit information for every compilation.
    """

    return {

        "id":

            compilation_id(result),

        "language":

            result.language,

        "success":

            result.success,

        "return_code":

            result.return_code,

        "compile_time":

            result.compile_time,

        "source_file":

            result.source_file,

        "workspace":

            result.workdir,

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# EXPORT LOG
# ==========================================================

def export_log(
    result: CompilationResult,
    filepath
):
    """
    Save compilation log as JSON.
    """

    with open(

        filepath,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            compilation_audit(result),

            fp,

            indent=4

        )

    return filepath


# ==========================================================
# RESOURCE LIMITS
# ==========================================================

DEFAULT_MEMORY_LIMIT = 256       # MB

DEFAULT_CPU_LIMIT = 1            # CPU

DEFAULT_PROCESS_LIMIT = 20

DEFAULT_FILE_LIMIT = 50


def resource_limits():

    return {

        "memory":

            DEFAULT_MEMORY_LIMIT,

        "cpu":

            DEFAULT_CPU_LIMIT,

        "processes":

            DEFAULT_PROCESS_LIMIT,

        "open_files":

            DEFAULT_FILE_LIMIT

    }


# ==========================================================
# SOURCE STATISTICS
# ==========================================================

def source_statistics(source):

    return {

        "characters":

            len(source),

        "lines":

            len(source.splitlines()),

        "words":

            len(source.split()),

        "hash":

            source_hash(source)

    }


# ==========================================================
# MONITOR
# ==========================================================

def monitor(result: CompilationResult):

    return {

        "language":

            result.language,

        "status":

            "Success"

            if result.success

            else "Failed",

        "compiler":

            compiler_name(

                result.language

            ),

        "compile_time":

            result.compile_time,

        "workspace_size":

            workspace_size(

                result.workdir

            )

    }


# ==========================================================
# SECURITY CHECK
# ==========================================================

BLACKLIST = (

    "fork(",

    "system(",

    "exec(",

    "popen(",

    "os.system",

    "subprocess",

    "__import__",

    "socket",

    "multiprocessing"

)


def security_scan(source):

    detected = []

    lower = source.lower()

    for keyword in BLACKLIST:

        if keyword.lower() in lower:

            detected.append(keyword)

    return {

        "safe":

            len(detected) == 0,

        "detected":

            detected

    }


# ==========================================================
# COMPILER DIAGNOSTICS
# ==========================================================

def diagnostics(result: CompilationResult):

    return {

        "summary":

            compilation_summary(result),

        "statistics":

            compilation_statistics(result),

        "monitor":

            monitor(result)

    }


# ==========================================================
# HEALTH REPORT
# ==========================================================

def compiler_health():

    report = compiler_report()

    report["resource_limits"] = resource_limits()

    report["timestamp"] = datetime.utcnow().isoformat()

    return report
# ==========================================================
# VERSION INFORMATION
# ==========================================================

COMPILER_NAME = "Lab Auto Grader Compiler"

COMPILER_VERSION = "1.0.0"

COMPILER_AUTHOR = "Lab Auto Grader"


def version():
    """
    Return compiler version information.
    """
    return {
        "name": COMPILER_NAME,
        "version": COMPILER_VERSION,
        "author": COMPILER_AUTHOR,
        "languages": supported_languages()
    }


# ==========================================================
# INITIALIZATION
# ==========================================================

def initialize():
    """
    Verify compiler environment before use.
    """

    report = compiler_report()

    if report["available"] == 0:
        raise RuntimeError(
            "No supported compiler was found."
        )

    logger.info(
        "Compiler initialized successfully."
    )

    return report


# ==========================================================
# DEFAULT API
# ==========================================================

def compile(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):
    """
    Main compiler API.
    """

    return compile_with_logging(
        language=language,
        source_code=source_code,
        timeout=timeout
    )


# ==========================================================
# COMPILE & CLEAN
# ==========================================================

def compile_once(
    language,
    source_code,
    timeout=DEFAULT_COMPILE_TIMEOUT
):
    """
    Compile and automatically cleanup.
    """

    result = compile(
        language,
        source_code,
        timeout
    )

    output = compilation_summary(result)

    safe_cleanup(result)

    return output


# ==========================================================
# VERIFY INSTALLATION
# ==========================================================

def verify_installation():
    """
    Check whether compiler is ready.
    """

    report = compiler_report()

    return report["missing"] == 0


# ==========================================================
# MODULE EXPORTS
# ==========================================================

__all__ = [

    # Main APIs
    "compile",
    "compile_once",
    "safe_compile",
    "compile_source",
    "compile_with_logging",
    "compile_multiple",

    # Language compilers
    "compile_python",
    "compile_c",
    "compile_cpp",
    "compile_java",
    "compile_javascript",

    # Models
    "CompilationResult",

    # Validation
    "validate_language",
    "validate_source",

    # Helpers
    "cleanup_result",
    "safe_cleanup",
    "compiler_report",
    "compiler_health",
    "verify_environment",
    "verify_installation",
    "supported_languages",
    "compiler_available",
    "compiler_version",
    "compiler_name",

    # Diagnostics
    "diagnostics",
    "compilation_summary",
    "compilation_statistics",
    "extract_errors",
    "extract_warnings",
    "pretty_print",

    # Security
    "security_scan",
    "source_hash",

    # Metadata
    "version",
    "initialize"
]