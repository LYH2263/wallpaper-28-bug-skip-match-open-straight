import os
import tempfile

# 在任何 app.* 模块导入前钉住独立测试库
_tmp = tempfile.mkdtemp(prefix="wp_pytest_")
os.environ.setdefault("DATA_DIR", _tmp)
