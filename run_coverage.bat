@echo off
REM 运行 pytest 并生成覆盖率报告
coverage run -m pytest
coverage report -m
coverage html
start htmlcov\index.html

echo 覆盖率测试完成！
echo HTML 报告已生成于 htmlcov\index.html
pause 