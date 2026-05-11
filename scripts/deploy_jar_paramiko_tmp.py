import os
import time
import paramiko
import requests


HOST = "81.71.44.180"
PORT = 22
USER = "root"
PASSWORD = "Yiguo9527_"

LOCAL_JAR = r"D:/iCode/cursor/d_hos_pinguan_traegj_backend_20260205/target/pinguan-backend-0.0.1-SNAPSHOT.jar"
REMOTE_DIR = "/data"
REMOTE_JAR = f"{REMOTE_DIR}/pinguan-backend-0.0.1-SNAPSHOT.jar"
REMOTE_LOG = f"{REMOTE_DIR}/pinguan-backend.log"


def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    code = stdout.channel.recv_exit_status()
    return code, out, err


def main():
    if not os.path.exists(LOCAL_JAR):
        raise RuntimeError(f"Local jar not found: {LOCAL_JAR}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, PORT, USER, PASSWORD, timeout=20)
    print("Connected.")

    code, out, err = run(ssh, "java -version 2>&1 | head -n 1; uname -a; pwd")
    print(out.strip() or err.strip())

    # Ensure /data exists
    code, out, err = run(ssh, f"mkdir -p {REMOTE_DIR} && ls -ld {REMOTE_DIR}")
    print(out.strip() or err.strip())

    # Upload jar only
    sftp = ssh.open_sftp()
    sftp.put(LOCAL_JAR, REMOTE_JAR)
    sftp.close()
    print(f"Uploaded jar to {REMOTE_JAR}")

    # Kill existing process on 6031
    kill_cmd = (
        "pid=$(ss -lntp 2>/dev/null | awk '/:6031 /{print $NF}' | sed -n 's/.*pid=\\([0-9]\\+\\).*/\\1/p' | head -n 1); "
        "if [ -n \"$pid\" ]; then kill -9 $pid && echo KILLED:$pid; else echo NO_PID; fi"
    )
    code, out, err = run(ssh, kill_cmd)
    print((out + err).strip())

    # Start new process
    start_cmd = (
        f"nohup java -jar {REMOTE_JAR} --server.port=6031 > {REMOTE_LOG} 2>&1 & "
        "echo STARTED:$!"
    )
    code, out, err = run(ssh, start_cmd)
    print((out + err).strip())

    # Wait and check remote process
    time.sleep(6)
    code, out, err = run(ssh, "ss -lntp 2>/dev/null | awk '/:6031 /{print}'")
    print("PORT6031:", (out + err).strip() or "not listening yet")

    ssh.close()

    # Health check from local
    ok = False
    for _ in range(20):
        try:
            r = requests.get("http://81.71.44.180:6031/actuator/health", timeout=5)
            if r.status_code == 200:
                print("HEALTH:", r.text)
                ok = True
                break
        except Exception:
            pass
        time.sleep(2)

    if not ok:
        raise RuntimeError("Health check failed after restart")


if __name__ == "__main__":
    main()
