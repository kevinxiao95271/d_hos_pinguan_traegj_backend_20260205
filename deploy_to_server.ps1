# 部署到服务器脚本
$SERVER = "81.71.44.180"
$USER = "root"
$PASSWORD = "Yiguo9527_"
$REMOTE_DIR = "/data/pinguan"
$JAR_FILE = "target/pinguan-backend-0.0.1-SNAPSHOT.jar"
$APP_YML = "src/main/resources/application.yml"

Write-Host "开始部署到服务器 $SERVER ..." -ForegroundColor Green

# 使用 plink 和 pscp (需要安装 PuTTY)
# 或者使用 WinSCP 的命令行工具

# 方法1: 使用 WinSCP
if (Get-Command winscp.com -ErrorAction SilentlyContinue) {
    Write-Host "使用 WinSCP 部署..." -ForegroundColor Yellow
    
    $script = @"
open scp://${USER}:${PASSWORD}@${SERVER}
mkdir $REMOTE_DIR
cd $REMOTE_DIR
put $JAR_FILE pinguan-backend.jar
put $APP_YML application.yml
call pkill -f pinguan-backend || true
call cd $REMOTE_DIR && nohup java -jar pinguan-backend.jar > app.log 2>&1 &
exit
"@
    
    $script | winscp.com /script=-
}
else {
    Write-Host "请手动执行以下命令:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "# 1. 创建目录并上传文件" -ForegroundColor Cyan
    Write-Host "scp $JAR_FILE ${USER}@${SERVER}:${REMOTE_DIR}/pinguan-backend.jar"
    Write-Host "scp $APP_YML ${USER}@${SERVER}:${REMOTE_DIR}/application.yml"
    Write-Host ""
    Write-Host "# 2. 连接服务器并启动" -ForegroundColor Cyan
    Write-Host "ssh ${USER}@${SERVER}"
    Write-Host "cd $REMOTE_DIR"
    Write-Host "pkill -f pinguan-backend || true"
    Write-Host "nohup java -jar pinguan-backend.jar > app.log 2>&1 &"
    Write-Host "tail -f app.log"
}
