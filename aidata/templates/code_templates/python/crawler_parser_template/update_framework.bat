@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

REM =========================
REM 使用者需設定（請依實際情況修改）
REM 1) 框架 git SSH 位置
set parserUrl=git@192.168.9.234:crawleragent/crawleragentxxxxx.git

REM 2) OpenSSH 私鑰路徑
set sshKeyPath=C:\Users\user\.ssh\SSHKEY_OPENSSH

REM 3) Git 連線命令
set GIT_SSH_COMMAND=ssh -i "C:\Users\user\.ssh\SSHKEY_OPENSSH"

REM 4) 需要自動更新的檔案
REM    範例:main.py, utils\helper.py, xxx.py
set "updateList=OtherInfoDefine.py, Match.py, OddPath.py"
REM =========================


REM --------------------------------
REM Step 1: 檢查 sshKeyPath 是否存在（沿用你提供的訊息）
if not exist "%sshKeyPath%" (
    echo can't git clone repo from gitlab.
    echo SSH private key not found.
    echo You need a private key compatible with OpenSSH, which can be generated using tools like PuTTYgen.
    echo If you already have a Pageant-compatible private key, you can use this tool for conversion.
    echo Note that Pageant private keys are not compatible with OpenSSH.
    pause
    exit /b
)

REM --------------------------------
REM Step 2: 檢查當前目錄是否有 project 資料夾
if not exist ".\project\" (
    echo [錯誤] 找不到 ".\project\" 資料夾。
    echo 請將此批次檔放在與 project 同一層目錄再執行。
    pause
    exit /b
)

REM --------------------------------
REM Step 3: 顯示 updateList，讓使用者確認
set "PRINT_LIST=%updateList%"
REM 將逗號替換成空白，便於 for 迴圈逐一處理
set "PRINT_LIST=%PRINT_LIST:,= %"

echo 即將檢查並套用更新的檔案如下:
for %%F in (%PRINT_LIST%) do (
    echo   %%F
)
echo.
pause

REM --------------------------------
REM Step 4: 建立 update_temp 資料夾（若已存在則先刪除）
if exist ".\update_temp\" (
    rmdir /s /q ".\update_temp\"
)
mkdir ".\update_temp\" || (
    echo [錯誤] 無法建立 update_temp 資料夾。
    pause
    exit /b
)

REM --------------------------------
REM Step 5: 在 update_temp 內 git clone %parserUrl%
pushd ".\update_temp\"
echo 進行 git clone：%parserUrl%
git clone %parserUrl% "framework"
if errorlevel 1 (
    echo [錯誤] git clone 失敗，請檢查 SSH 設定與 repo URL。
    popd
    rmdir /s /q ".\update_temp\"
    pause
    exit /b
)
popd

REM --------------------------------
REM 目標框架 project 路徑
set "FRAMEWORK_PROJECT=.\update_temp\framework\project"
if not exist "%FRAMEWORK_PROJECT%\" (
    echo [錯誤] 找不到 "%FRAMEWORK_PROJECT%\"，請確認框架內是否有 project 資料夾。
    rmdir /s /q ".\update_temp\"
    pause
    exit /b
)

REM 將 updateList 轉成空白分隔供 for 迴圈使用
set "LIST=%updateList%"
set "LIST=%LIST:,= %"

REM --------------------------------
REM Step 6: 檢查 updateList 所列的檔案在框架中是否存在
for %%F in (%LIST%) do (
    if not exist "%FRAMEWORK_PROJECT%\%%F" (
        echo [錯誤] updateList 的檔案在框架中不存在：%%F
        echo        路徑檢查：%FRAMEWORK_PROJECT%\%%F
        rmdir /s /q ".\update_temp\"
        pause
        exit /b
    )
)

REM --------------------------------
REM Step 7: 比對內容並列出結果
set "ORIG_PROJECT=.\project"
set "NEED_UPDATE_LIST="

echo.
echo ===== 比對結果 =====
for %%F in (%LIST%) do (
    if not exist "%ORIG_PROJECT%\%%F" (
        echo %%F  ^> 檔案在專案中不存在，需要新增
        set "NEED_UPDATE_LIST=!NEED_UPDATE_LIST! %%F"
    ) else (
        fc "%ORIG_PROJECT%\%%F" "%FRAMEWORK_PROJECT%\%%F" >nul
        if errorlevel 2 (
            echo %%F  ^> 比對失敗（檔案無法開啟或路徑錯誤）
            echo 請檢查路徑或權限後重試。
            rmdir /s /q ".\update_temp\"
            pause
            exit /b
        ) else if errorlevel 1 (
            echo %%F  ^> 需要更新
            set "NEED_UPDATE_LIST=!NEED_UPDATE_LIST! %%F"
        ) else (
            echo %%F  ^> 內容相同，不需更新
        )
    )
)
echo =====================

echo.
echo 是否要套用上述變更？
echo   1 = 確認更新
echo   2 = 取消更新
set /p "CHOICE=請輸入 1 或 2 並按下 Enter： "
if not "%CHOICE%"=="1" (
    echo 已取消更新，清理暫存資料夾...
    rmdir /s /q ".\update_temp\"
    echo 已完成清理。
	pause
    exit /b
)

REM --------------------------------
REM Step 8: 套用更新（只複製需要更新或新增的檔案）
set "FAIL=0"
echo 開始覆蓋（或新增）檔案至 %ORIG_PROJECT% ...
for %%F in (%LIST%) do (
    REM 重新判斷此檔案是否需更新／新增（避免前面列表遺漏）
    set "DO_COPY="
    if not exist "%ORIG_PROJECT%\%%F" (
        set "DO_COPY=1"
    ) else (
        fc "%ORIG_PROJECT%\%%F" "%FRAMEWORK_PROJECT%\%%F" >nul
        if errorlevel 1 set "DO_COPY=1"
    )

    if defined DO_COPY (
        REM 確保子資料夾存在
        for %%P in ("%ORIG_PROJECT%\%%F") do (
            if not exist "%%~dpP" mkdir "%%~dpP" >nul 2>&1
        )

        copy /y "%FRAMEWORK_PROJECT%\%%F" "%ORIG_PROJECT%\%%F" >nul
        if errorlevel 1 (
            echo [失敗] 複製失敗：%%F
            set "FAIL=1"
        ) else (
            echo [OK] 已更新：%%F
        )
    )
)

REM --------------------------------
REM Step 9: 刪除 update_temp 並提示完成

echo 清理暫存資料夾...
rmdir /s /q ".\update_temp\"

if "%FAIL%"=="0" (
    echo.
    echo ✅ 更新完成。
) else (
    echo.
    echo ⚠️ 部分檔案更新失敗，請查看上方訊息並手動處理。
)
pause
exit /b
