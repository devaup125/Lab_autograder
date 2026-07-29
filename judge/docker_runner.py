"""
==========================================================
Lab Auto Grader
Docker Runner
Part 1
==========================================================
"""

import os
import json
import time
import uuid
import shutil
import logging
import subprocess

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# ==========================================================
# DOCKER CONFIGURATION
# ==========================================================

DOCKER_EXECUTABLE = "docker"

DEFAULT_IMAGE = "python:3.11-slim"

DEFAULT_MEMORY = "256m"

DEFAULT_CPUS = "1"

DEFAULT_TIMEOUT = 5

DEFAULT_NETWORK = "none"

DEFAULT_WORKDIR = "/workspace"

DEFAULT_PIDS_LIMIT = 64

DEFAULT_TMPFS = "/tmp:rw,noexec,nosuid,size=64m"

# ==========================================================
# DOCKER RESULT
# ==========================================================

@dataclass
class DockerResult:

    success: bool = False

    container_id: str = ""

    container_name: str = ""

    image: str = ""

    command: str = ""

    stdout: str = ""

    stderr: str = ""

    exit_code: int = -1

    execution_time: float = 0.0

    timed_out: bool = False

    workdir: str = ""

# ==========================================================
# IMAGE MAP
# ==========================================================

LANGUAGE_IMAGES = {

    "Python": "python:3.11-slim",

    "C": "gcc:13",

    "C++": "gcc:13",

    "Java": "openjdk:21",

    "JavaScript": "node:20"

}

# ==========================================================
# HELPERS
# ==========================================================

def docker_exists():

    return shutil.which(

        DOCKER_EXECUTABLE

    ) is not None


def docker_version():

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "--version"

            ],

            capture_output=True,

            text=True,

            timeout=DEFAULT_TIMEOUT

        )

        return process.stdout.strip()

    except Exception:

        return "Unknown"


def image_for(language):

    return LANGUAGE_IMAGES.get(

        language,

        DEFAULT_IMAGE

    )


def generate_container_name():

    return (

        "judge_"

        +

        uuid.uuid4().hex

    )


def create_result():

    return DockerResult()


# ==========================================================
# IMAGE CHECK
# ==========================================================

def image_exists(image):

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "image",

                "inspect",

                image

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

        return process.returncode == 0

    except Exception:

        return False


# ==========================================================
# PULL IMAGE
# ==========================================================

def pull_image(image):

    result = create_result()

    result.image = image

    start = time.perf_counter()

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "pull",

                image

            ],

            capture_output=True,

            text=True

        )

        result.execution_time = round(

            time.perf_counter() - start,

            4

        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.exit_code = process.returncode

        result.success = (

            process.returncode == 0

        )

        return result

    except Exception as e:

        result.stderr = str(e)

        return result


# ==========================================================
# ENSURE IMAGE
# ==========================================================

def ensure_image(language):

    image = image_for(language)

    if image_exists(image):

        return True

    result = pull_image(image)

    return result.success
# ==========================================================
# CONTAINER CONFIGURATION
# ==========================================================

def container_config(
    image,
    workspace,
    command,
    memory=DEFAULT_MEMORY,
    cpus=DEFAULT_CPUS
):
    """
    Build docker run command.
    """

    container_name = generate_container_name()

    docker_cmd = [

        DOCKER_EXECUTABLE,

        "run",

        "--rm",

        "--name",

        container_name,

        "--memory",

        memory,

        "--cpus",

        str(cpus),

        "--network",

        DEFAULT_NETWORK,

        "--pids-limit",

        str(DEFAULT_PIDS_LIMIT),

        "--read-only",

        "--tmpfs",

        DEFAULT_TMPFS,

        "-v",

        f"{workspace}:{DEFAULT_WORKDIR}:rw",

        "-w",

        DEFAULT_WORKDIR,

        image

    ]

    docker_cmd.extend(command)

    return container_name, docker_cmd


# ==========================================================
# CREATE CONTAINER
# ==========================================================

def create_container(
    image,
    workspace,
    command
):

    container_name, docker_cmd = container_config(

        image,

        workspace,

        command

    )

    return {

        "name": container_name,

        "command": docker_cmd

    }


# ==========================================================
# EXECUTE CONTAINER
# ==========================================================

def run_container(
    image,
    workspace,
    command,
    timeout=30
):

    result = create_result()

    result.image = image

    start = time.perf_counter()

    container = create_container(

        image,

        workspace,

        command

    )

    result.container_name = container["name"]

    result.command = " ".join(

        container["command"]

    )

    try:

        process = subprocess.run(

            container["command"],

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.execution_time = round(

            time.perf_counter() - start,

            4

        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.exit_code = process.returncode

        result.success = (

            process.returncode == 0

        )

        return result

    except subprocess.TimeoutExpired:

        result.execution_time = timeout

        result.timed_out = True

        result.stderr = "Container timed out."

        return result

    except Exception as e:

        result.stderr = str(e)

        return result


# ==========================================================
# WORKSPACE HELPERS
# ==========================================================

def workspace_exists(path):

    return os.path.isdir(path)


def create_workspace(path):

    os.makedirs(

        path,

        exist_ok=True

    )

    return path


def remove_workspace(path):

    if workspace_exists(path):

        shutil.rmtree(

            path,

            ignore_errors=True

        )


# ==========================================================
# COPY SOURCE FILE
# ==========================================================

def copy_source(
    source_file,
    workspace
):

    destination = os.path.join(

        workspace,

        os.path.basename(source_file)

    )

    shutil.copy2(

        source_file,

        destination

    )

    return destination


# ==========================================================
# PREPARE WORKSPACE
# ==========================================================

def prepare_workspace(
    source_file,
    workspace
):

    create_workspace(

        workspace

    )

    return copy_source(

        source_file,

        workspace

    )
# ==========================================================
# LANGUAGE COMMAND BUILDERS
# ==========================================================

def python_command(source_file):
    """
    Build Python execution command.
    """

    return [

        "python3",

        os.path.basename(source_file)

    ]


def c_command(executable):
    """
    Build C execution command.
    """

    return [

        f"./{os.path.basename(executable)}"

    ]


def cpp_command(executable):
    """
    Build C++ execution command.
    """

    return [

        f"./{os.path.basename(executable)}"

    ]


def java_command():
    """
    Build Java execution command.
    """

    return [

        "java",

        "Main"

    ]


def javascript_command(source_file):
    """
    Build JavaScript execution command.
    """

    return [

        "node",

        os.path.basename(source_file)

    ]


# ==========================================================
# COMMAND DISPATCHER
# ==========================================================

def execution_command(
    language,
    source_file,
    executable=None
):
    """
    Return execution command for language.
    """

    if language == "Python":

        return python_command(

            source_file

        )

    elif language == "C":

        return c_command(

            executable

        )

    elif language == "C++":

        return cpp_command(

            executable

        )

    elif language == "Java":

        return java_command()

    elif language == "JavaScript":

        return javascript_command(

            source_file

        )

    raise ValueError(

        f"Unsupported language: {language}"

    )


# ==========================================================
# RUN LANGUAGE
# ==========================================================

def execute_language(
    language,
    source_file,
    workspace,
    executable=None,
    timeout=5
):
    """
    Execute program inside Docker.
    """

    image = image_for(language)

    command = execution_command(

        language,

        source_file,

        executable

    )

    return run_container(

        image=image,

        workspace=workspace,

        command=command,

        timeout=timeout

    )


# ==========================================================
# PYTHON
# ==========================================================

def execute_python(
    source_file,
    workspace,
    timeout=5
):

    return execute_language(

        "Python",

        source_file,

        workspace,

        timeout=timeout

    )


# ==========================================================
# C
# ==========================================================

def execute_c(
    executable,
    workspace,
    timeout=5
):

    return execute_language(

        "C",

        executable,

        workspace,

        executable,

        timeout

    )


# ==========================================================
# C++
# ==========================================================

def execute_cpp(
    executable,
    workspace,
    timeout=5
):

    return execute_language(

        "C++",

        executable,

        workspace,

        executable,

        timeout

    )


# ==========================================================
# JAVA
# ==========================================================

def execute_java(
    source_file,
    workspace,
    timeout=5
):

    return execute_language(

        "Java",

        source_file,

        workspace,

        timeout=timeout

    )


# ==========================================================
# JAVASCRIPT
# ==========================================================

def execute_javascript(
    source_file,
    workspace,
    timeout=5
):

    return execute_language(

        "JavaScript",

        source_file,

        workspace,

        timeout=timeout

    )


# ==========================================================
# GENERIC EXECUTION
# ==========================================================

def execute(
    language,
    source_file,
    workspace,
    executable=None,
    timeout=5
):
    """
    Universal Docker execution API.
    """

    return execute_language(

        language,

        source_file,

        workspace,

        executable,

        timeout

    )
# ==========================================================
# CONTAINER WITH STDIN SUPPORT
# ==========================================================

def run_container_with_input(
    image,
    workspace,
    command,
    stdin_data="",
    timeout=5
):
    """
    Execute docker container with stdin.
    """

    result = create_result()

    result.image = image

    container = create_container(

        image,

        workspace,

        command

    )

    start = time.perf_counter()

    try:

        process = subprocess.run(

            container["command"],

            input=stdin_data,

            capture_output=True,

            text=True,

            timeout=timeout

        )

        result.success = (

            process.returncode == 0

        )

        result.stdout = process.stdout

        result.stderr = process.stderr

        result.exit_code = process.returncode

        result.execution_time = round(

            time.perf_counter() - start,

            4

        )

        result.container_name = container["name"]

        result.command = " ".join(

            container["command"]

        )

        return result

    except subprocess.TimeoutExpired:

        result.timed_out = True

        result.execution_time = timeout

        result.stderr = "Execution timed out."

        return result

    except Exception as e:

        result.stderr = str(e)

        return result


# ==========================================================
# EXECUTE PROGRAM WITH INPUT
# ==========================================================

def execute_with_input(
    language,
    source_file,
    workspace,
    stdin_data="",
    executable=None,
    timeout=5
):

    image = image_for(language)

    command = execution_command(

        language,

        source_file,

        executable

    )

    return run_container_with_input(

        image,

        workspace,

        command,

        stdin_data,

        timeout

    )


# ==========================================================
# OUTPUT HELPERS
# ==========================================================

def stdout(result):

    return result.stdout


def stderr(result):

    return result.stderr


def exit_code(result):

    return result.exit_code


def execution_time(result):

    return result.execution_time


# ==========================================================
# STATUS
# ==========================================================

def successful(result):

    return result.success


def failed(result):

    return not result.success


def timed_out(result):

    return result.timed_out


# ==========================================================
# CLEANUP CONTAINER
# ==========================================================

def remove_container(
    container_name
):

    if not container_name:

        return

    try:

        subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "rm",

                "-f",

                container_name

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

    except Exception:

        pass


# ==========================================================
# AUTO CLEANUP
# ==========================================================

def cleanup(result):

    remove_container(

        result.container_name

    )


# ==========================================================
# EXECUTE & CLEANUP
# ==========================================================

def execute_once(
    language,
    source_file,
    workspace,
    stdin_data="",
    executable=None,
    timeout=5
):

    result = execute_with_input(

        language,

        source_file,

        workspace,

        stdin_data,

        executable,

        timeout

    )

    cleanup(result)

    return result
# ==========================================================
# EXECUTION LOGGING
# ==========================================================

def log_result(result):
    """
    Log Docker execution result.
    """

    if result.success:

        logger.info(

            "Container executed successfully | "
            "Container=%s | "
            "Time=%.4fs",

            result.container_name,

            result.execution_time

        )

    else:

        logger.error(

            "Container execution failed | "
            "Container=%s | "
            "Error=%s",

            result.container_name,

            result.stderr

        )


# ==========================================================
# JSON REPORT
# ==========================================================

def result_dict(result):

    return {

        "success": result.success,

        "container_name": result.container_name,

        "image": result.image,

        "command": result.command,

        "stdout": result.stdout,

        "stderr": result.stderr,

        "exit_code": result.exit_code,

        "execution_time": result.execution_time,

        "timed_out": result.timed_out

    }


def export_result(
    result,
    filename
):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            result_dict(result),

            fp,

            indent=4

        )

    return filename


# ==========================================================
# CONTAINER INFORMATION
# ==========================================================

def inspect_container(
    container_name
):

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "inspect",

                container_name

            ],

            capture_output=True,

            text=True

        )

        if process.returncode != 0:

            return None

        return json.loads(

            process.stdout

        )

    except Exception:

        return None


# ==========================================================
# IMAGE INFORMATION
# ==========================================================

def inspect_image(
    image
):

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "image",

                "inspect",

                image

            ],

            capture_output=True,

            text=True

        )

        if process.returncode != 0:

            return None

        return json.loads(

            process.stdout

        )

    except Exception:

        return None


# ==========================================================
# REMOVE IMAGE
# ==========================================================

def remove_image(
    image
):

    try:

        subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "rmi",

                image

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

        return True

    except Exception:

        return False


# ==========================================================
# PRUNE DOCKER
# ==========================================================

def prune():

    try:

        subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "system",

                "prune",

                "-f"

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

        return True

    except Exception:

        return False


# ==========================================================
# LIST IMAGES
# ==========================================================

def list_images():

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "images",

                "--format",

                "{{.Repository}}:{{.Tag}}"

            ],

            capture_output=True,

            text=True

        )

        if process.returncode != 0:

            return []

        return [

            line

            for line in process.stdout.splitlines()

            if line.strip()

        ]

    except Exception:

        return []


# ==========================================================
# LIST CONTAINERS
# ==========================================================

def list_running_containers():

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "ps",

                "--format",

                "{{.Names}}"

            ],

            capture_output=True,

            text=True

        )

        if process.returncode != 0:

            return []

        return [

            line

            for line in process.stdout.splitlines()

            if line.strip()

        ]

    except Exception:

        return []


# ==========================================================
# QUICK REPORT
# ==========================================================

def report(result):

    return {

        "status":

            "Success"

            if result.success

            else

            "Failed",

        "container":

            result.container_name,

        "image":

            result.image,

        "execution_time":

            result.execution_time,

        "exit_code":

            result.exit_code,

        "timed_out":

            result.timed_out

    }
# ==========================================================
# DOCKER HEALTH CHECK
# ==========================================================

def docker_health():
    """
    Check Docker availability and version.
    """

    return {

        "docker_installed": docker_exists(),

        "docker_version": docker_version(),

        "default_image": DEFAULT_IMAGE,

        "status": (

            "Healthy"

            if docker_exists()

            else "Unavailable"

        )

    }


# ==========================================================
# CONTAINER STATS
# ==========================================================

def container_stats(container_name):
    """
    Return CPU and memory usage.
    """

    try:

        process = subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "stats",

                container_name,

                "--no-stream",

                "--format",

                "{{json .}}"

            ],

            capture_output=True,

            text=True,

            timeout=5

        )

        if process.returncode != 0:

            return None

        return json.loads(

            process.stdout

        )

    except Exception:

        return None


# ==========================================================
# MEMORY USAGE
# ==========================================================

def memory_usage(container_name):

    stats = container_stats(

        container_name

    )

    if not stats:

        return "Unknown"

    return stats.get(

        "MemUsage",

        "Unknown"

    )


# ==========================================================
# CPU USAGE
# ==========================================================

def cpu_usage(container_name):

    stats = container_stats(

        container_name

    )

    if not stats:

        return "Unknown"

    return stats.get(

        "CPUPerc",

        "Unknown"

    )


# ==========================================================
# SECURITY CHECK
# ==========================================================

def security_report():

    return {

        "network_disabled":

            DEFAULT_NETWORK == "none",

        "read_only":

            True,

        "tmpfs":

            DEFAULT_TMPFS,

        "memory_limit":

            DEFAULT_MEMORY,

        "cpu_limit":

            DEFAULT_CPUS,

        "pids_limit":

            DEFAULT_PIDS_LIMIT

    }


# ==========================================================
# BENCHMARK
# ==========================================================

def benchmark(
    language,
    source_file,
    workspace,
    runs=5
):

    timings = []

    for _ in range(runs):

        result = execute(

            language,

            source_file,

            workspace

        )

        timings.append(

            result.execution_time

        )

    if not timings:

        return {}

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
# EXECUTION MONITOR
# ==========================================================

class DockerMonitor:

    def __init__(self):

        self.executions = 0

        self.success = 0

        self.failure = 0

        self.total_time = 0.0

    def update(

        self,

        result

    ):

        self.executions += 1

        self.total_time += (

            result.execution_time

        )

        if result.success:

            self.success += 1

        else:

            self.failure += 1

    def report(self):

        average = 0

        if self.executions:

            average = round(

                self.total_time

                /

                self.executions,

                4

            )

        return {

            "executions":

                self.executions,

            "success":

                self.success,

            "failure":

                self.failure,

            "average_time":

                average

        }


# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

def system_information():

    return {

        "docker":

            docker_health(),

        "security":

            security_report(),

        "images":

            len(

                list_images()

            ),

        "containers":

            len(

                list_running_containers()

            )

    }


# ==========================================================
# VERIFY ENVIRONMENT
# ==========================================================

def verify_environment():

    return (

        docker_exists()

        and

        len(

            list_images()

        ) >= 0

    )


# ==========================================================
# DIAGNOSTICS
# ==========================================================

def diagnostics():

    return {

        "health":

            docker_health(),

        "system":

            system_information(),

        "environment_ready":

            verify_environment()

    }
# ==========================================================
# AUDIT LOGGING
# ==========================================================

from datetime import datetime
import hashlib


def audit_id(result):
    """
    Generate unique audit ID.
    """

    text = (

        f"{result.container_name}"

        f"{result.execution_time}"

        f"{datetime.utcnow()}"

    )

    return hashlib.sha256(

        text.encode("utf-8")

    ).hexdigest()


# ==========================================================
# AUDIT REPORT
# ==========================================================

def audit_report(result):

    return {

        "audit_id":

            audit_id(result),

        "container":

            result.container_name,

        "image":

            result.image,

        "command":

            result.command,

        "exit_code":

            result.exit_code,

        "execution_time":

            result.execution_time,

        "timed_out":

            result.timed_out,

        "success":

            result.success,

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

            audit_report(result),

            fp,

            indent=4

        )

    return filename


# ==========================================================
# EXECUTION HISTORY
# ==========================================================

class DockerHistory:

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

    def count(self):

        return len(

            self.history

        )

    def successful(self):

        return [

            r

            for r in self.history

            if r.success

        ]

    def failed(self):

        return [

            r

            for r in self.history

            if not r.success

        ]


# ==========================================================
# RETRY EXECUTION
# ==========================================================

def retry_execution(

    language,

    source_file,

    workspace,

    executable=None,

    timeout=5,

    retries=3

):

    last = None

    for _ in range(retries):

        last = execute(

            language,

            source_file,

            workspace,

            executable,

            timeout

        )

        if last.success:

            return last

    return last


# ==========================================================
# AUTO CLEANUP
# ==========================================================

def cleanup_all():

    """
    Remove stopped containers.
    """

    try:

        subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "container",

                "prune",

                "-f"

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

    except Exception:

        pass


# ==========================================================
# REMOVE DANGLING IMAGES
# ==========================================================

def remove_dangling_images():

    try:

        subprocess.run(

            [

                DOCKER_EXECUTABLE,

                "image",

                "prune",

                "-f"

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

    except Exception:

        pass


# ==========================================================
# COMPLETE CLEANUP
# ==========================================================

def full_cleanup():

    cleanup_all()

    remove_dangling_images()


# ==========================================================
# EXECUTE WITH LOGGING
# ==========================================================

def execute_logged(

    language,

    source_file,

    workspace,

    executable=None,

    timeout=5

):

    result = execute(

        language,

        source_file,

        workspace,

        executable,

        timeout

    )

    log_result(

        result

    )

    return result


# ==========================================================
# QUICK REPORT
# ==========================================================

def summary(result):

    return {

        "container":

            result.container_name,

        "status":

            "Success"

            if result.success

            else "Failed",

        "execution_time":

            result.execution_time,

        "exit_code":

            result.exit_code,

        "timed_out":

            result.timed_out

    }
# ==========================================================
# PARALLEL EXECUTION
# ==========================================================

from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics


def execute_parallel(
    jobs,
    max_workers=4
):
    """
    Execute multiple docker jobs.

    jobs = [
        {
            "language": "...",
            "source_file": "...",
            "workspace": "...",
            "executable": "...",
            "timeout": 5
        }
    ]
    """

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = [

            executor.submit(

                execute,

                job["language"],

                job["source_file"],

                job["workspace"],

                job.get("executable"),

                job.get("timeout", 5)

            )

            for job in jobs

        ]

        for future in as_completed(futures):

            try:

                results.append(

                    future.result()

                )

            except Exception as e:

                failed = create_result()

                failed.stderr = str(e)

                results.append(

                    failed

                )

    return results


# ==========================================================
# EXECUTION STATISTICS
# ==========================================================

def execution_statistics(
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

    times = [

        r.execution_time

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

                min(times),

                4

            ),

        "maximum":

            round(

                max(times),

                4

            ),

        "average":

            round(

                statistics.mean(times),

                4

            ),

        "median":

            round(

                statistics.median(times),

                4

            )

    }


# ==========================================================
# BATCH EXECUTION
# ==========================================================

def execute_batch(
    jobs
):

    return execute_parallel(

        jobs

    )


# ==========================================================
# BENCHMARK SUITE
# ==========================================================

class DockerBenchmark:

    def __init__(self):

        self.results = []

    def add(

        self,

        result

    ):

        self.results.append(

            result

        )

    def statistics(self):

        return execution_statistics(

            self.results

        )

    def average_time(self):

        if not self.results:

            return 0

        return round(

            sum(

                r.execution_time

                for r in self.results

            )

            /

            len(self.results),

            4

        )


# ==========================================================
# PERFORMANCE SCORE
# ==========================================================

def performance_score(
    result
):

    score = 100

    if not result.success:

        return 0

    if result.execution_time > 0.5:

        score -= 5

    if result.execution_time > 1:

        score -= 10

    if result.execution_time > 2:

        score -= 20

    return max(

        score,

        0

    )


# ==========================================================
# MONITOR
# ==========================================================

class DockerMonitor:

    def __init__(self):

        self.executions = []

    def update(

        self,

        result

    ):

        self.executions.append(

            result

        )

    def report(self):

        return execution_statistics(

            self.executions

        )


# ==========================================================
# HEALTH REPORT
# ==========================================================

def health_report():

    return {

        "docker":

            docker_health(),

        "environment":

            verify_environment(),

        "images":

            list_images(),

        "containers":

            list_running_containers()

    }


# ==========================================================
# QUICK DIAGNOSTIC
# ==========================================================

def diagnostic():

    return {

        "health":

            health_report(),

        "system":

            system_information()

    }


# ==========================================================
# METADATA
# ==========================================================

def metadata():

    return {

        "engine":

            "Docker Runner",

        "version":

            "1.0.0",

        "default_image":

            DEFAULT_IMAGE,

        "languages":

            list(

                LANGUAGE_IMAGES.keys()

            )

    }
# ==========================================================
# WORKSPACE MANAGER
# ==========================================================

import tempfile
import os
import shutil
from pathlib import Path


class WorkspaceManager:
    """
    Manage temporary Docker workspaces.
    """

    def __init__(self):

        self.workspaces = []

    def create(self):

        workspace = tempfile.mkdtemp(

            prefix="judge_workspace_"

        )

        self.workspaces.append(

            workspace

        )

        return workspace

    def cleanup(self, workspace):

        if os.path.exists(workspace):

            shutil.rmtree(

                workspace,

                ignore_errors=True

            )

    def cleanup_all(self):

        for workspace in self.workspaces:

            self.cleanup(

                workspace

            )

        self.workspaces.clear()


# ==========================================================
# IMAGE CACHE
# ==========================================================

class DockerImageCache:

    def __init__(self):

        self.cache = {}

    def has(self, image):

        return image in self.cache

    def add(self, image):

        self.cache[image] = datetime.utcnow()

    def remove(self, image):

        self.cache.pop(

            image,

            None

        )

    def clear(self):

        self.cache.clear()

    def list(self):

        return list(

            self.cache.keys()

        )


# ==========================================================
# CONTAINER LIFECYCLE
# ==========================================================

class ContainerManager:

    def __init__(self):

        self.active = {}

    def register(

        self,

        result

    ):

        if result.container_name:

            self.active[

                result.container_name

            ] = result

    def unregister(

        self,

        container_name

    ):

        self.active.pop(

            container_name,

            None

        )

    def cleanup(self):

        for name in list(

            self.active.keys()

        ):

            remove_container(

                name

            )

            self.unregister(

                name

            )

    def count(self):

        return len(

            self.active

        )


# ==========================================================
# RESOURCE MANAGER
# ==========================================================

class ResourceManager:

    def __init__(self):

        self.images = DockerImageCache()

        self.workspaces = WorkspaceManager()

        self.containers = ContainerManager()

    def cleanup(self):

        self.containers.cleanup()

        self.workspaces.cleanup_all()

        prune()

    def report(self):

        return {

            "images":

                len(

                    self.images.list()

                ),

            "containers":

                self.containers.count(),

            "workspaces":

                len(

                    self.workspaces.workspaces

                )

        }


# ==========================================================
# AUTO RECOVERY
# ==========================================================

def auto_recovery():

    try:

        cleanup_all()

    except Exception:

        pass

    try:

        prune()

    except Exception:

        pass

    return True


# ==========================================================
# SAFE EXECUTION
# ==========================================================

def safe_execute(

    language,

    source_file,

    workspace,

    executable=None,

    timeout=5

):

    try:

        return execute(

            language,

            source_file,

            workspace,

            executable,

            timeout

        )

    except Exception as e:

        result = create_result()

        result.stderr = str(e)

        return result


# ==========================================================
# EXECUTION PIPELINE
# ==========================================================

def execution_pipeline(

    language,

    source_file,

    workspace,

    executable=None,

    timeout=5

):

    result = safe_execute(

        language,

        source_file,

        workspace,

        executable,

        timeout

    )

    log_result(

        result

    )

    return result


# ==========================================================
# RUNTIME INFORMATION
# ==========================================================

def runtime_information():

    return {

        "docker_version":

            docker_version(),

        "default_image":

            DEFAULT_IMAGE,

        "workspace":

            DEFAULT_WORKDIR,

        "memory_limit":

            DEFAULT_MEMORY,

        "cpu_limit":

            DEFAULT_CPUS

    }


# ==========================================================
# SYSTEM SUMMARY
# ==========================================================

def summary():

    manager = ResourceManager()

    return {

        "docker":

            docker_health(),

        "runtime":

            runtime_information(),

        "resources":

            manager.report()

    }
# ==========================================================
# VERSION INFORMATION
# ==========================================================

DOCKER_RUNNER_NAME = "Lab Auto Grader Docker Runner"

DOCKER_RUNNER_VERSION = "1.0.0"

DOCKER_RUNNER_AUTHOR = "Devanshu Ranjan Upadhyay"


def version():
    """
    Docker runner version information.
    """

    return {

        "name": DOCKER_RUNNER_NAME,

        "version": DOCKER_RUNNER_VERSION,

        "author": DOCKER_RUNNER_AUTHOR,

        "docker_version": docker_version(),

        "supported_languages": list(

            LANGUAGE_IMAGES.keys()

        )

    }


# ==========================================================
# INITIALIZE
# ==========================================================

def initialize():
    """
    Initialize Docker Runner.
    """

    if not docker_exists():

        raise RuntimeError(

            "Docker is not installed."

        )

    logger.info(

        "Docker Runner initialized."

    )

    return docker_health()


# ==========================================================
# VERIFY INSTALLATION
# ==========================================================

def verify_installation():

    if not docker_exists():

        return False

    for language in LANGUAGE_IMAGES:

        image = image_for(language)

        if not image_exists(image):

            logger.warning(

                "Docker image missing: %s",

                image

            )

    return True


# ==========================================================
# MAIN API
# ==========================================================

def run(
    language,
    source_file,
    workspace,
    executable=None,
    stdin_data="",
    timeout=5
):
    """
    Main public execution API.
    """

    return execute_with_input(

        language=language,

        source_file=source_file,

        workspace=workspace,

        stdin_data=stdin_data,

        executable=executable,

        timeout=timeout

    )


# ==========================================================
# RUN ONCE
# ==========================================================

def run_once(
    language,
    source_file,
    workspace,
    executable=None,
    stdin_data="",
    timeout=5
):

    result = run(

        language,

        source_file,

        workspace,

        executable,

        stdin_data,

        timeout

    )

    cleanup(result)

    return result


# ==========================================================
# RUN MULTIPLE
# ==========================================================

def run_batch(jobs):

    return execute_batch(

        jobs

    )


# ==========================================================
# READY CHECK
# ==========================================================

def ready():

    return verify_environment()


# ==========================================================
# SHUTDOWN
# ==========================================================

def shutdown():

    full_cleanup()

    logger.info(

        "Docker Runner shutdown completed."

    )

    return True


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    # Models

    "DockerResult",

    # Main APIs

    "run",

    "run_once",

    "run_batch",

    "execute",

    "execute_with_input",

    "execute_parallel",

    "execution_pipeline",

    "safe_execute",

    # Workspace

    "WorkspaceManager",

    "ContainerManager",

    "ResourceManager",

    # Reports

    "diagnostic",

    "metadata",

    "summary",

    "health_report",

    "runtime_information",

    # Utilities

    "docker_health",

    "docker_version",

    "docker_exists",

    "verify_environment",

    "verify_installation",

    "initialize",

    "shutdown",

    "ready",

    "version"

]