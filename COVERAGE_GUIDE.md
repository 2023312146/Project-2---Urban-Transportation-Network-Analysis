# Coverage Gutters 使用指南

## 什麼是 Coverage Gutters？

Coverage Gutters 是一個 VS Code 擴展，可以在編輯器中直接顯示代碼覆蓋率信息。它會在代碼行的左側顯示顏色條，表示該行的測試覆蓋情況。

## 安裝 Coverage Gutters

1. 在 VS Code 中打開擴展面板 (Ctrl+Shift+X)
2. 搜索 "Coverage Gutters"
3. 安裝 "Coverage Gutters" 擴展

## 使用方法

### 1. 運行覆蓋率測試

您可以使用以下任一方式運行覆蓋率測試：

#### 方式一：使用便捷腳本
```bash
python run_coverage.py
```

#### 方式二：直接使用 pytest
```bash
python -m pytest tests/ --cov=project --cov-report=xml --cov-report=html --cov-report=term-missing
```

### 2. 查看覆蓋率信息

運行測試後，Coverage Gutters 會自動檢測 `coverage.xml` 文件並在編輯器中顯示覆蓋率信息：

- **綠色條**：該行代碼被測試覆蓋
- **紅色條**：該行代碼未被測試覆蓋
- **黃色條**：該行代碼部分被測試覆蓋

### 3. Coverage Gutters 命令

在 VS Code 中，您可以使用以下命令：

- `Ctrl+Shift+P` 然後輸入 "Coverage Gutters: Watch" - 開始監視覆蓋率文件
- `Ctrl+Shift+P` 然後輸入 "Coverage Gutters: Remove Coverage" - 移除覆蓋率顯示
- `Ctrl+Shift+P` 然後輸入 "Coverage Gutters: Reload" - 重新加載覆蓋率數據

### 4. 覆蓋率報告

測試完成後會生成以下報告：

- `coverage.xml` - XML 格式的覆蓋率報告（Coverage Gutters 使用）
- `htmlcov/index.html` - HTML 格式的詳細覆蓋率報告
- 終端輸出 - 簡要的覆蓋率統計信息

## 當前項目覆蓋率

根據最新的測試結果，您的項目覆蓋率為 **94%**，這是一個很好的覆蓋率水平！

### 覆蓋率詳情：

- **高覆蓋率模組** (95%+):
  - `project/algorithms/dfs_all_paths_algorithm.py` - 100%
  - `project/algorithms/distance_calculation.py` - 100%
  - `project/algorithms/path_efficiency_analysis.py` - 100%
  - `project/gui/main_window_gui_builder.py` - 100%
  - `project/gui/path_analysis_result_display.py` - 100%
  - `project/gui/stop_and_route_dialogs_gui.py` - 100%

- **需要改進的模組**:
  - `project/core/csv_network_data_manager.py` - 83%
  - `project/analysis/network_path_analyzer.py` - 88%

## 故障排除

### 問題：Coverage Gutters 沒有顯示覆蓋率信息

**解決方案：**
1. 確保已經運行了覆蓋率測試並生成了 `coverage.xml` 文件
2. 在 VS Code 中按 `Ctrl+Shift+P`，輸入 "Coverage Gutters: Watch"
3. 檢查 VS Code 設置中的 Coverage Gutters 配置

### 問題：覆蓋率文件找不到

**解決方案：**
1. 確保已經安裝了 `pytest-cov`：`pip install pytest-cov`
2. 運行覆蓋率測試：`python run_coverage.py`
3. 檢查項目根目錄是否有 `coverage.xml` 文件

## 配置選項

在 `.vscode/settings.json` 中已經配置了 Coverage Gutters 的設置：

- 支持多種覆蓋率文件格式
- 在編輯器左側顯示覆蓋率條
- 啟用行覆蓋率和標尺覆蓋率顯示

## 最佳實踐

1. **定期運行覆蓋率測試**：在修改代碼後運行覆蓋率測試
2. **關注低覆蓋率區域**：優先為覆蓋率低的代碼編寫測試
3. **使用 HTML 報告**：查看 `htmlcov/index.html` 獲得更詳細的覆蓋率信息
4. **設置覆蓋率目標**：為項目設置最低覆蓋率要求（建議 80% 以上） 